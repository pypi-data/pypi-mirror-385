"""
Usage examples for the Data Sync API
Demonstrates different ways to use the functional interface.
"""

from data_sync_api import DataSyncAPI, SyncConfig, SyncResult, sync_data_simple, create_config_from_env


def example_1_basic_usage():
    """Example 1: Basic usage with manual configuration"""
    print("=== Example 1: Basic Usage ===")
    
    # Create configuration
    config = SyncConfig(
        clickhouse_host="localhost",
        clickhouse_port=9000,
        clickhouse_user="default",
        clickhouse_password="",
        clickhouse_database="mart",
        rabbitmq_host="localhost",
        rabbitmq_port=5672,
        rabbitmq_user="guest",
        rabbitmq_password="guest",
        batch_size=100,
        process_limit=1000,  # Process only 1000 records
        enable_logging=True
    )
    
    # Create API instance and sync data
    api = DataSyncAPI(config)
    result = api.sync_data()
    
    # Check results
    if result.success:
        print(f"✅ Sync completed successfully!")
        print(f"   Processed: {result.total_processed}")
        print(f"   Published: {result.total_published}")
        print(f"   Failed: {result.total_failed}")
        print(f"   Execution time: {result.execution_time:.2f}s")
        print(f"   Success rate: {result.details.get('success_rate', 0):.1f}%")
    else:
        print(f"❌ Sync failed: {result.error_message}")


def example_2_from_env_file():
    """Example 2: Using configuration from .env file"""
    print("\n=== Example 2: Configuration from .env file ===")
    
    # Load configuration from .env file
    config = create_config_from_env(".env.company.dev")
    
    # Customize some settings
    config.process_limit = 500
    config.batch_size = 50
    config.enable_logging = False  # Disable logging for library use
    
    # Sync data
    api = DataSyncAPI(config)
    result = api.sync_data(offset=100, limit=200)  # Process 200 records starting from offset 100
    
    print(f"Result: {'Success' if result.success else 'Failed'}")
    if result.success:
        print(f"Records processed: {result.total_processed}")


def example_3_simple_function():
    """Example 3: Using the simple convenience function"""
    print("\n=== Example 3: Simple Function Usage ===")
    
    # Define configurations as dictionaries
    clickhouse_config = {
        "clickhouse_host": "localhost",
        "clickhouse_port": 9000,
        "clickhouse_user": "default",
        "clickhouse_password": "",
        "clickhouse_database": "mart"
    }
    
    rabbitmq_config = {
        "rabbitmq_host": "localhost",
        "rabbitmq_port": 5672,
        "rabbitmq_user": "guest",
        "rabbitmq_password": "guest",
        "rabbitmq_exchange": "data_exchange"
    }
    
    # Use simple function
    result = sync_data_simple(
        clickhouse_config=clickhouse_config,
        rabbitmq_config=rabbitmq_config,
        batch_size=200,
        process_limit=100,
        enable_logging=False
    )
    
    print(f"Simple sync result: {'Success' if result.success else 'Failed'}")


def example_4_validation_and_error_handling():
    """Example 4: Configuration validation and error handling"""
    print("\n=== Example 4: Validation and Error Handling ===")
    
    # Create configuration with potentially invalid settings
    config = SyncConfig(
        clickhouse_host="invalid-host",  # Invalid host
        rabbitmq_host="localhost",
        enable_logging=True
    )
    
    api = DataSyncAPI(config)
    
    # Validate configuration first
    validation_result = api.validate_configuration()
    if not validation_result.success:
        print(f"❌ Configuration validation failed: {validation_result.error_message}")
        return
    
    # If validation passes, proceed with sync
    result = api.sync_data(validate_config=False)  # Skip validation since we already did it
    
    if result.success:
        print(f"✅ Sync completed: {result.total_processed} records")
    else:
        print(f"❌ Sync failed: {result.error_message}")


def example_5_batch_processing():
    """Example 5: Processing data in chunks with custom logic"""
    print("\n=== Example 5: Batch Processing ===")
    
    config = create_config_from_env()
    config.batch_size = 100
    config.enable_logging = True
    
    api = DataSyncAPI(config)
    
    # Process data in chunks
    total_processed = 0
    offset = 0
    chunk_size = 500
    
    while True:
        result = api.sync_data(offset=offset, limit=chunk_size, validate_config=False)
        
        if not result.success:
            print(f"❌ Chunk failed at offset {offset}: {result.error_message}")
            break
            
        if result.total_processed == 0:
            print("✅ No more data to process")
            break
            
        total_processed += result.total_processed
        offset += result.total_processed
        
        print(f"📊 Processed chunk: {result.total_processed} records (total: {total_processed})")
        
        # Stop after processing 2000 records for demo
        if total_processed >= 2000:
            break
    
    print(f"🏁 Total processed: {total_processed} records")


def example_6_integration_in_application():
    """Example 6: Integration in a larger application"""
    print("\n=== Example 6: Application Integration ===")
    
    class DataProcessor:
        def __init__(self, env_file: str = None):
            self.config = create_config_from_env(env_file)
            self.config.enable_logging = False  # Use application's logging
            self.api = DataSyncAPI(self.config)
        
        def sync_companies(self, max_records: int = None) -> dict:
            """Sync company data and return summary."""
            if max_records:
                self.config.process_limit = max_records
            
            result = self.api.sync_data()
            
            return {
                'success': result.success,
                'processed': result.total_processed,
                'published': result.total_published,
                'failed': result.total_failed,
                'execution_time': result.execution_time,
                'error': result.error_message
            }
        
        def health_check(self) -> bool:
            """Check if connections are working."""
            validation = self.api.validate_configuration()
            return validation.success
    
    # Use in application
    processor = DataProcessor(".env.company.prod")
    
    # Health check
    if processor.health_check():
        print("✅ System is healthy")
        
        # Sync data
        summary = processor.sync_companies(max_records=100)
        print(f"Sync summary: {summary}")
    else:
        print("❌ System health check failed")


def example_7_error_recovery():
    """Example 7: Error recovery and retry logic"""
    print("\n=== Example 7: Error Recovery ===")
    
    config = create_config_from_env()
    config.max_retries = 5
    config.enable_logging = True
    
    api = DataSyncAPI(config)
    
    max_attempts = 3
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"Attempt {attempt}/{max_attempts}")
        
        result = api.sync_data()
        
        if result.success:
            print(f"✅ Success on attempt {attempt}")
            print(f"   Processed: {result.total_processed}")
            break
        else:
            print(f"❌ Attempt {attempt} failed: {result.error_message}")
            
            if attempt < max_attempts:
                print("   Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("   Max attempts reached, giving up")
        
        attempt += 1


if __name__ == "__main__":
    """Run all examples"""
    print("🚀 Data Sync API Usage Examples\n")
    
    try:
        example_1_basic_usage()
        example_2_from_env_file()
        example_3_simple_function()
        example_4_validation_and_error_handling()
        example_5_batch_processing()
        example_6_integration_in_application()
        example_7_error_recovery()
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {str(e)}")
        print("Make sure ClickHouse and RabbitMQ are running and configured correctly.")
    
    print("\n✅ Examples completed!")
