"""
Database connection management for PyArchInit-Mini
"""

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Manages database connections for both PostgreSQL and SQLite
    """
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Initialize database engine and session factory"""
        try:
            # Create engine with appropriate settings
            if self.connection_string.startswith('sqlite'):
                # SQLite specific settings with foreign key support
                self.engine = create_engine(
                    self.connection_string,
                    echo=False,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    }
                )
                
                # Enable foreign key constraints for SQLite
                from sqlalchemy import event
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            else:
                # PostgreSQL specific settings
                self.engine = create_engine(
                    self.connection_string,
                    echo=False,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database connection established: {self._get_db_type()}")
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to establish database connection: {e}")
            raise
    
    def _get_db_type(self) -> str:
        """Get database type from connection string"""
        if self.connection_string.startswith('sqlite'):
            return 'SQLite'
        elif self.connection_string.startswith('postgresql'):
            return 'PostgreSQL'
        else:
            return 'Unknown'
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        Ensures proper session cleanup
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all tables from models"""
        from ..models.base import Base
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def initialize_database(self):
        """Initialize database and create tables with migrations"""
        try:
            # Create all tables
            self.create_tables()
            
            # Run migrations to add any missing columns
            from ..database.migrations import DatabaseMigrations
            from ..database.manager import DatabaseManager
            
            db_manager = DatabaseManager(self)
            migrations = DatabaseMigrations(db_manager)
            migrations_applied = migrations.migrate_all_tables()
            
            if migrations_applied > 0:
                logger.info(f"Applied {migrations_applied} database migrations")
            
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    @classmethod
    def from_url(cls, database_url: str) -> 'DatabaseConnection':
        """Create connection from database URL"""
        return cls(database_url)
    
    @classmethod
    def sqlite(cls, db_path: str) -> 'DatabaseConnection':
        """Create SQLite connection"""
        # Ensure directory exists if path contains directory
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        connection_string = f"sqlite:///{db_path}"
        return cls(connection_string)
    
    @classmethod
    def postgresql(cls, host: str, port: int, database: str, 
                   username: str, password: str) -> 'DatabaseConnection':
        """Create PostgreSQL connection"""
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        return cls(connection_string)