"""
Data validation utilities for PyArchInit-Mini
"""

import re
from typing import Dict, Any, List
from .exceptions import ValidationError

class BaseValidator:
    """Base validator class"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]):
        """Validate that all required fields are present and not empty"""
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Required field '{field}' is missing", field)
            if data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                raise ValidationError(f"Required field '{field}' cannot be empty", field, data[field])
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, max_length: int, min_length: int = 0):
        """Validate string length"""
        if value is None:
            return
        
        if len(value) > max_length:
            raise ValidationError(f"Field '{field_name}' exceeds maximum length of {max_length}", 
                                field_name, value)
        if len(value) < min_length:
            raise ValidationError(f"Field '{field_name}' is below minimum length of {min_length}", 
                                field_name, value)
    
    @staticmethod
    def validate_numeric_range(value, field_name: str, min_value=None, max_value=None):
        """Validate numeric value is within range"""
        if value is None:
            return
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"Field '{field_name}' must be >= {min_value}", 
                                field_name, value)
        if max_value is not None and value > max_value:
            raise ValidationError(f"Field '{field_name}' must be <= {max_value}", 
                                field_name, value)

class SiteValidator(BaseValidator):
    """Validator for Site model data"""
    
    @classmethod
    def validate(cls, data: Dict[str, Any]):
        """Validate site data"""
        # Required fields
        cls.validate_required_fields(data, ['sito'])
        
        # String length validations
        if 'sito' in data:
            cls.validate_string_length(data['sito'], 'sito', 350, 1)
        
        if 'nazione' in data and data['nazione']:
            cls.validate_string_length(data['nazione'], 'nazione', 250)
        
        if 'regione' in data and data['regione']:
            cls.validate_string_length(data['regione'], 'regione', 250)
        
        if 'comune' in data and data['comune']:
            cls.validate_string_length(data['comune'], 'comune', 250)
        
        if 'provincia' in data and data['provincia']:
            cls.validate_string_length(data['provincia'], 'provincia', 10)
        
        if 'definizione_sito' in data and data['definizione_sito']:
            cls.validate_string_length(data['definizione_sito'], 'definizione_sito', 250)
        
        # Site name should be unique - this would be validated at service level
        if 'sito' in data:
            site_name = data['sito'].strip()
            if not site_name:
                raise ValidationError("Site name cannot be empty", 'sito', data['sito'])
            
            # Basic name validation (alphanumeric + spaces, hyphens, underscores)
            if not re.match(r'^[a-zA-Z0-9\s\-_àáâäèéêëìíîïòóôöùúûüñç]+$', site_name):
                raise ValidationError("Site name contains invalid characters", 'sito', site_name)

class USValidator(BaseValidator):
    """Validator for US (Stratigraphic Unit) model data"""
    
    @classmethod
    def validate(cls, data: Dict[str, Any]):
        """Validate US data"""
        # Required fields
        cls.validate_required_fields(data, ['sito', 'us'])
        
        # String length validations
        if 'sito' in data:
            cls.validate_string_length(data['sito'], 'sito', 350, 1)
        
        if 'area' in data and data['area']:
            cls.validate_string_length(data['area'], 'area', 20)
        
        if 'd_stratigrafica' in data and data['d_stratigrafica']:
            cls.validate_string_length(data['d_stratigrafica'], 'd_stratigrafica', 350)
        
        if 'd_interpretativa' in data and data['d_interpretativa']:
            cls.validate_string_length(data['d_interpretativa'], 'd_interpretativa', 350)
        
        # US number validation
        if 'us' in data:
            us_num = data['us']
            if not isinstance(us_num, int) or us_num <= 0:
                raise ValidationError("US number must be a positive integer", 'us', us_num)
            cls.validate_numeric_range(us_num, 'us', 1, 999999)
        
        # Year validation
        if 'anno_scavo' in data and data['anno_scavo']:
            year = data['anno_scavo']
            if isinstance(year, int):
                cls.validate_numeric_range(year, 'anno_scavo', 1800, 2100)
        
        # Measurement validations
        measurement_fields = [
            'quota_relativa', 'quota_abs', 'lunghezza_max', 'altezza_max',
            'altezza_min', 'profondita_max', 'profondita_min', 'larghezza_media'
        ]
        
        for field in measurement_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValidationError(f"Field '{field}' must be a non-negative number", 
                                        field, value)

class InventarioValidator(BaseValidator):
    """Validator for Inventario Materiali model data"""
    
    @classmethod
    def validate(cls, data: Dict[str, Any]):
        """Validate inventory material data"""
        # Required fields
        cls.validate_required_fields(data, ['sito', 'numero_inventario'])
        
        # String length validations
        if 'sito' in data:
            cls.validate_string_length(data['sito'], 'sito', 350, 1)
        
        if 'tipo_reperto' in data and data['tipo_reperto']:
            cls.validate_string_length(data['tipo_reperto'], 'tipo_reperto', 20)
        
        if 'criterio_schedatura' in data and data['criterio_schedatura']:
            cls.validate_string_length(data['criterio_schedatura'], 'criterio_schedatura', 20)
        
        if 'definizione' in data and data['definizione']:
            cls.validate_string_length(data['definizione'], 'definizione', 20)
        
        # Inventory number validation
        if 'numero_inventario' in data:
            inv_num = data['numero_inventario']
            if not isinstance(inv_num, int) or inv_num <= 0:
                raise ValidationError("Inventory number must be a positive integer", 
                                    'numero_inventario', inv_num)
            cls.validate_numeric_range(inv_num, 'numero_inventario', 1, 999999999)
        
        # Area validation
        if 'area' in data and data['area']:
            cls.validate_string_length(data['area'], 'area', 20)
        
        # US validation - field is a string in the model (can be "1001", "1001a", etc.)
        if 'us' in data and data['us'] is not None and data['us'] != '':
            us_value = data['us']
            # Convert to string if it's an integer
            if isinstance(us_value, int):
                us_value = str(us_value)
            elif not isinstance(us_value, str):
                raise ValidationError("US must be a string or integer", 'us', us_value)

            # Validate it's not empty
            if not us_value.strip():
                raise ValidationError("US cannot be empty", 'us', us_value)

            # Validate length (max 20 chars as per model)
            cls.validate_string_length(us_value, 'us', 20)
        
        # Numeric field validations
        numeric_fields = [
            ('forme_minime', 0, 999999),
            ('forme_massime', 0, 999999), 
            ('totale_frammenti', 0, 999999),
            ('diametro_orlo', 0, 1000),
            ('peso', 0, 999999),
            ('eve_orlo', 0, 100),
            ('n_reperto', 1, 999999999),
            ('years', 1800, 2100)
        ]
        
        for field_name, min_val, max_val in numeric_fields:
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if isinstance(value, (int, float)):
                    cls.validate_numeric_range(value, field_name, min_val, max_val)
        
        # Validate choice fields (accept Italian and English yes/no values)
        yes_no_fields = ['lavato', 'repertato', 'diagnostico']
        for field in yes_no_fields:
            if field in data and data[field] is not None and data[field] != '':
                value = data[field].upper() if isinstance(data[field], str) else str(data[field])
                # Accept both Italian (Sì/No with accents) and English (Yes/No) values
                if value not in ['SI', 'SÌ', 'NO', 'S', 'N', 'YES', '1', '0', 'TRUE', 'FALSE']:
                    raise ValidationError(f"Field '{field}' must be a yes/no value", field, data[field])

def validate_data(model_type: str, data: Dict[str, Any]):
    """
    Validate data based on model type
    
    Args:
        model_type: Type of model ('site', 'us', 'inventario')
        data: Data to validate
    
    Raises:
        ValidationError: If validation fails
    """
    validators = {
        'site': SiteValidator,
        'us': USValidator,
        'inventario': InventarioValidator
    }
    
    if model_type not in validators:
        raise ValidationError(f"Unknown model type: {model_type}")
    
    validators[model_type].validate(data)