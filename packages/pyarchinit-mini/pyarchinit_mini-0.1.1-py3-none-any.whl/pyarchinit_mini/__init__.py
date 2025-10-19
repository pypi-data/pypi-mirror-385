"""
PyArchInit-Mini: Standalone Archaeological Data Management System

A lightweight, modular version of PyArchInit focused on core archaeological 
data management functionality without GIS dependencies.

Features:
- Site management
- Stratigraphic Unit (US) management  
- Material inventory management
- Multi-database support (PostgreSQL/SQLite)
- REST API interface
- Scalable and modular architecture
"""

__version__ = "0.1.0"
__author__ = "PyArchInit Team"
__email__ = "enzo.ccc@gmail.com"

from .database.manager import DatabaseManager
from .services.site_service import SiteService
from .services.us_service import USService
from .services.inventario_service import InventarioService

__all__ = [
    "DatabaseManager",
    "SiteService", 
    "USService",
    "InventarioService"
]