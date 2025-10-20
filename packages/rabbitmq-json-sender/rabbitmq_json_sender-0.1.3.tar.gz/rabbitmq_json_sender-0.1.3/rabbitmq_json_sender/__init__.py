"""
RabbitMQ JSON Sender - Universal ClickHouse to RabbitMQ Data Sync
A configurable data synchronization system with field mapping and validation.
"""

__version__ = "0.1.3"

# Import main API classes for easy access
from .data_sync_api import (
    DataSyncAPI,
    SyncConfig,
    SyncResult,
    sync_data_simple,
    create_config_from_env,
)

# Import configuration and field mapping
from .config import load_config
from .field_mapping import FieldMappingConfig

# Import clients
from .clickhouse_client import ClickHouseClient
from .rabbitmq_client import RabbitMQClient

# Import transformers
from .transform import transform_company, transform_batch
from .universal_transform import UniversalTransformer

__all__ = [
    # Main API
    "DataSyncAPI",
    "SyncConfig",
    "SyncResult",
    "sync_data_simple",
    "create_config_from_env",
    
    # Configuration
    "load_config",
    "FieldMappingConfig",
    
    # Clients
    "ClickHouseClient",
    "RabbitMQClient",
    
    # Transformers
    "transform_company",
    "transform_batch",
    "UniversalTransformer",
    
    # Version
    "__version__",
]
