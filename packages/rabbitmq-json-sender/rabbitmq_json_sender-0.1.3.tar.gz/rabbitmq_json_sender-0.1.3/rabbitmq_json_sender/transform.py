from typing import Dict, Any, List, Optional
import logging
from datetime import date, datetime
from . import config

logger = logging.getLogger(__name__)

def transform_company(company: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Transform a single company record from ClickHouse format to the target JSON schema.
    Uses universal transformer if field mapping configuration is available,
    otherwise falls back to hardcoded transformation.
    
    Args:
        company: Dictionary containing company data from ClickHouse
        
    Returns:
        Transformed company data as a dictionary or None if transformation fails
    """
    # Use universal transformer if configuration is available
    if config.field_mapping:
        try:
            from .universal_transform import UniversalTransformer
            transformer = UniversalTransformer(config.field_mapping)
            return transformer.transform_record(company)
        except Exception as e:
            logger.warning(f"Universal transformer failed, falling back to hardcoded: {str(e)}")
    
    # Fallback to original hardcoded transformation
    try:
        # Extract and validate BIN
        bin_value = company.get('bin')
        if not bin_value:
            logger.warning(f"Missing BIN for company ID {company.get('id')}")
            return None
            
        # Convert BIN to string (handle bytes objects from ClickHouse)
        if isinstance(bin_value, bytes):
            bin_str = bin_value.decode('utf-8').strip()
        else:
            bin_str = str(bin_value).strip()
            
        # Validate it contains only digits
        if not bin_str or not bin_str.isdigit():
            logger.warning(f"Invalid BIN: {bin_str} for company ID {company.get('id')}")
            return None
            
        
        # Format register date
        register_date = company.get('register_date')
        if isinstance(register_date, (date, datetime)):
            register_date = register_date.isoformat()
        
        # Parse OKED codes
        oked = company.get('oked')
        second_oked = company.get('second_oked')
        
        transformed = {
            'UF_BIN': bin_str,
            'UF_COMPANY_NAME': company.get('company_name', ''),
            'UF_COMPANY_FULL_NAME': company.get('full_company_name_rus', ''),
            'UF_ORG_FORM': company.get('org_form', ''),
            'UF_REGISTER_DATE': register_date or None,
            'UF_OKED': oked,
            'UF_MAIN_ACTIVITY': company.get('main_activity', ''),
            'UF_SECOND_OKED': second_oked if second_oked != oked else None,
            'UF_KRP_CODE': company.get('krp_code'),
            'UF_KRP_NAME': company.get('krp_name', ''),
            'UF_KSE_CODE': company.get('kse_code'),
            'UF_KSE_NAME': company.get('kse_name', ''),
            'UF_KFS_CODE': company.get('kfs_code'),
            'UF_KFS_NAME': company.get('kfs_name', ''),
            'UF_KATO_CODE': company.get('kato_code'),
            'UF_CITY_NAME': company.get('city_name', ''),
            'UF_ADDRESS': company.get('legal_address', ''),
            'UF_CEO_NAME': company.get('ceo_name', ''),
            'UF_REGION': company.get('region', ''),
            'UF_COMPANYTYPE_CODE': company.get('legal_entity_type', ''),
            'UF_COMPANYTYPE_NAME': company.get('legal_entity_type_txt', '')
        }
        
        # Remove None values to reduce message size
        return {k: v for k, v in transformed.items() if v is not None}
        
    except Exception as e:
        logger.error(f"Error transforming company {company.get('id')}: {str(e)}")
        return None

def transform_batch(companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform a batch of company records.
    Uses universal transformer if field mapping configuration is available,
    otherwise falls back to hardcoded transformation.
    
    Args:
        companies: List of company dictionaries from ClickHouse
        
    Returns:
        List of transformed company records
    """
    # Use universal transformer if configuration is available
    if config.field_mapping:
        try:
            from .universal_transform import UniversalTransformer
            transformer = UniversalTransformer(config.field_mapping)
            return transformer.transform_batch(companies)
        except Exception as e:
            logger.warning(f"Universal transformer failed, falling back to hardcoded: {str(e)}")
    
    # Fallback to original transformation logic
    transformed = []
    for company in companies:
        result = transform_company(company)
        if result and result.get('UF_BIN') and result.get('UF_COMPANY_NAME'):
            transformed.append(result)
    return transformed

def _parse_int(value: Any) -> Optional[int]:
    """Safely parse an integer value from various input types."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            # Remove any non-digit characters
            digits = ''.join(c for c in value if c.isdigit())
            return int(digits) if digits else None
        return int(value)
    except (ValueError, TypeError):
        return None
