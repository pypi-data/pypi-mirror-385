"""
Custom exceptions for PyArchInit-Mini
"""

class PyArchInitMiniError(Exception):
    """Base exception class for PyArchInit-Mini"""
    pass

class DatabaseError(PyArchInitMiniError):
    """Raised when database operations fail"""
    pass

class ValidationError(PyArchInitMiniError):
    """Raised when data validation fails"""
    def __init__(self, message: str, field: str = None, value = None):
        super().__init__(message)
        self.field = field
        self.value = value

class RecordNotFoundError(PyArchInitMiniError):
    """Raised when a requested record is not found"""
    pass

class DuplicateRecordError(PyArchInitMiniError):
    """Raised when trying to create a duplicate record"""
    pass

class ConnectionError(PyArchInitMiniError):
    """Raised when database connection fails"""
    pass

class ConfigurationError(PyArchInitMiniError):
    """Raised when configuration is invalid"""
    pass

class PermissionError(PyArchInitMiniError):
    """Raised when user lacks required permissions"""
    pass