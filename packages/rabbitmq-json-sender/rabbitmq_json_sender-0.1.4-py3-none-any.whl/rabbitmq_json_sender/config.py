import os
from dotenv import load_dotenv
from .field_mapping import FieldMappingConfig

# Global variables that will be set by load_config()
CLICKHOUSE_HOST = None
CLICKHOUSE_PORT = None
CLICKHOUSE_USER = None
CLICKHOUSE_PASSWORD = None
CLICKHOUSE_DATABASE = None
CLICKHOUSE_TABLE = None
RABBITMQ_HOST = None
RABBITMQ_PORT = None
RABBITMQ_USER = None
RABBITMQ_PASSWORD = None
RABBITMQ_QUEUE = None
RABBITMQ_EXCHANGE = None
RABBITMQ_EXCHANGE_TYPE = None
RABBITMQ_ROUTING_KEY = None
BATCH_SIZE = None
MAX_RETRIES = None
PROCESS_LIMIT = None
FIELD_MAPPING_CONFIG_PATH = None
field_mapping = None

def load_config(env_file_path=None):
    """Load configuration from specified .env file or default .env"""
    global CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD
    global CLICKHOUSE_DATABASE, CLICKHOUSE_TABLE, RABBITMQ_HOST, RABBITMQ_PORT
    global RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE, RABBITMQ_EXCHANGE
    global RABBITMQ_EXCHANGE_TYPE, RABBITMQ_ROUTING_KEY, BATCH_SIZE, MAX_RETRIES
    global PROCESS_LIMIT, FIELD_MAPPING_CONFIG_PATH, field_mapping
    
    # Clear existing environment variables to avoid conflicts
    env_vars_to_clear = [
        'CLICKHOUSE_HOST', 'CLICKHOUSE_PORT', 'CLICKHOUSE_USER', 'CLICKHOUSE_PASSWORD',
        'CLICKHOUSE_DATABASE', 'CLICKHOUSE_TABLE', 'RABBITMQ_HOST', 'RABBITMQ_PORT',
        'RABBITMQ_USER', 'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE', 'RABBITMQ_EXCHANGE',
        'RABBITMQ_EXCHANGE_TYPE', 'RABBITMQ_ROUTING_KEY', 'BATCH_SIZE', 'MAX_RETRIES',
        'PROCESS_LIMIT', 'FIELD_MAPPING_CONFIG_PATH'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    # Load new environment file
    if env_file_path:
        load_dotenv(env_file_path, override=True)
    else:
        load_dotenv(override=True)
    
    # Set configuration variables
    CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
    CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', 9000))
    CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
    CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')
    CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'mart')
    CLICKHOUSE_TABLE = os.getenv('CLICKHOUSE_TABLE', 'datamart.statgov_snap_legal_entities_v1_2_view_latest')

    # RabbitMQ configuration
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'legal_entities_queue')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'data_exchange')
    RABBITMQ_EXCHANGE_TYPE = os.getenv('RABBITMQ_EXCHANGE_TYPE', 'direct')
    RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY', 'data.processed')

    # Application configuration
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    PROCESS_LIMIT = int(os.getenv('PROCESS_LIMIT', -1))

    # Field mapping configuration
    FIELD_MAPPING_CONFIG_PATH = os.getenv('FIELD_MAPPING_CONFIG_PATH', 'field_mapping.json')

    # Initialize field mapping configuration
    try:
        field_mapping = FieldMappingConfig(FIELD_MAPPING_CONFIG_PATH)
        # Override CLICKHOUSE_TABLE with value from field mapping if available
        if field_mapping.get_source_table():
            CLICKHOUSE_TABLE = field_mapping.get_source_table()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not load field mapping config: {e}. Using default configuration.")
        field_mapping = None

# Default load
load_config()
