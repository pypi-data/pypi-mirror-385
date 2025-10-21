# Configuration Examples

This directory contains example configurations for different types of ClickHouse tables and use cases.

## Available Examples

### 1. Legal Entities Configuration (`legal_entities_mapping.json`)
- **Use Case**: Company/legal entity data synchronization
- **Features**: BIN validation, date transformations, organizational forms
- **Target Fields**: UF_* prefixed fields for CRM integration

### 2. Financial Data Configuration (`financial_data_mapping.json`)
- **Use Case**: Financial transactions and accounting data
- **Features**: Decimal precision, currency codes, transaction types
- **Target Fields**: FIN_* prefixed fields

### 3. User Data Configuration (`user_data_mapping.json`)
- **Use Case**: User profiles and authentication data
- **Features**: Email validation, phone formatting, role mappings
- **Target Fields**: USER_* prefixed fields

### 4. Product Catalog Configuration (`product_catalog_mapping.json`)
- **Use Case**: E-commerce product data
- **Features**: SKU validation, price formatting, category hierarchies
- **Target Fields**: PROD_* prefixed fields

### 5. Minimal Configuration (`minimal_mapping.json`)
- **Use Case**: Simple table with basic fields
- **Features**: Demonstrates minimal required configuration
- **Target Fields**: Basic field mappings

## How to Use Examples

1. **Copy Example**: Copy the relevant example to your project root
   ```bash
   cp examples/legal_entities_mapping.json field_mapping.json
   ```

2. **Customize**: Edit the configuration to match your table structure
   - Update `source.table` with your table name
   - Modify field mappings to match your columns
   - Adjust validation rules as needed

3. **Validate**: Test your configuration
   ```bash
   python test_validation_system.py
   ```

4. **Deploy**: Use the configuration in production
   ```bash
   python main.py
   ```

## Configuration Guidelines

### Naming Conventions
- **Source Fields**: Use actual database column names
- **Target Fields**: Use consistent prefixes (UF_, FIN_, USER_, etc.)
- **Descriptions**: Include meaningful descriptions for documentation

### Validation Best Practices
- Always validate critical fields (IDs, codes, required data)
- Use appropriate data types for better performance
- Set reasonable length constraints
- Include business rule validations

### Performance Considerations
- Exclude unnecessary fields using `"target": null`
- Use aliases for complex column expressions
- Order fields by query frequency
- Consider indexing on batch_column and order_by fields

## Customization Tips

### Adding New Field Types
```json
{
  "custom_field": {
    "target": "CUSTOM_FIELD",
    "type": "string",
    "validation": {
      "type": "regex",
      "pattern": "^[A-Z]{2}\\d{6}$"
    },
    "transformation": "uppercase"
  }
}
```

### Complex Validations
```json
{
  "email_field": {
    "target": "EMAIL",
    "type": "string",
    "validation": {
      "type": "email"
    }
  },
  "phone_field": {
    "target": "PHONE",
    "type": "string",
    "validation": {
      "type": "regex",
      "pattern": "^\\+?[1-9]\\d{1,14}$"
    }
  }
}
```

### Conditional Logic
```json
{
  "secondary_code": {
    "target": "SECONDARY_CODE",
    "type": "string",
    "validation": {
      "exclude_if_same_as": "primary_code"
    }
  }
}
```

## Testing Your Configuration

Always test your configuration before deployment:

```bash
# Validate configuration structure
python -c "from config_validator import validate_config_file; print(validate_config_file('field_mapping.json')[1])"

# Test database compatibility
python -c "from validation_reporter import run_validation_check; run_validation_check()"

# Test with sample data
python test_universal_transform.py
```
