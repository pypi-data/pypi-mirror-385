"""
Database migrations for PyArchInit-Mini
"""

import logging
from sqlalchemy import text, inspect
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseMigrations:
    """
    Handle database schema migrations
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection = db_manager.connection
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        try:
            inspector = inspect(self.connection.engine)
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
        except Exception as e:
            logger.error(f"Error checking column {column_name} in table {table_name}: {e}")
            return False
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value: str = None):
        """Add a column to a table if it doesn't exist"""
        try:
            if not self.check_column_exists(table_name, column_name):
                with self.connection.get_session() as session:
                    # Build ALTER TABLE statement
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    if default_value is not None:
                        alter_sql += f" DEFAULT {default_value}"
                    
                    session.execute(text(alter_sql))
                    session.commit()
                    logger.info(f"Added column {column_name} to table {table_name}")
                    return True
            else:
                logger.info(f"Column {column_name} already exists in table {table_name}")
                return False
        except Exception as e:
            logger.error(f"Error adding column {column_name} to table {table_name}: {e}")
            raise
    
    def migrate_inventario_materiali_table(self):
        """Migrate inventario_materiali_table to include all new fields"""
        try:
            logger.info("Starting migration for inventario_materiali_table...")
            
            # List of new columns to add
            new_columns = [
                ('schedatore', 'TEXT'),
                ('date_scheda', 'TEXT'),
                ('punto_rinv', 'TEXT'),
                ('negativo_photo', 'TEXT'),
                ('diapositiva', 'TEXT')
            ]
            
            migrations_applied = 0
            
            for column_name, column_type in new_columns:
                if self.add_column_if_not_exists('inventario_materiali_table', column_name, column_type):
                    migrations_applied += 1
            
            logger.info(f"Migration completed. {migrations_applied} new columns added to inventario_materiali_table")
            return migrations_applied
            
        except Exception as e:
            logger.error(f"Error during inventario_materiali_table migration: {e}")
            raise
    
    def migrate_all_tables(self):
        """Run all necessary migrations"""
        try:
            logger.info("Starting database migrations...")
            
            total_migrations = 0
            
            # Migrate inventario_materiali_table
            total_migrations += self.migrate_inventario_materiali_table()
            
            # Add other table migrations here as needed
            
            logger.info(f"All migrations completed. Total migrations applied: {total_migrations}")
            return total_migrations
            
        except Exception as e:
            logger.error(f"Error during database migrations: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure"""
        try:
            inspector = inspect(self.connection.engine)
            
            # Check if table exists
            if not inspector.has_table(table_name):
                return {'exists': False}
            
            # Get columns info
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            return {
                'exists': True,
                'columns': columns,
                'column_names': column_names,
                'column_count': len(columns)
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {'exists': False, 'error': str(e)}
    
    def check_migration_needed(self, table_name: str, required_columns: List[str]) -> List[str]:
        """Check which columns are missing from a table"""
        try:
            table_info = self.get_table_info(table_name)
            
            if not table_info['exists']:
                return required_columns  # All columns are missing if table doesn't exist
            
            existing_columns = table_info['column_names']
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            return missing_columns
            
        except Exception as e:
            logger.error(f"Error checking migration for {table_name}: {e}")
            return required_columns