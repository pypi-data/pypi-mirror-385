# Using RabbitMQ JSON Sender as a Package

## Installation

### From Source with Poetry (Development)

```bash
cd /path/to/rabbitmq_json_sender
poetry install
```

### From Source with pip

```bash
pip install -e /path/to/rabbitmq_json_sender
```

### From PyPI (when published)

```bash
pip install rabbitmq-json-sender
```

## Usage Examples

### 1. As a CLI Tool

After installation, the `rabbitmq-sync` command is available:

```bash
# Show help
rabbitmq-sync --help

# Run with default .env
rabbitmq-sync

# Run with specific .env file
rabbitmq-sync --env-file /path/to/.env.company

# Run with preset
rabbitmq-sync --env-preset company

# Process specific range
rabbitmq-sync --offset 100 --limit 1000

# Validate configuration only
rabbitmq-sync --validate-only
```

### 2. As a Python Library

#### Basic Usage

```python
from rabbitmq_json_sender import DataSyncAPI, SyncConfig

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
    batch_size=1000,
    process_limit=10000
)

# Create API and sync
api = DataSyncAPI(config)
result = api.sync_data()

# Check results
if result.success:
    print(f"Processed: {result.total_processed}")
    print(f"Published: {result.total_published}")
    print(f"Success rate: {result.details.get('success_rate', 0):.1f}%")
else:
    print(f"Error: {result.error_message}")
```

#### Using Environment Files

```python
from rabbitmq_json_sender import create_config_from_env, DataSyncAPI

# Load from .env file
config = create_config_from_env(".env.company")

# Customize if needed
config.process_limit = 5000
config.enable_logging = False

# Sync data
api = DataSyncAPI(config)
result = api.sync_data(offset=100, limit=500)
```

#### Simple Function Call

```python
from rabbitmq_json_sender import sync_data_simple

result = sync_data_simple(
    clickhouse_config={
        "clickhouse_host": "localhost",
        "clickhouse_database": "mart"
    },
    rabbitmq_config={
        "rabbitmq_host": "localhost",
        "rabbitmq_exchange": "data_exchange"
    },
    batch_size=500,
    process_limit=1000
)
```

#### Integration in Your Application

```python
from rabbitmq_json_sender import DataSyncAPI, create_config_from_env

class MyDataPipeline:
    def __init__(self):
        self.config = create_config_from_env()
        self.config.enable_logging = False  # Use your own logging
        self.sync_api = DataSyncAPI(self.config)
    
    def sync_data(self, max_records=None):
        """Sync data from ClickHouse to RabbitMQ."""
        if max_records:
            self.config.process_limit = max_records
        
        result = self.sync_api.sync_data()
        
        return {
            'success': result.success,
            'processed': result.total_processed,
            'published': result.total_published,
            'failed': result.total_failed,
            'time': result.execution_time
        }
    
    def health_check(self):
        """Check if connections are working."""
        validation = self.sync_api.validate_configuration()
        return validation.success

# Usage
pipeline = MyDataPipeline()
if pipeline.health_check():
    stats = pipeline.sync_data(max_records=1000)
    print(f"Synced {stats['published']} records")
```

### 3. Advanced Usage

#### Configuration Validation

```python
from rabbitmq_json_sender import DataSyncAPI, SyncConfig

config = SyncConfig(
    clickhouse_host="localhost",
    rabbitmq_host="localhost"
)

api = DataSyncAPI(config)
validation = api.validate_configuration()

if validation.success:
    print("✅ Configuration valid")
    print(f"ClickHouse records: {validation.details.get('clickhouse_records')}")
else:
    print(f"❌ Validation failed: {validation.error_message}")
```

#### Batch Processing with Custom Logic

```python
from rabbitmq_json_sender import DataSyncAPI, create_config_from_env

config = create_config_from_env()
api = DataSyncAPI(config)

offset = 0
chunk_size = 1000
total_processed = 0

while True:
    result = api.sync_data(offset=offset, limit=chunk_size, validate_config=False)
    
    if not result.success or result.total_processed == 0:
        break
    
    total_processed += result.total_processed
    offset += result.total_processed
    
    print(f"Processed {total_processed} records so far...")

print(f"Total: {total_processed} records")
```

## API Reference

### SyncConfig

Configuration dataclass for data synchronization.

**Parameters:**
- `clickhouse_host` (str): ClickHouse server host
- `clickhouse_port` (int): ClickHouse server port (default: 9000)
- `clickhouse_user` (str): ClickHouse username
- `clickhouse_password` (str): ClickHouse password
- `clickhouse_database` (str): ClickHouse database name
- `clickhouse_table` (str): ClickHouse table name
- `rabbitmq_host` (str): RabbitMQ server host
- `rabbitmq_port` (int): RabbitMQ server port (default: 5672)
- `rabbitmq_user` (str): RabbitMQ username
- `rabbitmq_password` (str): RabbitMQ password
- `rabbitmq_queue` (str): RabbitMQ queue name
- `rabbitmq_exchange` (str): RabbitMQ exchange name
- `rabbitmq_exchange_type` (str): Exchange type (default: 'direct')
- `rabbitmq_routing_key` (str): Routing key
- `batch_size` (int): Batch size for processing (default: 1000)
- `max_retries` (int): Maximum retry attempts (default: 3)
- `process_limit` (int): Max records to process, -1 for unlimited (default: -1)
- `field_mapping_config_path` (str): Path to field mapping JSON
- `enable_logging` (bool): Enable logging (default: True)
- `log_level` (str): Logging level (default: 'INFO')

### SyncResult

Result dataclass returned by sync operations.

**Attributes:**
- `success` (bool): Whether operation succeeded
- `total_processed` (int): Total records processed
- `total_published` (int): Total records published to RabbitMQ
- `total_failed` (int): Total records that failed
- `batches_processed` (int): Number of batches processed
- `error_message` (str): Error message if failed
- `execution_time` (float): Execution time in seconds
- `details` (dict): Additional details (success_rate, etc.)

### DataSyncAPI

Main API class for data synchronization.

**Methods:**
- `sync_data(offset=0, limit=None, validate_config=True)`: Sync data from ClickHouse to RabbitMQ
- `validate_configuration()`: Validate configuration and connections

### Convenience Functions

- `sync_data_simple(clickhouse_config, rabbitmq_config, **kwargs)`: Simple sync function
- `create_config_from_env(env_file_path=None)`: Create config from .env file

## Building and Publishing

### Build the Package

```bash
poetry build
```

This creates distribution files in `dist/`:
- `rabbitmq_json_sender-0.1.2.tar.gz` (source)
- `rabbitmq_json_sender-0.1.2-py3-none-any.whl` (wheel)

### Publish to PyPI

```bash
# Configure PyPI credentials
poetry config pypi-token.pypi your-token

# Publish
poetry publish
```

### Install from Local Build

```bash
pip install dist/rabbitmq_json_sender-0.1.2-py3-none-any.whl
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black rabbitmq_json_sender/
```

### Type Checking

```bash
poetry run mypy rabbitmq_json_sender/
```

### Linting

```bash
poetry run flake8 rabbitmq_json_sender/
```
