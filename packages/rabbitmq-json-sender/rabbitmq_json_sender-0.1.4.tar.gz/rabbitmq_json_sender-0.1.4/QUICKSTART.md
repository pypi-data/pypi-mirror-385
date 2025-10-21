# Quick Start Guide

## Installation

```bash
# Install with Poetry
poetry add rabbitmq-json-sender

# Or with pip
pip install rabbitmq-json-sender
```

## Basic Usage

### 1. Command-Line Tool

```bash
# Run with default .env file
rabbitmq-json-sender

# Validate configuration
rabbitmq-json-sender --validate-only

# Process specific range
rabbitmq-json-sender --offset 0 --limit 1000

# Use custom .env file
rabbitmq-json-sender --env-file /path/to/.env
```

### 2. Python Library - Simple

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
    process_limit=1000
)

print(f"Success: {result.success}")
print(f"Processed: {result.total_processed}")
```

### 3. Python Library - Full Control

```python
from rabbitmq_json_sender import DataSyncAPI, SyncConfig

# Create configuration
config = SyncConfig(
    clickhouse_host="localhost",
    clickhouse_port=9000,
    clickhouse_database="mart",
    rabbitmq_host="localhost",
    rabbitmq_port=5672,
    batch_size=1000,
    process_limit=5000
)

# Run sync
api = DataSyncAPI(config)
result = api.sync_data(offset=0, limit=1000)

# Check results
if result.success:
    print(f"✅ Processed: {result.total_processed}")
    print(f"✅ Published: {result.total_published}")
    print(f"✅ Success rate: {result.details['success_rate']:.1f}%")
else:
    print(f"❌ Error: {result.error_message}")
```

### 4. Load Configuration from .env

```python
from rabbitmq_json_sender import create_config_from_env, DataSyncAPI

# Load from .env file
config = create_config_from_env(".env.production")

# Customize if needed
config.process_limit = 10000
config.enable_logging = False

# Run sync
api = DataSyncAPI(config)
result = api.sync_data()
```

## Integration Examples

### Django/Celery Task

```python
# tasks.py
from celery import shared_task
from rabbitmq_json_sender import DataSyncAPI, create_config_from_env

@shared_task
def sync_to_rabbitmq():
    config = create_config_from_env()
    api = DataSyncAPI(config)
    result = api.sync_data()
    
    return {
        'success': result.success,
        'processed': result.total_processed
    }
```

### FastAPI Endpoint

```python
from fastapi import FastAPI, BackgroundTasks
from rabbitmq_json_sender import DataSyncAPI, create_config_from_env

app = FastAPI()

@app.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    def run_sync():
        config = create_config_from_env()
        api = DataSyncAPI(config)
        api.sync_data()
    
    background_tasks.add_task(run_sync)
    return {"status": "started"}
```

### Scheduled Job (APScheduler)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from rabbitmq_json_sender import DataSyncAPI, create_config_from_env

def sync_job():
    config = create_config_from_env()
    api = DataSyncAPI(config)
    result = api.sync_data()
    print(f"Sync completed: {result.total_processed} records")

scheduler = BlockingScheduler()
scheduler.add_job(sync_job, 'interval', hours=1)
scheduler.start()
```

## Configuration

Create a `.env` file:

```env
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=mart
CLICKHOUSE_TABLE=your_table

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=data_exchange
RABBITMQ_ROUTING_KEY=data.processed

BATCH_SIZE=1000
PROCESS_LIMIT=-1
FIELD_MAPPING_CONFIG_PATH=field_mapping.json
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [INSTALL.md](INSTALL.md) for advanced installation options
- Check [usage_examples.py](usage_examples.py) for more examples
- Review [examples/](examples/) directory for field mapping configurations
