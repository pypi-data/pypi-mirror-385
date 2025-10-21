# Universal ClickHouse to RabbitMQ Data Sync

This application provides a **universal data synchronization system** that can sync data from any ClickHouse table to RabbitMQ queues with configurable field mappings and transformations. No code changes required - just configure through JSON files!

## 🚀 Key Features

- **Universal Configuration**: Support any ClickHouse table through JSON configuration
- **Dynamic Field Mapping**: Map source fields to target JSON fields with validation
- **Data Transformation**: Built-in transformations for dates, strings, and data types
- **Comprehensive Validation**: JSON schema validation and database compatibility checks
- **Error Handling**: Robust error handling with detailed reporting
- **Backward Compatibility**: Works with existing configurations
- **Functional API**: Can be used as a library in other applications
- **Flexible Execution**: Command-line tool or programmatic function calls

## Prerequisites

- Python 3.7+
- ClickHouse server
- RabbitMQ server

## Installation

### Option 1: Install as a Package (Recommended)

Using Poetry (recommended for development):

```bash
# Clone the repository
git clone <repository-url>
cd rabbitmq-json-sender

# Install with Poetry
poetry install

# Or install in existing virtual environment
source .venv/bin/activate
poetry install
```

Using pip:

```bash
# Install from source
pip install .

# Or install in development mode
pip install -e .
```

After installation, the package can be used in two ways:

**As a CLI tool:**
```bash
rabbitmq-sync --help
rabbitmq-sync --env-file .env.company
```

**As a Python library:**
```python
from rabbitmq_json_sender import DataSyncAPI, SyncConfig

config = SyncConfig(
    clickhouse_host="localhost",
    rabbitmq_host="localhost"
)
api = DataSyncAPI(config)
result = api.sync_data()
```

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rabbitmq-json-sender
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your configuration:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your ClickHouse and RabbitMQ connection details.

## Configuration

### Environment Configuration

Edit the `.env` file with your connection details:

```env
# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DATABASE=mart

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=legal_entities_queue
RABBITMQ_EXCHANGE=data_exchange
RABBITMQ_EXCHANGE_TYPE=direct
RABBITMQ_ROUTING_KEY=data.processed

# Application Configuration
BATCH_SIZE=1000
MAX_RETRIES=3
PROCESS_LIMIT=-1

# Field Mapping Configuration
FIELD_MAPPING_CONFIG_PATH=field_mapping.json
```

### Field Mapping Configuration

The heart of the universal system is the `field_mapping.json` file that defines:
- Source table and fields
- Target JSON field mappings
- Data validation rules
- Transformation settings

#### Basic Structure

```json
{
  "metadata": {
    "version": "1.0",
    "description": "Field mapping for legal entities"
  },
  "source": {
    "table": "datamart.legal_entities_view",
    "primary_key": "id",
    "batch_column": "id",
    "order_by": "id"
  },
  "field_mappings": {
    "source_field": {
      "target": "TARGET_FIELD",
      "type": "string",
      "required": true,
      "validation": {
        "min_length": 1
      }
    }
  },
  "transformations": {
    "date_format": "iso",
    "remove_null_values": true,
    "encoding": "utf-8"
  },
  "validation_rules": {
    "required_fields": ["TARGET_FIELD"],
    "skip_record_if_missing": ["source_field"]
  }
}
```

#### Field Mapping Options

Each field mapping supports:

- **target**: Target field name in output JSON (null to exclude)
- **type**: Data type (`string`, `integer`, `date`, `float`, `boolean`)
- **required**: Whether field is required
- **alias**: SQL alias for the field
- **validation**: Validation rules
  - `type`: `digits_only`, `email`, `url`, `regex`
  - `min_length`, `max_length`: Length constraints
  - `pattern`: Regex pattern
- **transformation**: Data transformation (`iso_format`, `uppercase`, `lowercase`)

#### Example Field Mappings

```json
{
  "bin": {
    "target": "UF_BIN",
    "type": "string",
    "required": true,
    "validation": {
      "type": "digits_only",
      "min_length": 12,
      "max_length": 12
    }
  },
  "company_name": {
    "target": "UF_COMPANY_NAME",
    "type": "string",
    "required": true
  },
  "register_date": {
    "target": "UF_REGISTER_DATE",
    "type": "date",
    "transformation": "iso_format"
  },
  "internal_id": {
    "target": null,
    "type": "integer",
    "description": "Internal ID, not included in output"
  }
}
```

## Usage

### Command-Line Usage

#### Basic Execution

1. **Validate Configuration** (recommended):
   ```bash
   python main.py --validate-only
   ```

2. **Start Data Synchronization**:
   ```bash
   python main.py
   ```

3. **Using Different Environment Files**:
   ```bash
   # Use preset configurations
   python main.py --env-preset company
   python main.py --env-preset products
   
   # Use custom .env file
   python main.py --env-file /path/to/custom.env
   ```

4. **Process Specific Range**:
   ```bash
   # Process 1000 records starting from offset 500
   python main.py --offset 500 --limit 1000
   ```

5. **Use Legacy Mode**:
   ```bash
   # Use the legacy DataSyncApp class
   python main.py --use-legacy
   ```

#### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --env-file PATH           Path to .env file (default: .env)
  --env-preset PRESET       Use preset: default, company, or products
  --offset N                Starting offset for data retrieval (default: 0)
  --limit N                 Maximum records to process (overrides PROCESS_LIMIT)
  --use-legacy              Use legacy DataSyncApp class
  --validate-only           Only validate configuration without running sync
  -h, --help                Show help message
```

### Programmatic Usage (Functional API)

The application can be imported and used as a library in other Python applications.

#### Example 1: Basic Usage

```python
from data_sync_api import DataSyncAPI, SyncConfig

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
    process_limit=1000
)

# Create API instance and sync data
api = DataSyncAPI(config)
result = api.sync_data()

# Check results
if result.success:
    print(f"Processed: {result.total_processed}")
    print(f"Published: {result.total_published}")
    print(f"Success rate: {result.details.get('success_rate', 0):.1f}%")
else:
    print(f"Failed: {result.error_message}")
```

#### Example 2: Using Environment Files

```python
from data_sync_api import create_config_from_env, DataSyncAPI

# Load configuration from .env file
config = create_config_from_env(".env.company")

# Customize settings
config.process_limit = 500
config.enable_logging = False  # Disable logging for library use

# Sync data with offset and limit
api = DataSyncAPI(config)
result = api.sync_data(offset=100, limit=200)

print(f"Result: {'Success' if result.success else 'Failed'}")
```

#### Example 3: Simple Function Call

```python
from data_sync_api import sync_data_simple

# Define configurations
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
    "rabbitmq_password": "guest"
}

# Sync data
result = sync_data_simple(
    clickhouse_config=clickhouse_config,
    rabbitmq_config=rabbitmq_config,
    batch_size=200,
    process_limit=100
)
```

#### Example 4: Integration in Application

```python
from data_sync_api import DataSyncAPI, create_config_from_env

class DataProcessor:
    def __init__(self, env_file: str = None):
        self.config = create_config_from_env(env_file)
        self.config.enable_logging = False
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
processor = DataProcessor(".env.company")
if processor.health_check():
    summary = processor.sync_companies(max_records=100)
    print(f"Sync summary: {summary}")
```

#### Example 5: Configuration Validation

```python
from data_sync_api import DataSyncAPI, SyncConfig

config = SyncConfig(
    clickhouse_host="localhost",
    rabbitmq_host="localhost"
)

api = DataSyncAPI(config)

# Validate configuration
validation_result = api.validate_configuration()

if validation_result.success:
    print("✅ Configuration is valid")
    print(f"ClickHouse records: {validation_result.details.get('clickhouse_records')}")
    print(f"RabbitMQ connected: {validation_result.details.get('rabbitmq_connected')}")
else:
    print(f"❌ Validation failed: {validation_result.error_message}")
```

#### SyncConfig Parameters

```python
SyncConfig(
    # ClickHouse configuration
    clickhouse_host: str = "localhost",
    clickhouse_port: int = 9000,
    clickhouse_user: str = "default",
    clickhouse_password: str = "",
    clickhouse_database: str = "mart",
    clickhouse_table: str = "datamart.statgov_snap_legal_entities_v1_2_view_latest",
    
    # RabbitMQ configuration
    rabbitmq_host: str = "localhost",
    rabbitmq_port: int = 5672,
    rabbitmq_user: str = "guest",
    rabbitmq_password: str = "guest",
    rabbitmq_queue: str = "legal_entities_queue",
    rabbitmq_exchange: str = "data_exchange",
    rabbitmq_exchange_type: str = "direct",
    rabbitmq_routing_key: str = "data.processed",
    
    # Processing configuration
    batch_size: int = 1000,
    max_retries: int = 3,
    process_limit: int = -1,  # -1 means no limit
    
    # Field mapping configuration
    field_mapping_config_path: Optional[str] = "field_mapping.json",
    
    # Logging configuration
    enable_logging: bool = True,
    log_level: str = "INFO"
)
```

#### SyncResult Structure

```python
@dataclass
class SyncResult:
    success: bool                    # Whether sync was successful
    total_processed: int = 0         # Total records processed
    total_published: int = 0         # Total records published to RabbitMQ
    total_failed: int = 0            # Total records that failed
    batches_processed: int = 0       # Number of batches processed
    error_message: Optional[str]     # Error message if failed
    execution_time: float = 0.0      # Execution time in seconds
    details: Dict[str, Any]          # Additional details (success_rate, etc.)
```

### More Examples

See `usage_examples.py` for comprehensive examples including:
- Batch processing with custom logic
- Error recovery and retry mechanisms
- Integration patterns for larger applications

## Data Flow

1. **Configuration Loading**: Load field mapping from JSON file
2. **Validation**: Validate configuration and database compatibility  
3. **Dynamic SQL Generation**: Build SELECT query based on field mappings
4. **Data Extraction**: Fetch data from configured ClickHouse table
5. **Universal Transformation**: Transform data using configurable rules
6. **Validation & Filtering**: Apply validation rules and filters
7. **Publishing**: Send transformed data to RabbitMQ queue

## Validation System

The application includes a comprehensive validation system:

### Configuration Validation
- **JSON Schema Validation**: Validates structure against schema
- **Business Rules**: Checks field mappings and cross-references
- **Type Compatibility**: Ensures data types are compatible

### Database Validation
- **Schema Compatibility**: Verifies fields exist in database
- **Type Mapping**: Checks ClickHouse to config type compatibility
- **Sample Query Testing**: Tests actual data retrieval

### Runtime Validation
- **Field Validation**: Validates individual field values
- **Record Validation**: Checks required fields and constraints
- **Error Reporting**: Detailed logging of validation issues

## Error Handling

Enhanced error handling includes:
- **Configuration Errors**: Invalid JSON, missing fields, type mismatches
- **Database Errors**: Connection issues, missing tables/fields, query failures
- **Transformation Errors**: Data type conversion, validation failures
- **Publishing Errors**: RabbitMQ connection issues, message failures
- **Retry Logic**: Automatic retries with exponential backoff
- **Graceful Degradation**: Fallback to hardcoded transformation if needed

## Troubleshooting

### Common Issues

1. **Configuration Validation Fails**
   ```bash
   # Validate using the new API
   python main.py --validate-only
   
   # Check configuration syntax
   python -c "import json; json.load(open('field_mapping.json'))"
   ```

2. **Database Connection Issues**
   ```bash
   # Test ClickHouse connection
   python check_connection.py
   ```

3. **Field Mapping Errors**
   ```bash
   # Test field mappings
   python test_field_mapping.py
   ```

4. **Transformation Issues**
   ```bash
   # Test transformer
   python test_universal_transform.py
   ```

### Debug Mode

Enable debug logging:

```python
# In your script
from data_sync_api import DataSyncAPI, SyncConfig

config = SyncConfig(
    # ... other config ...
    enable_logging=True,
    log_level="DEBUG"
)

api = DataSyncAPI(config)
```

Or set it globally:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration Guide

### From Hardcoded to Universal Configuration

1. **Create Field Mapping**: Use existing `field_mapping.json` as template
2. **Update Environment**: Add `FIELD_MAPPING_CONFIG_PATH` to `.env`
3. **Validate Configuration**: Run validation tests
4. **Test with Sample Data**: Verify transformations work correctly
5. **Deploy**: The system automatically uses universal transformer

### Backward Compatibility

The system maintains backward compatibility:
- If no field mapping config is found, falls back to hardcoded transformation
- Existing `.env` configurations continue to work
- No changes required to existing deployment scripts
- Legacy mode available with `--use-legacy` flag

## Examples

See the following files for examples:
- `examples/` directory: Different table configurations and field mapping patterns
- `usage_examples.py`: Comprehensive functional API usage examples

## License

This project is licensed under the MIT License.
