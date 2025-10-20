"""
Custom exceptions for PyArchInit-Mini
"""

class PyArchInitError(Exception):
    """Base exception for PyArchInit-Mini"""
    pass

class DatabaseError(PyArchInitError):
    """Database related errors"""
    pass

class ValidationError(PyArchInitError):
    """Data validation errors"""
    pass

class ServiceError(PyArchInitError):
    """Service layer errors"""
    pass

class ConfigurationError(PyArchInitError):
    """Configuration errors"""
    pass