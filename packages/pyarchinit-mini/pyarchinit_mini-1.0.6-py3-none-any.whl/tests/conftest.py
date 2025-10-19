"""
Test configuration and fixtures
"""

import pytest
import tempfile
import os
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService

@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        temp_db_path = temp_file.name
    
    # Create connection and tables
    db_conn = DatabaseConnection.sqlite(temp_db_path)
    db_conn.create_tables()
    
    yield db_conn
    
    # Cleanup
    db_conn.close()
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)

@pytest.fixture
def db_manager(temp_db):
    """Create database manager with test database"""
    return DatabaseManager(temp_db)

@pytest.fixture
def site_service(db_manager):
    """Create site service with test database"""
    return SiteService(db_manager)

@pytest.fixture
def us_service(db_manager):
    """Create US service with test database"""
    return USService(db_manager)

@pytest.fixture
def inventario_service(db_manager):
    """Create inventario service with test database"""
    return InventarioService(db_manager)

@pytest.fixture
def sample_site_data():
    """Sample site data for testing"""
    return {
        "sito": "Test Site",
        "nazione": "Italia",
        "regione": "Lazio",
        "comune": "Roma",
        "provincia": "RM",
        "definizione_sito": "Test excavation",
        "descrizione": "A test archaeological site"
    }

@pytest.fixture
def sample_us_data():
    """Sample US data for testing"""
    return {
        "sito": "Test Site",
        "area": "A",
        "us": 1001,
        "d_stratigrafica": "Test layer",
        "d_interpretativa": "Test interpretation",
        "descrizione": "Test US description",
        "anno_scavo": 2024
    }

@pytest.fixture
def sample_inventario_data():
    """Sample inventory data for testing"""
    return {
        "sito": "Test Site",
        "numero_inventario": 1,
        "tipo_reperto": "Ceramica",
        "definizione": "Vaso",
        "descrizione": "Test ceramic vessel",
        "area": "A",
        "us": 1001
    }