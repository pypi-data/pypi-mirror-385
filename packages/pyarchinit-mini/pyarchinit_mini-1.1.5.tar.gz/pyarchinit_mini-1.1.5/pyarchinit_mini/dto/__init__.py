"""
Data Transfer Objects (DTOs) for PyArchInit-Mini

DTOs are simple data classes that hold data without database session dependencies.
They solve SQLAlchemy session management issues in GUI applications.
"""

from .site_dto import SiteDTO
from .us_dto import USDTO
from .inventario_dto import InventarioDTO

__all__ = [
    "SiteDTO",
    "USDTO", 
    "InventarioDTO"
]