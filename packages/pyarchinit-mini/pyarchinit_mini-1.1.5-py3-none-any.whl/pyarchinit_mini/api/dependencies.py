"""
FastAPI dependencies for PyArchInit-Mini
"""

from fastapi import Depends, HTTPException, Request
from ..database.connection import DatabaseConnection
from ..database.manager import DatabaseManager
from ..services.site_service import SiteService
from ..services.us_service import USService
from ..services.inventario_service import InventarioService

# Global database connection (will be initialized by app)
_db_connection = None

def get_database_connection() -> DatabaseConnection:
    """Get database connection dependency"""
    global _db_connection
    if _db_connection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return _db_connection

def get_database_manager(
    db_conn: DatabaseConnection = Depends(get_database_connection)
) -> DatabaseManager:
    """Get database manager dependency"""
    return DatabaseManager(db_conn)

def get_site_service(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> SiteService:
    """Get site service dependency"""
    return SiteService(db_manager)

def get_us_service(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> USService:
    """Get US service dependency"""
    return USService(db_manager)

def get_inventario_service(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> InventarioService:
    """Get inventario service dependency"""
    return InventarioService(db_manager)

def init_database(database_url: str):
    """Initialize global database connection"""
    global _db_connection
    _db_connection = DatabaseConnection.from_url(database_url)
    
    # Initialize database with migrations
    _db_connection.initialize_database()
    
    # Test connection
    if not _db_connection.test_connection():
        raise Exception("Failed to establish database connection")

def close_database():
    """Close global database connection"""
    global _db_connection
    if _db_connection:
        _db_connection.close()
        _db_connection = None