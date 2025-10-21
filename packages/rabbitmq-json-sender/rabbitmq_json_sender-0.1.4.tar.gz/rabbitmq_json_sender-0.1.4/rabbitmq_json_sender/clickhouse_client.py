import clickhouse_connect
from clickhouse_connect.driver.exceptions import ClickHouseError
import logging
from typing import List, Dict, Any, Optional
from . import config

logger = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self):
        try:
            # Build connection parameters
            connection_params = {
                'host': config.CLICKHOUSE_HOST,
                'port': config.CLICKHOUSE_PORT,
                'username': config.CLICKHOUSE_USER,
                'password': config.CLICKHOUSE_PASSWORD,
                'database': config.CLICKHOUSE_DATABASE,
                'connect_timeout': 10,
                'secure': False  # Set to True if using HTTPS
            }
            
            CONNECTION_STRING = f"http://{config.CLICKHOUSE_USER}:{config.CLICKHOUSE_PASSWORD}@{config.CLICKHOUSE_HOST}:{config.CLICKHOUSE_PORT}/"

            logger.info(f"Attempting to connect to ClickHouse at {config.CLICKHOUSE_HOST}:{config.CLICKHOUSE_PORT}")
            logger.debug(f"Connection parameters: { {k: '*****' if k == 'password' else v for k, v in connection_params.items()} }")
            
            # Try to connect
            self.client = clickhouse_connect.get_client(dsn=CONNECTION_STRING,database=config.CLICKHOUSE_DATABASE)
            
            # Test the connection
            server_info = self.client.server_version
            logger.info(f"Successfully connected to ClickHouse ")
            
        except Exception as e:
            error_msg = f"Failed to connect to ClickHouse at {config.CLICKHOUSE_HOST}:{config.CLICKHOUSE_PORT}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e

    def fetch_companies_batch(self, offset: int = 0, limit: int = None) -> List[Dict[str, Any]]:
        """
        Fetch a batch of companies from the configured table using dynamic field mapping.
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of company records as dictionaries
        """
        # Build the query dynamically based on field mapping configuration
        if limit is None:
            limit = config.BATCH_SIZE
        query = self._build_select_query(offset, limit)
        
        for attempt in range(config.MAX_RETRIES):
            try:
                result = self.client.query(query)
                # Convert result to list of dictionaries
                columns = result.column_names
                return [dict(zip(columns, row)) for row in result.result_rows]
            except ClickHouseError as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == config.MAX_RETRIES - 1:
                    logger.error("Max retries reached. Could not fetch data from ClickHouse.")
                    raise
                continue
        return []
    
    def _build_select_query(self, offset: int, limit: int) -> str:
        """
        Build SELECT query dynamically based on field mapping configuration.
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Complete SQL SELECT query string
        """
        # Get table name from configuration or fallback to environment variable
        table_name = config.CLICKHOUSE_TABLE
        order_by_column = "id"
        
        if config.field_mapping:
            # Use configuration from field mapping
            if config.field_mapping.get_source_table():
                table_name = config.field_mapping.get_source_table()
            order_by_column = config.field_mapping.get_order_by()
            
            # Get fields to select from configuration
            source_fields = config.field_mapping.get_source_fields()
            fields_str = ",\n            ".join(source_fields)
        else:
            # Fallback to hardcoded fields if no configuration available
            logger.warning("No field mapping configuration available, using hardcoded fields")
            fields_str = """id,
            bin,
            full_company_name_rus as full_company_name_rus,
            register_date,
            oked,
            main_activity_rus as main_activity,
            second_oked,
            krp_code,
            krp_name_rus as krp_name,
            kse_code,
            kse_name_rus as kse_name,
            kfs_code,
            kfs_name_rus as kfs_name,
            kato_code,
            city_name_rus as city_name,
            legal_address,
            ceo_name,
            region,
            legal_entity_type,
            legal_entity_type_txt,
            org_form,
            company_name"""
        
        query = f"""
        SELECT 
            {fields_str}
        FROM {table_name}
        ORDER BY {order_by_column}
        LIMIT {limit} OFFSET {offset}
        """
        
        logger.debug(f"Generated SQL query: {query}")
        return query
    
    def get_total_companies_count(self) -> int:
        """Get the total number of companies in the configured table."""
        # Get table name from configuration or fallback to environment variable
        table_name = CLICKHOUSE_TABLE
        if field_mapping and field_mapping.get_source_table():
            table_name = field_mapping.get_source_table()
        
        query = f"SELECT count(*) as count FROM {table_name}"
        try:
            result = self.client.query(query)
            if result and result.result_rows:
                return result.result_rows[0][0]
            return 0
        except ClickHouseError as e:
            logger.error(f"Failed to get total companies count: {str(e)}")
            raise
