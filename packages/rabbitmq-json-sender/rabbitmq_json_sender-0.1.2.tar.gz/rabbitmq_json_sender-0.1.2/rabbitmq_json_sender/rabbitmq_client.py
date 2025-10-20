import pika
import json
import logging
from typing import List, Dict, Any
from pika.exceptions import AMQPError
from datetime import date, datetime
from config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, 
    RABBITMQ_PASSWORD, RABBITMQ_QUEUE, RABBITMQ_EXCHANGE,
    RABBITMQ_EXCHANGE_TYPE, RABBITMQ_ROUTING_KEY,
    MAX_RETRIES
)

logger = logging.getLogger(__name__)

def safe_json_dumps(obj):
    """Safely serialize objects to JSON, handling bytes and other non-serializable types."""
    def default_serializer(o):
        if isinstance(o, bytes):
            return o.decode('utf-8', errors='replace')
        elif isinstance(o, (date, datetime)):
            return o.isoformat()
        else:
            return str(o)
    
    return json.dumps(obj, default=default_serializer, ensure_ascii=False)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = RABBITMQ_EXCHANGE
        self.exchange_type = RABBITMQ_EXCHANGE_TYPE
        self.routing_key = RABBITMQ_ROUTING_KEY
        self._connect()

    def _connect(self):
        """Establish connection to RabbitMQ server."""
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        for attempt in range(MAX_RETRIES):
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare exchange for message routing (only if not using default exchange)
                if self.exchange_name:
                    self.channel.exchange_declare(
                        exchange=self.exchange_name,
                        exchange_type=self.exchange_type,
                        durable=True  # Make exchange persistent
                    )
                    logger.info(f"Declared exchange: {self.exchange_name} (type: {self.exchange_type})")
                else:
                    logger.info("Using default exchange (empty exchange name)")
                
                logger.info("Successfully connected to RabbitMQ")
                return
                
            except AMQPError as e:
                logger.error(f"Attempt {attempt + 1} failed to connect to RabbitMQ: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    logger.error("Max retries reached. Could not connect to RabbitMQ.")
                    raise

    def is_connected(self) -> bool:
        """Check if the connection to RabbitMQ is active."""
        return self.connection and self.connection.is_open

    def reconnect(self):
        """Reconnect to RabbitMQ if connection is lost."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        self._connect()

    def publish_batch(self, messages: List[Dict[str, Any]]) -> int:
        """
        Publish a batch of messages to RabbitMQ.
        
        Args:
            messages: List of message dictionaries to publish
            
        Returns:
            Number of successfully published messages
        """
        if not messages:
            return 0
            
        published_count = 0
        
        for message in messages:
            try:
                if not self.is_connected():
                    self.reconnect()
                    
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.routing_key,
                    body=safe_json_dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                        content_type='application/json'
                    )
                )
                published_count += 1
                
            except (AMQPError, json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to publish message: {str(e)}")
                if isinstance(e, AMQPError):
                    self.reconnect()
                continue
                
        return published_count

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
