"""
Functional API for RabbitMQ JSON Sender
Provides a clean interface for programmatic use from other applications.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
import os
from pathlib import Path

# Import ClickHouse specific exceptions
try:
    from clickhouse_connect.driver.exceptions import DatabaseError, OperationalError
except ImportError:
    DatabaseError = Exception
    OperationalError = Exception


@dataclass
class SyncConfig:
    """Configuration for data synchronization."""
    # ClickHouse configuration
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 9000
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "mart"
    clickhouse_table: str = "datamart.statgov_snap_legal_entities_v1_2_view_latest"
    
    # RabbitMQ configuration
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "legal_entities_queue"
    rabbitmq_exchange: str = "data_exchange"
    rabbitmq_exchange_type: str = "direct"
    rabbitmq_routing_key: str = "data.processed"
    
    # Processing configuration
    batch_size: int = 1000
    max_retries: int = 3
    process_limit: int = -1  # -1 means no limit
    
    # Field mapping configuration
    field_mapping_config_path: Optional[str] = "field_mapping.json"
    
    # Logging configuration
    enable_logging: bool = True
    log_level: str = "INFO"


@dataclass
class SyncResult:
    """Result of a data synchronization operation."""
    success: bool
    total_processed: int = 0
    total_published: int = 0
    total_failed: int = 0
    batches_processed: int = 0
    error_message: Optional[str] = None
    execution_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class DataSyncAPI:
    """Functional API for data synchronization operations."""
    
    def __init__(self, config: SyncConfig):
        """Initialize the API with configuration."""
        self.config = config
        self._setup_logging()
        self.logger = logging.getLogger(f"{__name__}.DataSyncAPI")
        
        # Initialize components
        self._clickhouse = None
        self._rabbitmq = None
        self._transform_batch = None
        self._field_mapping = None
        
    def _setup_logging(self):
        """Setup logging based on configuration."""
        if self.config.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # Reduce Pika logging verbosity
            logging.getLogger('pika').setLevel(logging.WARNING)
            logging.getLogger('pika.adapters').setLevel(logging.WARNING)
            logging.getLogger('pika.connection').setLevel(logging.WARNING)
            logging.getLogger('pika.channel').setLevel(logging.WARNING)
    
    def _initialize_components(self):
        """Initialize ClickHouse, RabbitMQ clients and transformation functions."""
        if self._clickhouse is not None:
            return  # Already initialized
            
        # Set up temporary environment variables for existing modules
        self._set_temp_env_vars()
        
        try:
            # Import and initialize field mapping
            if self.config.field_mapping_config_path and Path(self.config.field_mapping_config_path).exists():
                from field_mapping import FieldMappingConfig
                self._field_mapping = FieldMappingConfig(self.config.field_mapping_config_path)
                if self._field_mapping.get_source_table():
                    self.config.clickhouse_table = self._field_mapping.get_source_table()
            
            # Import and initialize clients
            from clickhouse_client import ClickHouseClient
            from rabbitmq_client import RabbitMQClient
            from transform import transform_batch
            
            self._clickhouse = ClickHouseClient()
            self._rabbitmq = RabbitMQClient()
            self._transform_batch = transform_batch
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize components: {str(e)}") from e
        finally:
            self._cleanup_temp_env_vars()
    
    def _set_temp_env_vars(self):
        """Set temporary environment variables for existing modules."""
        self._original_env = {}
        env_mapping = {
            'CLICKHOUSE_HOST': self.config.clickhouse_host,
            'CLICKHOUSE_PORT': str(self.config.clickhouse_port),
            'CLICKHOUSE_USER': self.config.clickhouse_user,
            'CLICKHOUSE_PASSWORD': self.config.clickhouse_password,
            'CLICKHOUSE_DATABASE': self.config.clickhouse_database,
            'CLICKHOUSE_TABLE': self.config.clickhouse_table,
            'RABBITMQ_HOST': self.config.rabbitmq_host,
            'RABBITMQ_PORT': str(self.config.rabbitmq_port),
            'RABBITMQ_USER': self.config.rabbitmq_user,
            'RABBITMQ_PASSWORD': self.config.rabbitmq_password,
            'RABBITMQ_QUEUE': self.config.rabbitmq_queue,
            'RABBITMQ_EXCHANGE': self.config.rabbitmq_exchange,
            'RABBITMQ_EXCHANGE_TYPE': self.config.rabbitmq_exchange_type,
            'RABBITMQ_ROUTING_KEY': self.config.rabbitmq_routing_key,
            'BATCH_SIZE': str(self.config.batch_size),
            'MAX_RETRIES': str(self.config.max_retries),
            'PROCESS_LIMIT': str(self.config.process_limit),
            'FIELD_MAPPING_CONFIG_PATH': self.config.field_mapping_config_path or ''
        }
        
        for key, value in env_mapping.items():
            self._original_env[key] = os.environ.get(key)
            os.environ[key] = value
    
    def _cleanup_temp_env_vars(self):
        """Restore original environment variables."""
        for key, original_value in self._original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
    
    @contextmanager
    def _managed_resources(self):
        """Context manager for resource cleanup."""
        try:
            self._initialize_components()
            yield
        finally:
            self._cleanup_resources()
    
    def _cleanup_resources(self):
        """Clean up resources."""
        if self._rabbitmq:
            try:
                self._rabbitmq.close()
            except Exception as e:
                if self.config.enable_logging:
                    self.logger.error(f"Error during RabbitMQ cleanup: {str(e)}")
    
    def sync_data(self, 
                  offset: int = 0, 
                  limit: Optional[int] = None,
                  validate_config: bool = True) -> SyncResult:
        """
        Synchronize data from ClickHouse to RabbitMQ.
        
        Args:
            offset: Starting offset for data retrieval
            limit: Maximum number of records to process (overrides config.process_limit)
            validate_config: Whether to validate configuration before processing
            
        Returns:
            SyncResult with operation details
        """
        start_time = time.time()
        result = SyncResult(success=False)
        
        try:
            if validate_config:
                validation_result = self.validate_configuration()
                if not validation_result.success:
                    result.error_message = f"Configuration validation failed: {validation_result.error_message}"
                    return result
            
            with self._managed_resources():
                result = self._perform_sync(offset, limit or self.config.process_limit)
                
        except Exception as e:
            result.error_message = str(e)
            if self.config.enable_logging:
                self.logger.error(f"Sync operation failed: {str(e)}", exc_info=True)
        
        result.execution_time = time.time() - start_time
        return result
    
    def _perform_sync(self, offset: int, limit: int) -> SyncResult:
        """Perform the actual synchronization."""
        result = SyncResult(success=True)
        
        try:
            # Get total available records
            total_available = self._clickhouse.get_total_companies_count()
            
            # Calculate actual limit
            if limit > 0:
                total_to_process = min(limit, total_available - offset)
            else:
                total_to_process = total_available - offset
            
            if total_to_process <= 0:
                result.details['message'] = "No records to process"
                return result
            
            current_offset = offset
            batch_number = 0
            
            while result.total_processed < total_to_process:
                batch_number += 1
                
                # Calculate batch size
                remaining = total_to_process - result.total_processed
                current_batch_size = min(self.config.batch_size, remaining)
                
                # Process batch
                batch_result = self._process_batch(current_offset, current_batch_size, batch_number)
                
                # Update results
                result.total_processed += batch_result['fetched']
                result.total_published += batch_result['published']
                result.total_failed += batch_result['failed']
                result.batches_processed += 1
                
                # Update offset
                current_offset += batch_result['fetched']
                
                # Check if we should continue
                if batch_result['fetched'] == 0:
                    break
                
                # Small delay to prevent overwhelming systems
                time.sleep(0.1)
            
            result.details.update({
                'total_available': total_available,
                'total_to_process': total_to_process,
                'success_rate': (result.total_published / max(result.total_processed, 1)) * 100
            })
            
        except (DatabaseError, OperationalError) as e:
            result.success = False
            result.error_message = f"Database error: {str(e)}"
        except Exception as e:
            result.success = False
            result.error_message = f"Unexpected error: {str(e)}"
        
        return result
    
    def _process_batch(self, offset: int, limit: int, batch_number: int) -> Dict[str, int]:
        """Process a single batch of records."""
        batch_result = {'fetched': 0, 'published': 0, 'failed': 0}
        
        try:
            # Fetch data
            companies = self._clickhouse.fetch_companies_batch(offset=offset, limit=limit)
            batch_result['fetched'] = len(companies)
            
            if not companies:
                return batch_result
            
            # Transform data
            transformed = self._transform_batch(companies)
            
            # Publish to RabbitMQ
            if transformed:
                published_count = self._rabbitmq.publish_batch(transformed)
                batch_result['published'] = published_count
                batch_result['failed'] = len(transformed) - published_count
            
            if self.config.enable_logging:
                self.logger.info(f"Batch {batch_number}: fetched={batch_result['fetched']}, "
                               f"published={batch_result['published']}, failed={batch_result['failed']}")
                
        except Exception as e:
            batch_result['failed'] = batch_result['fetched']
            if self.config.enable_logging:
                self.logger.error(f"Error processing batch {batch_number}: {str(e)}")
        
        return batch_result
    
    def validate_configuration(self) -> SyncResult:
        """Validate the current configuration."""
        result = SyncResult(success=True)
        errors = []
        
        try:
            with self._managed_resources():
                # Test ClickHouse connection
                try:
                    count = self._clickhouse.get_total_companies_count()
                    result.details['clickhouse_records'] = count
                except Exception as e:
                    errors.append(f"ClickHouse connection failed: {str(e)}")
                
                # Test RabbitMQ connection
                try:
                    if not self._rabbitmq.is_connected():
                        errors.append("RabbitMQ connection failed")
                    else:
                        result.details['rabbitmq_connected'] = True
                except Exception as e:
                    errors.append(f"RabbitMQ connection error: {str(e)}")
                
        except Exception as e:
            errors.append(f"Configuration validation error: {str(e)}")
        
        if errors:
            result.success = False
            result.error_message = "; ".join(errors)
        
        return result


# Convenience functions for easy use

def sync_data_simple(clickhouse_config: Dict[str, Any], 
                    rabbitmq_config: Dict[str, Any],
                    **kwargs) -> SyncResult:
    """
    Simple function to sync data with minimal configuration.
    
    Args:
        clickhouse_config: ClickHouse connection parameters
        rabbitmq_config: RabbitMQ connection parameters
        **kwargs: Additional configuration options
        
    Returns:
        SyncResult with operation details
    """
    config = SyncConfig(**clickhouse_config, **rabbitmq_config, **kwargs)
    api = DataSyncAPI(config)
    return api.sync_data()


def create_config_from_env(env_file_path: Optional[str] = None) -> SyncConfig:
    """
    Create configuration from environment file.
    
    Args:
        env_file_path: Path to .env file (optional)
        
    Returns:
        SyncConfig instance
    """
    if env_file_path:
        from dotenv import load_dotenv
        load_dotenv(env_file_path, override=True)
    
    return SyncConfig(
        clickhouse_host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        clickhouse_port=int(os.getenv('CLICKHOUSE_PORT', 9000)),
        clickhouse_user=os.getenv('CLICKHOUSE_USER', 'default'),
        clickhouse_password=os.getenv('CLICKHOUSE_PASSWORD', ''),
        clickhouse_database=os.getenv('CLICKHOUSE_DATABASE', 'mart'),
        clickhouse_table=os.getenv('CLICKHOUSE_TABLE', 'datamart.statgov_snap_legal_entities_v1_2_view_latest'),
        rabbitmq_host=os.getenv('RABBITMQ_HOST', 'localhost'),
        rabbitmq_port=int(os.getenv('RABBITMQ_PORT', 5672)),
        rabbitmq_user=os.getenv('RABBITMQ_USER', 'guest'),
        rabbitmq_password=os.getenv('RABBITMQ_PASSWORD', 'guest'),
        rabbitmq_queue=os.getenv('RABBITMQ_QUEUE', 'legal_entities_queue'),
        rabbitmq_exchange=os.getenv('RABBITMQ_EXCHANGE', 'data_exchange'),
        rabbitmq_exchange_type=os.getenv('RABBITMQ_EXCHANGE_TYPE', 'direct'),
        rabbitmq_routing_key=os.getenv('RABBITMQ_ROUTING_KEY', 'data.processed'),
        batch_size=int(os.getenv('BATCH_SIZE', 1000)),
        max_retries=int(os.getenv('MAX_RETRIES', 3)),
        process_limit=int(os.getenv('PROCESS_LIMIT', -1)),
        field_mapping_config_path=os.getenv('FIELD_MAPPING_CONFIG_PATH', 'field_mapping.json')
    )
