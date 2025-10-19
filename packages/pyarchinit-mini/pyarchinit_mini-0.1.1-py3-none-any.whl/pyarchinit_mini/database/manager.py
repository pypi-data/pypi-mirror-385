"""
Main database manager for PyArchInit-Mini
"""

from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, asc, desc, func, text

from .connection import DatabaseConnection
from .migrations import DatabaseMigrations
from ..models.base import BaseModel
from ..exceptions import DatabaseError, ValidationError

class RecordNotFoundError(DatabaseError):
    """Record not found error"""
    pass

T = TypeVar('T', bound=BaseModel)

class DatabaseManager:
    """
    High-level database manager providing CRUD operations
    and query functionality for PyArchInit-Mini models
    """
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.migrations = DatabaseMigrations(self)
        
    def run_migrations(self):
        """Run all necessary database migrations"""
        try:
            return self.migrations.migrate_all_tables()
        except Exception as e:
            raise DatabaseError(f"Migration failed: {e}")
    
    # Generic CRUD operations
    
    def create(self, model_class: Type[T], data: Dict[str, Any]) -> T:
        """Create a new record"""
        try:
            with self.connection.get_session() as session:
                instance = model_class(**data)
                session.add(instance)
                session.flush()  # Get the ID without committing
                session.refresh(instance)
                return instance
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create {model_class.__name__}: {e}")
    
    def get_by_id(self, model_class: Type[T], record_id: int) -> Optional[T]:
        """Get record by primary key"""
        try:
            with self.connection.get_session() as session:
                return session.query(model_class).get(record_id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {model_class.__name__} by ID: {e}")
    
    def get_by_field(self, model_class: Type[T], field_name: str, value: Any) -> Optional[T]:
        """Get record by specific field"""
        try:
            with self.connection.get_session() as session:
                return session.query(model_class).filter(
                    getattr(model_class, field_name) == value
                ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {model_class.__name__} by {field_name}: {e}")
    
    def get_all(self, model_class: Type[T], 
                offset: int = 0, limit: int = 100,
                order_by: Optional[str] = None,
                filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all records with optional filtering and pagination"""
        try:
            with self.connection.get_session() as session:
                query = session.query(model_class)
                
                # Apply filters
                if filters:
                    for field, value in filters.items():
                        if hasattr(model_class, field):
                            query = query.filter(getattr(model_class, field) == value)
                
                # Apply ordering
                if order_by:
                    if order_by.startswith('-'):
                        # Descending order
                        field_name = order_by[1:]
                        if hasattr(model_class, field_name):
                            query = query.order_by(desc(getattr(model_class, field_name)))
                    else:
                        # Ascending order
                        if hasattr(model_class, order_by):
                            query = query.order_by(asc(getattr(model_class, order_by)))
                
                # Apply pagination
                return query.offset(offset).limit(limit).all()
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {model_class.__name__} records: {e}")
    
    def update(self, model_class: Type[T], record_id: int, data: Dict[str, Any]) -> T:
        """Update existing record"""
        try:
            with self.connection.get_session() as session:
                instance = session.query(model_class).get(record_id)
                if not instance:
                    raise RecordNotFoundError(f"{model_class.__name__} with ID {record_id} not found")
                
                # Update fields
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                
                session.flush()
                session.refresh(instance)
                return instance
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update {model_class.__name__}: {e}")
    
    def delete(self, model_class: Type[T], record_id: int) -> bool:
        """Delete record by ID"""
        try:
            with self.connection.get_session() as session:
                instance = session.query(model_class).get(record_id)
                if not instance:
                    raise RecordNotFoundError(f"{model_class.__name__} with ID {record_id} not found")
                
                session.delete(instance)
                return True
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to delete {model_class.__name__}: {e}")
    
    def count(self, model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters"""
        try:
            with self.connection.get_session() as session:
                # Use count() on the model class directly
                query = session.query(model_class)
                
                # Apply filters
                if filters:
                    for field, value in filters.items():
                        if hasattr(model_class, field):
                            query = query.filter(getattr(model_class, field) == value)
                
                return query.count()
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to count {model_class.__name__} records: {e}")
    
    def search(self, model_class: Type[T], search_term: str, 
               search_fields: List[str]) -> List[T]:
        """Search records across multiple fields"""
        try:
            with self.connection.get_session() as session:
                # Build OR conditions for each search field
                conditions = []
                for field in search_fields:
                    if hasattr(model_class, field):
                        field_attr = getattr(model_class, field)
                        conditions.append(field_attr.ilike(f"%{search_term}%"))
                
                if not conditions:
                    return []
                
                return session.query(model_class).filter(or_(*conditions)).all()
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to search {model_class.__name__}: {e}")
    
    def bulk_create(self, model_class: Type[T], data_list: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records in a single transaction"""
        try:
            with self.connection.get_session() as session:
                instances = [model_class(**data) for data in data_list]
                session.add_all(instances)
                session.flush()
                for instance in instances:
                    session.refresh(instance)
                return instances
                
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to bulk create {model_class.__name__}: {e}")
    
    def execute_raw_query(self, query: str, params: Optional[Dict] = None):
        """Execute raw SQL query"""
        try:
            with self.connection.get_session() as session:
                return session.execute(text(query), params or {}).fetchall()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to execute query: {e}")
    
    # Transaction management
    
    def begin_transaction(self) -> Session:
        """Begin a manual transaction"""
        return self.connection.SessionLocal()
    
    def commit_transaction(self, session: Session):
        """Commit transaction"""
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Failed to commit transaction: {e}")
        finally:
            session.close()
    
    def rollback_transaction(self, session: Session):
        """Rollback transaction"""
        try:
            session.rollback()
        finally:
            session.close()
    
    # Utility methods
    
    def get_table_info(self, model_class: Type[T]) -> Dict[str, Any]:
        """Get table metadata information"""
        table = model_class.__table__
        return {
            'name': table.name,
            'columns': [{'name': col.name, 'type': str(col.type)} for col in table.columns],
            'primary_keys': [col.name for col in table.primary_key],
            'foreign_keys': [{'column': fk.parent.name, 'references': f"{fk.column.table.name}.{fk.column.name}"} 
                           for fk in table.foreign_keys]
        }