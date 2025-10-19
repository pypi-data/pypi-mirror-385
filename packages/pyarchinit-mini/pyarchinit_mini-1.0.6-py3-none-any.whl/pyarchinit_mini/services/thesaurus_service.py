"""
Thesaurus service for managing controlled vocabularies
"""

from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from ..models.thesaurus import ThesaurusSigle, ThesaurusField, ThesaurusCategory, THESAURUS_MAPPINGS
from ..database.manager import DatabaseManager
from ..exceptions import DatabaseError, ValidationError

logger = logging.getLogger(__name__)

class ThesaurusService:
    """
    Service for managing thesaurus and controlled vocabularies
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_field_values(self, table_name: str, field_name: str, 
                        language: str = 'it') -> List[Dict[str, Any]]:
        """
        Get vocabulary values for a specific field
        
        Args:
            table_name: Database table name
            field_name: Field name
            language: Language code
            
        Returns:
            List of vocabulary entries
        """
        try:
            with self.db_manager.connection.get_session() as session:
                # First try to get from ThesaurusField
                field_entries = session.query(ThesaurusField).filter(
                    and_(
                        ThesaurusField.table_name == table_name,
                        ThesaurusField.field_name == field_name,
                        ThesaurusField.language == language,
                        ThesaurusField.active == '1'
                    )
                ).order_by(ThesaurusField.sort_order, ThesaurusField.value).all()
                
                if field_entries:
                    return [
                        {
                            'id': entry.id_field,
                            'value': entry.value,
                            'label': entry.label or entry.value,
                            'description': entry.description,
                            'parent_id': entry.parent_id
                        }
                        for entry in field_entries
                    ]
                
                # Fallback to ThesaurusSigle
                sigle_entries = session.query(ThesaurusSigle).filter(
                    and_(
                        ThesaurusSigle.nome_tabella == table_name,
                        ThesaurusSigle.tipologia_sigla == field_name,
                        ThesaurusSigle.lingua == language
                    )
                ).order_by(ThesaurusSigle.sigla).all()
                
                if sigle_entries:
                    return [
                        {
                            'id': entry.id_thesaurus_sigle,
                            'value': entry.sigla,
                            'label': entry.sigla_estesa or entry.sigla,
                            'description': entry.descrizione
                        }
                        for entry in sigle_entries
                    ]
                
                # Fallback to predefined mappings
                if table_name in THESAURUS_MAPPINGS and field_name in THESAURUS_MAPPINGS[table_name]:
                    values = THESAURUS_MAPPINGS[table_name][field_name]
                    return [
                        {
                            'id': f'predefined_{i}',
                            'value': value,
                            'label': value,
                            'description': None
                        }
                        for i, value in enumerate(values)
                    ]
                
                return []
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting field values: {e}")
            raise DatabaseError(f"Failed to get field values: {e}")
    
    def add_field_value(self, table_name: str, field_name: str, value: str,
                       label: Optional[str] = None, description: Optional[str] = None,
                       language: str = 'it') -> Dict[str, Any]:
        """
        Add a new vocabulary value for a field
        
        Args:
            table_name: Database table name
            field_name: Field name
            value: The vocabulary value
            label: Human-readable label
            description: Description
            language: Language code
            
        Returns:
            Created entry data
        """
        try:
            with self.db_manager.connection.get_session() as session:
                # Check if value already exists
                existing = session.query(ThesaurusField).filter(
                    and_(
                        ThesaurusField.table_name == table_name,
                        ThesaurusField.field_name == field_name,
                        ThesaurusField.value == value,
                        ThesaurusField.language == language
                    )
                ).first()
                
                if existing:
                    raise ValidationError(f"Value '{value}' already exists for {table_name}.{field_name}")
                
                # Create new entry
                new_entry = ThesaurusField(
                    table_name=table_name,
                    field_name=field_name,
                    value=value,
                    label=label,
                    description=description,
                    language=language,
                    active='1'
                )
                
                session.add(new_entry)
                session.commit()
                
                return {
                    'id': new_entry.id_field,
                    'value': new_entry.value,
                    'label': new_entry.label or new_entry.value,
                    'description': new_entry.description
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database error adding field value: {e}")
            raise DatabaseError(f"Failed to add field value: {e}")
    
    def update_field_value(self, field_id: int, value: Optional[str] = None,
                          label: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing vocabulary value
        
        Args:
            field_id: Field entry ID
            value: New value
            label: New label
            description: New description
            
        Returns:
            Updated entry data
        """
        try:
            with self.db_manager.connection.get_session() as session:
                entry = session.query(ThesaurusField).filter(
                    ThesaurusField.id_field == field_id
                ).first()
                
                if not entry:
                    raise ValidationError(f"Field entry with ID {field_id} not found")
                
                if value is not None:
                    entry.value = value
                if label is not None:
                    entry.label = label
                if description is not None:
                    entry.description = description
                
                session.commit()
                
                return {
                    'id': entry.id_field,
                    'value': entry.value,
                    'label': entry.label or entry.value,
                    'description': entry.description
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database error updating field value: {e}")
            raise DatabaseError(f"Failed to update field value: {e}")
    
    def delete_field_value(self, field_id: int) -> bool:
        """
        Delete a vocabulary value
        
        Args:
            field_id: Field entry ID
            
        Returns:
            True if deleted successfully
        """
        try:
            with self.db_manager.connection.get_session() as session:
                entry = session.query(ThesaurusField).filter(
                    ThesaurusField.id_field == field_id
                ).first()
                
                if not entry:
                    raise ValidationError(f"Field entry with ID {field_id} not found")
                
                session.delete(entry)
                session.commit()
                
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting field value: {e}")
            raise DatabaseError(f"Failed to delete field value: {e}")
    
    def get_table_fields(self, table_name: str) -> List[str]:
        """
        Get list of fields that have thesaurus entries for a table
        
        Args:
            table_name: Database table name
            
        Returns:
            List of field names
        """
        try:
            with self.db_manager.connection.get_session() as session:
                # Get fields from ThesaurusField
                field_fields = session.query(ThesaurusField.field_name).filter(
                    ThesaurusField.table_name == table_name
                ).distinct().all()
                
                # Get fields from ThesaurusSigle
                sigle_fields = session.query(ThesaurusSigle.tipologia_sigla).filter(
                    ThesaurusSigle.nome_tabella == table_name
                ).distinct().all()
                
                # Combine and deduplicate
                all_fields = set()
                all_fields.update([f[0] for f in field_fields if f[0]])
                all_fields.update([f[0] for f in sigle_fields if f[0]])
                
                # Add predefined fields
                if table_name in THESAURUS_MAPPINGS:
                    all_fields.update(THESAURUS_MAPPINGS[table_name].keys())
                
                return sorted(list(all_fields))
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting table fields: {e}")
            raise DatabaseError(f"Failed to get table fields: {e}")
    
    def initialize_default_vocabularies(self) -> bool:
        """
        Initialize default vocabularies from predefined mappings
        
        Returns:
            True if initialized successfully
        """
        try:
            with self.db_manager.connection.get_session() as session:
                for table_name, fields in THESAURUS_MAPPINGS.items():
                    for field_name, values in fields.items():
                        for sort_order, value in enumerate(values):
                            # Check if entry already exists
                            existing = session.query(ThesaurusField).filter(
                                and_(
                                    ThesaurusField.table_name == table_name,
                                    ThesaurusField.field_name == field_name,
                                    ThesaurusField.value == value,
                                    ThesaurusField.language == 'it'
                                )
                            ).first()
                            
                            if not existing:
                                new_entry = ThesaurusField(
                                    table_name=table_name,
                                    field_name=field_name,
                                    value=value,
                                    label=value,
                                    language='it',
                                    sort_order=sort_order,
                                    active='1'
                                )
                                session.add(new_entry)
                
                session.commit()
                logger.info("Default vocabularies initialized successfully")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error initializing vocabularies: {e}")
            raise DatabaseError(f"Failed to initialize vocabularies: {e}")
    
    def search_values(self, query: str, table_name: Optional[str] = None,
                     field_name: Optional[str] = None, language: str = 'it') -> List[Dict[str, Any]]:
        """
        Search vocabulary values by query string
        
        Args:
            query: Search query
            table_name: Optional table filter
            field_name: Optional field filter
            language: Language code
            
        Returns:
            List of matching entries
        """
        try:
            with self.db_manager.connection.get_session() as session:
                # Search in ThesaurusField
                field_query = session.query(ThesaurusField).filter(
                    and_(
                        ThesaurusField.language == language,
                        ThesaurusField.active == '1',
                        or_(
                            ThesaurusField.value.ilike(f'%{query}%'),
                            ThesaurusField.label.ilike(f'%{query}%'),
                            ThesaurusField.description.ilike(f'%{query}%')
                        )
                    )
                )
                
                if table_name:
                    field_query = field_query.filter(ThesaurusField.table_name == table_name)
                if field_name:
                    field_query = field_query.filter(ThesaurusField.field_name == field_name)
                
                field_results = field_query.limit(50).all()
                
                return [
                    {
                        'id': entry.id_field,
                        'table_name': entry.table_name,
                        'field_name': entry.field_name,
                        'value': entry.value,
                        'label': entry.label or entry.value,
                        'description': entry.description,
                        'type': 'field'
                    }
                    for entry in field_results
                ]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error searching values: {e}")
            raise DatabaseError(f"Failed to search values: {e}")