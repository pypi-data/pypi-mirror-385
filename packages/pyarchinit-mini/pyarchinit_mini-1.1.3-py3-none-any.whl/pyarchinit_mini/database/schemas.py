"""
Database schema utilities for PyArchInit-Mini
"""

from typing import Dict, List, Any
from sqlalchemy import text
from .connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """
    Utilities for database schema management and migrations
    """
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
    
    def create_all_tables(self):
        """Create all tables defined in models"""
        self.connection.create_tables()
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            with self.connection.get_session() as session:
                if self.connection.connection_string.startswith('sqlite'):
                    query = text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name")
                else:  # PostgreSQL
                    query = text("SELECT tablename FROM pg_tables WHERE tablename=:table_name")
                
                result = session.execute(query, {'table_name': table_name}).fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def get_table_list(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            with self.connection.get_session() as session:
                if self.connection.connection_string.startswith('sqlite'):
                    query = text("SELECT name FROM sqlite_master WHERE type='table'")
                else:  # PostgreSQL
                    query = text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                
                result = session.execute(query).fetchall()
                return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table"""
        try:
            with self.connection.get_session() as session:
                if self.connection.connection_string.startswith('sqlite'):
                    query = text(f"PRAGMA table_info({table_name})")
                    result = session.execute(query).fetchall()
                    return [
                        {
                            'name': row[1],
                            'type': row[2],
                            'nullable': not bool(row[3]),
                            'default': row[4],
                            'primary_key': bool(row[5])
                        }
                        for row in result
                    ]
                else:  # PostgreSQL
                    query = text("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """)
                    result = session.execute(query, {'table_name': table_name}).fetchall()
                    return [
                        {
                            'name': row[0],
                            'type': row[1],
                            'nullable': row[2] == 'YES',
                            'default': row[3],
                            'primary_key': False  # Would need additional query for PK info
                        }
                        for row in result
                    ]
        except Exception as e:
            logger.error(f"Error getting table columns: {e}")
            return []
    
    def create_indexes(self):
        """Create recommended indexes for performance"""
        indexes = [
            # Site table indexes
            "CREATE INDEX IF NOT EXISTS idx_site_sito ON site_table(sito)",
            "CREATE INDEX IF NOT EXISTS idx_site_comune ON site_table(comune)",
            
            # US table indexes
            "CREATE INDEX IF NOT EXISTS idx_us_sito ON us_table(sito)",
            "CREATE INDEX IF NOT EXISTS idx_us_area ON us_table(area)",
            "CREATE INDEX IF NOT EXISTS idx_us_numero ON us_table(us)",
            "CREATE INDEX IF NOT EXISTS idx_us_sito_area_us ON us_table(sito, area, us)",
            
            # Inventario materiali indexes
            "CREATE INDEX IF NOT EXISTS idx_invmat_sito ON inventario_materiali_table(sito)",
            "CREATE INDEX IF NOT EXISTS idx_invmat_numero ON inventario_materiali_table(numero_inventario)",
            "CREATE INDEX IF NOT EXISTS idx_invmat_tipo ON inventario_materiali_table(tipo_reperto)",
            "CREATE INDEX IF NOT EXISTS idx_invmat_sito_us ON inventario_materiali_table(sito, area, us)",
        ]
        
        try:
            with self.connection.get_session() as session:
                for index_sql in indexes:
                    try:
                        session.execute(text(index_sql))
                        logger.debug(f"Created index: {index_sql}")
                    except Exception as e:
                        logger.warning(f"Failed to create index: {index_sql}, Error: {e}")
                session.commit()
                logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def check_schema_compatibility(self) -> Dict[str, Any]:
        """Check if current database schema is compatible with models"""
        required_tables = ['site_table', 'us_table', 'inventario_materiali_table']
        existing_tables = self.get_table_list()
        
        compatibility_report = {
            'compatible': True,
            'missing_tables': [],
            'existing_tables': existing_tables,
            'warnings': []
        }
        
        # Check required tables
        for table in required_tables:
            if table not in existing_tables:
                compatibility_report['missing_tables'].append(table)
                compatibility_report['compatible'] = False
        
        # Additional checks could be added here for column compatibility
        
        return compatibility_report
    
    def backup_schema(self) -> str:
        """Generate SQL script to backup current schema structure"""
        # This would be implemented differently for SQLite vs PostgreSQL
        # For now, return a placeholder
        return "-- Schema backup not implemented yet"
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'database_type': 'SQLite' if self.connection.connection_string.startswith('sqlite') else 'PostgreSQL',
            'tables': {},
            'total_records': 0
        }
        
        try:
            with self.connection.get_session() as session:
                for table in self.get_table_list():
                    if not table.startswith('sqlite_'):  # Skip SQLite system tables
                        try:
                            count_query = text(f"SELECT COUNT(*) FROM {table}")
                            count = session.execute(count_query).scalar()
                            stats['tables'][table] = count
                            stats['total_records'] += count
                        except Exception as e:
                            logger.warning(f"Could not get count for table {table}: {e}")
                            stats['tables'][table] = 'Error'
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
        
        return stats