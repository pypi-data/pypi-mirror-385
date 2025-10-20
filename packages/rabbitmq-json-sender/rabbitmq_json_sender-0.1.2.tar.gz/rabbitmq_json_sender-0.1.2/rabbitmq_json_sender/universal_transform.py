from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import date, datetime
from config import field_mapping

logger = logging.getLogger(__name__)

class UniversalTransformer:
    """
    Universal data transformer that uses field mapping configuration
    to transform records from source format to target JSON format.
    """
    
    def __init__(self, field_mapping_config=None):
        """
        Initialize the universal transformer.
        
        Args:
            field_mapping_config: FieldMappingConfig instance, uses global config if None
        """
        self.config = field_mapping_config or field_mapping
        if not self.config:
            raise ValueError("Field mapping configuration is required")
    
    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform a single record from source format to target JSON format.
        
        Args:
            record: Dictionary containing source data
            
        Returns:
            Transformed record as dictionary or None if transformation fails
        """
        try:
            # Validate record first
            is_valid, errors = self.config.validate_record(record)
            if not is_valid:
                if self.config.should_log_validation_errors():
                    for error in errors:
                        logger.warning(f"Validation error: {error}")
                return None
            
            transformed = {}
            
            # Transform each field according to configuration
            for source_field, source_value in record.items():
                target_field = self.config.get_target_field(source_field)
                
                # Skip fields that don't have a target mapping
                if not target_field:
                    continue
                
                # Transform the value
                transformed_value = self._transform_field_value(
                    source_field, source_value, self.config.get_field_mapping(source_field)
                )
                
                # Apply filtering rules
                if self._should_include_value(transformed_value):
                    transformed[target_field] = transformed_value
            
            # Validate required output fields are present
            required_fields = self.config.get_required_output_fields()
            for required_field in required_fields:
                if required_field not in transformed or not transformed[required_field]:
                    logger.warning(f"Missing required output field: {required_field}")
                    return None
            
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming record: {str(e)}", exc_info=True)
            return None
    
    def transform_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of records.
        
        Args:
            records: List of source record dictionaries
            
        Returns:
            List of transformed records
        """
        transformed_records = []
        
        for record in records:
            transformed = self.transform_record(record)
            if transformed:
                transformed_records.append(transformed)
        
        logger.info(f"Transformed {len(transformed_records)} out of {len(records)} records")
        return transformed_records
    
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
    
    def _transform_field_value(self, field_name: str, value: Any, field_config: Dict[str, Any]) -> Any:
        """
        Transform a single field value according to its configuration.
        
        Args:
            field_name: Name of the source field
            value: Value to transform
            field_config: Field configuration from mapping
            
        Returns:
            Transformed value
        """
        if value is None:
            return None
        
        # Handle bytes objects (common in ClickHouse)
        if isinstance(value, bytes):
            encoding = self.config.get_encoding()
            try:
                value = value.decode(encoding).strip()
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode bytes for field {field_name}")
                return None
        
        # Convert to string for processing
        if not isinstance(value, str) and not isinstance(value, (date, datetime, int, float)):
            value = str(value)
        
        # Apply type-specific transformations
        field_type = field_config.get('type', 'string')
        
        if field_type == 'string':
            return self._transform_string_value(field_name, value, field_config)
        elif field_type == 'date':
            return self._transform_date_value(field_name, value, field_config)
        elif field_type == 'integer':
            return self._transform_integer_value(field_name, value, field_config)
        else:
            # Default string transformation
            return self._transform_string_value(field_name, value, field_config)
    
    def _transform_string_value(self, field_name: str, value: Any, field_config: Dict[str, Any]) -> Optional[str]:
        """Transform string values."""
        if value is None:
            return None
        
        # Convert to string and strip whitespace
        str_value = str(value).strip()
        
        # Handle empty strings
        if not str_value:
            return None if self.config.should_exclude_empty_strings() else ""
        
        # Apply validation rules
        validation = field_config.get('validation', {})
        
        # Check for digits_only validation
        if validation.get('type') == 'digits_only':
            if not str_value.isdigit():
                logger.warning(f"Field {field_name} failed digits_only validation: {str_value}")
                return None
        
        # Check exclude_if_same_as rule
        exclude_if_same = validation.get('exclude_if_same_as')
        if exclude_if_same:
            # This would need access to the full record, implement if needed
            pass
        
        return str_value
    
    def _transform_date_value(self, field_name: str, value: Any, field_config: Dict[str, Any]) -> Optional[str]:
        """Transform date values."""
        if value is None:
            return None
        
        # Handle different date input formats
        if isinstance(value, (date, datetime)):
            date_obj = value
        elif isinstance(value, str):
            # Try to parse string dates
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        date_obj = datetime.strptime(value.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    logger.warning(f"Could not parse date for field {field_name}: {value}")
                    return None
            except Exception:
                logger.warning(f"Error parsing date for field {field_name}: {value}")
                return None
        else:
            logger.warning(f"Unsupported date type for field {field_name}: {type(value)}")
            return None
        
        # Format according to configuration
        transformation = field_config.get('transformation', 'iso_format')
        date_format = self.config.get_date_format()
        
        if transformation == 'iso_format' or date_format == 'iso':
            return date_obj.isoformat()
        else:
            return str(date_obj)
    
    def _transform_integer_value(self, field_name: str, value: Any, field_config: Dict[str, Any]) -> Optional[int]:
        """Transform integer values."""
        if value is None:
            return None
        
        try:
            if isinstance(value, str):
                # Remove any non-digit characters for cleaning
                digits = ''.join(c for c in value if c.isdigit())
                return int(digits) if digits else None
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert to integer for field {field_name}: {value}")
            return None
    
    def _should_include_value(self, value: Any) -> bool:
        """
        Determine if a value should be included in the output.
        
        Args:
            value: Value to check
            
        Returns:
            True if value should be included, False otherwise
        """
        # Remove null values if configured
        if value is None and self.config.should_remove_null_values():
            return False
        
        # Remove empty strings if configured
        if value == "" and self.config.should_exclude_empty_strings():
            return False
        
        return True

# Backward compatibility functions
def transform_company(company: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Backward compatibility function for existing code.
    Transform a single company record using the universal transformer.
    """
    if not field_mapping:
        # Fallback to original implementation if no configuration
        from transform import transform_company as original_transform
        return original_transform(company)
    
    transformer = UniversalTransformer(field_mapping)
    return transformer.transform_record(company)

def transform_batch(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Backward compatibility function for existing code.
    Transform a batch of company records using the universal transformer.
    """
    if not field_mapping:
        # Fallback to original implementation if no configuration
        from transform import transform_batch as original_transform
        return original_transform(companies)
    
    transformer = UniversalTransformer(field_mapping)
    return transformer.transform_batch(companies)
