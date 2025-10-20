import logging
import time
import argparse
from typing import List, Dict, Any, Optional
from . import config
from .data_sync_api import DataSyncAPI, create_config_from_env

# Import ClickHouse specific exceptions
try:
    from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError
except ImportError:
    # Fallback if clickhouse_connect is not available
    DatabaseError = Exception
    OperationalError = Exception

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Reduce Pika logging verbosity
logging.getLogger('pika').setLevel(logging.WARNING)
logging.getLogger('pika.adapters').setLevel(logging.WARNING)
logging.getLogger('pika.connection').setLevel(logging.WARNING)
logging.getLogger('pika.channel').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class DataSyncApp:
    def __init__(self):
        # Import modules after config is loaded
        from .clickhouse_client import ClickHouseClient
        from .rabbitmq_client import RabbitMQClient
        from .transform import transform_batch
        
        self.clickhouse = ClickHouseClient()
        self.rabbitmq = RabbitMQClient()
        self.transform_batch = transform_batch
        self.processed_count = 0
        self.total_companies = 0

    def run(self):
        """Run the data synchronization process."""
        try:
            logger.info("Starting data synchronization from ClickHouse to RabbitMQ")
            
            # Get total number of companies
            try:
                total_available = self.clickhouse.get_total_companies_count()
            except DatabaseError as e:
                if "UNKNOWN_IDENTIFIER" in str(e):
                    logger.error("ClickHouse schema error: One or more fields in the configuration don't exist in the database table")
                    logger.error("Please check your field mapping configuration and ensure all fields exist in the source table")
                    logger.error(f"ClickHouse error details: {str(e)}")
                    return
                else:
                    logger.error(f"ClickHouse database error: {str(e)}")
                    return
            except OperationalError as e:
                logger.error(f"ClickHouse connection error: {str(e)}")
                logger.error("Please check your ClickHouse connection settings")
                return
            except Exception as e:
                logger.error(f"Unexpected error while connecting to ClickHouse: {str(e)}")
                return
            
            # Apply limit if specified
            if config.PROCESS_LIMIT > 0:
                self.total_companies = min(config.PROCESS_LIMIT, total_available)
                logger.info(f"Processing limited to {self.total_companies} companies (as per PROCESS_LIMIT in .env)")
            else:
                self.total_companies = total_available
                logger.info(f"Processing all {self.total_companies} companies")
            
            offset = 0
            batch_number = 0
            
            while True:
                batch_number += 1
                logger.info(f"Processing batch {batch_number} (offset: {offset})")
                
                # Calculate how many records we still need to reach the limit
                remaining = self.total_companies - self.processed_count
                if remaining <= 0:
                    logger.info("Reached the processing limit")
                    break
                    
                # Adjust batch size if we're close to the limit
                current_batch_size = min(config.BATCH_SIZE, remaining)
                
                # Fetch a batch of companies from ClickHouse
                try:
                    companies = self.clickhouse.fetch_companies_batch(offset=offset, limit=current_batch_size)
                except DatabaseError as e:
                    if "UNKNOWN_IDENTIFIER" in str(e):
                        logger.error("ClickHouse schema error: One or more fields in the configuration don't exist in the database table")
                        logger.error("Please check your field mapping configuration and ensure all fields exist in the source table")
                        logger.error(f"ClickHouse error details: {str(e)}")
                        break
                    else:
                        logger.error(f"ClickHouse database error in batch {batch_number}: {str(e)}")
                        break
                except OperationalError as e:
                    logger.error(f"ClickHouse connection error in batch {batch_number}: {str(e)}")
                    logger.error("Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error fetching batch {batch_number}: {str(e)}")
                    break
                
                if not companies:
                    logger.info("No more companies to process")
                    break
                
                # Transform the data to match the target schema
                try:
                    transformed = self.transform_batch(companies)
                except Exception as e:
                    logger.error(f"Error transforming batch {batch_number}: {str(e)}")
                    logger.error("Skipping this batch and continuing...")
                    offset += len(companies)
                    continue
                
                # Publish to RabbitMQ
                if transformed:
                    try:
                        success_count = self.rabbitmq.publish_batch(transformed)
                        self.processed_count += success_count
                        logger.info(f"Published {success_count} companies in batch {batch_number}")
                    except Exception as e:
                        logger.error(f"Error publishing batch {batch_number} to RabbitMQ: {str(e)}")
                        logger.error("Skipping this batch and continuing...")
                        offset += len(companies)
                        continue
                
                # Update offset for next batch
                offset += len(companies)
                
                # Log progress
                progress = (self.processed_count / max(self.total_companies, 1)) * 100
                logger.info(f"Progress: {progress:.2f}% ({self.processed_count}/{self.total_companies})")
                
                # Check if we've reached the limit
                if self.processed_count >= self.total_companies:
                    logger.info(f"Reached the limit of {self.total_companies} companies to process")
                    break
                
                # Small delay to prevent overwhelming the systems
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main process: {str(e)}", exc_info=True)
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        try:
            self.rabbitmq.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        
        logger.info(f"Processing complete. Total companies processed: {self.processed_count}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='RabbitMQ JSON Sender - Sync data from ClickHouse to RabbitMQ')
    parser.add_argument(
        '--env-file', 
        type=str, 
        help='Path to .env file to use (default: .env)',
        default=None
    )
    parser.add_argument(
        '--env-preset',
        type=str,
        choices=['default', 'company', 'products'],
        help='Use predefined .env file preset (default, company, products)',
        default=None
    )
    return parser.parse_args()

def main():
    """Main entry point for CLI."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Determine which .env file to use
    env_file_path = None
    if args.env_preset:
        preset_files = {
            'default': '.env',
            'company': '.env.company', 
            'products': '.env.products'
        }
        env_file_path = preset_files[args.env_preset]
        logger.info(f"Using .env preset: {args.env_preset} ({env_file_path})")
    elif args.env_file:
        env_file_path = args.env_file
        logger.info(f"Using custom .env file: {env_file_path}")
    else:
        logger.info("Using default .env file")
    
    # Load configuration with specified .env file
    if env_file_path:
        config.load_config(env_file_path)
        logger.info(f"Configuration loaded from: {env_file_path}")
    
    # Create and run the application
    app = DataSyncApp()
    app.run()


if __name__ == "__main__":
    main()
