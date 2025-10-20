import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime

logger = logging.getLogger(__name__)

class FieldMappingConfig:
    """
    Manages field mapping configuration for dynamic data transformation.
    """
    
    def __init__(self, config_path: str = "field_mapping.json"):
        """
        Initialize field mapping configuration.
        
        Args:
            config_path: Path to the field mapping JSON configuration file
        """
        self.config_path = config_path
        self.config = {}
        self.field_mappings = {}
        self.source_config = {}
        self.transformations = {}
        self.validation_rules = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.field_mappings = self.config.get('field_mappings', {})
            self.source_config = self.config.get('source', {})
            self.transformations = self.config.get('transformations', {})
            self.validation_rules = self.config.get('validation_rules', {})
            
            logger.info(f"Loaded field mapping configuration from {self.config_path}")
            logger.info(f"Found {len(self.field_mappings)} field mappings")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def get_source_table(self) -> str:
        """Get the source table name."""
        return self.source_config.get('table', '')
    
    def get_primary_key(self) -> str:
        """Get the primary key field name."""
        return self.source_config.get('primary_key', 'id')
    
    def get_batch_column(self) -> str:
        """Get the column used for batching."""
        return self.source_config.get('batch_column', 'id')
    
    def get_order_by(self) -> str:
        """Get the ORDER BY column."""
        return self.source_config.get('order_by', 'id')
    
    def get_source_fields(self) -> List[str]:
        """
        Get list of source fields that should be selected from database.
        
        Returns:
            List of field names to select from source table
        """
        fields = []
        for source_field, config in self.field_mappings.items():
            # Skip fields that don't have a target (like internal IDs)
            if config.get('target') is not None:
                # Use alias if specified, otherwise use the field name
                alias = config.get('alias')
                if alias:
                    fields.append(f"{source_field} as {alias}")
                else:
                    fields.append(source_field)
            elif source_field == self.get_primary_key():
                # Always include primary key for processing
                fields.append(source_field)
        
        return fields
    
    def get_field_mapping(self, source_field: str) -> Optional[Dict[str, Any]]:
        """
        Get mapping configuration for a specific source field.
        
        Args:
            source_field: Name of the source field
            
        Returns:
            Field mapping configuration or None if not found
        """
        return self.field_mappings.get(source_field)
    
    def get_target_field(self, source_field: str) -> Optional[str]:
        """
        Get target field name for a source field.
        
        Args:
            source_field: Name of the source field
            
        Returns:
            Target field name or None if no mapping exists
        """
        mapping = self.get_field_mapping(source_field)
        return mapping.get('target') if mapping else None
    
    def is_field_required(self, source_field: str) -> bool:
        """
        Check if a field is required.
        
        Args:
            source_field: Name of the source field
            
        Returns:
            True if field is required, False otherwise
        """
        mapping = self.get_field_mapping(source_field)
        return mapping.get('required', False) if mapping else False
    
    def get_field_type(self, source_field: str) -> str:
        """
        Get the expected type for a field.
        
        Args:
            source_field: Name of the source field
            
        Returns:
            Field type (string, integer, date, etc.)
        """
        mapping = self.get_field_mapping(source_field)
        return mapping.get('type', 'string') if mapping else 'string'
    
    def get_field_validation(self, source_field: str) -> Dict[str, Any]:
        """
        Get validation rules for a field.
        
        Args:
            source_field: Name of the source field
            
        Returns:
            Dictionary of validation rules
        """
        mapping = self.get_field_mapping(source_field)
        return mapping.get('validation', {}) if mapping else {}
    
    def should_remove_null_values(self) -> bool:
        """Check if null values should be removed from output."""
        return self.transformations.get('remove_null_values', True)
    
    def should_exclude_empty_strings(self) -> bool:
        """Check if empty strings should be excluded from output."""
        return self.transformations.get('exclude_empty_strings', False)
    
    def get_date_format(self) -> str:
        """Get the date format for transformations."""
        return self.transformations.get('date_format', 'iso')
    
    def get_encoding(self) -> str:
        """Get the encoding for text transformations."""
        return self.transformations.get('encoding', 'utf-8')
    
    def get_byte_handling(self) -> str:
        """Get the byte handling strategy."""
        return self.transformations.get('byte_handling', 'decode_utf8')
    
    def get_required_output_fields(self) -> List[str]:
        """Get list of fields that must be present in output."""
        return self.validation_rules.get('required_fields', [])
    
    def get_skip_record_conditions(self) -> List[str]:
        """Get list of source fields that if missing should cause record to be skipped."""
        return self.validation_rules.get('skip_record_if_missing', [])
    
    def should_log_validation_errors(self) -> bool:
        """Check if validation errors should be logged."""
        return self.validation_rules.get('log_validation_errors', True)
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a record against the configuration rules.
        
        Args:
            record: Record to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for required source fields (after converting bytes to strings)
        skip_conditions = self.get_skip_record_conditions()
        for field in skip_conditions:
            value = record.get(field)
            # Convert bytes to string for validation
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8').strip()
                except UnicodeDecodeError:
                    value = None
            
            if not value:
                errors.append(f"Missing required source field: {field}")
        
        # Validate individual fields
        for source_field, value in record.items():
            validation_rules = self.get_field_validation(source_field)
            field_errors = self._validate_field_value(source_field, value, validation_rules)
            errors.extend(field_errors)
        
        return len(errors) == 0, errors
    
    def _validate_field_value(self, field_name: str, value: Any, rules: Dict[str, Any]) -> List[str]:
        """
        Validate a single field value against its rules.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            rules: Validation rules
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not rules:
            return errors
        
        # Convert bytes to string for validation
        if isinstance(value, bytes):
            try:
                value = value.decode('utf-8').strip()
            except UnicodeDecodeError:
                errors.append(f"Field {field_name} contains invalid bytes")
                return errors
        
        # Check digits_only validation
        if rules.get('type') == 'digits_only' and value:
            str_value = str(value).strip()
            if not str_value.isdigit():
                errors.append(f"Field {field_name} must contain only digits")
        
        # Check length validations
        if value and isinstance(value, (str, bytes)):
            str_value = str(value) if not isinstance(value, bytes) else value.decode('utf-8', errors='replace')
            min_length = rules.get('min_length')
            max_length = rules.get('max_length')
            
            if min_length and len(str_value) < min_length:
                errors.append(f"Field {field_name} is too short (min: {min_length})")
            
            if max_length and len(str_value) > max_length:
                errors.append(f"Field {field_name} is too long (max: {max_length})")
        
        return errors
    
    def reload_config(self):
        """Reload configuration from file."""
        self._load_config()
