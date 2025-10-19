"""
Media service - Business logic for media file management
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import asc, desc, or_
from ..database.manager import DatabaseManager
from ..models.media import Media, MediaThumb, Documentation
from ..media_manager.media_handler import MediaHandler
from ..utils.validators import validate_data
from ..utils.exceptions import ValidationError, RecordNotFoundError
import os
from pathlib import Path

class MediaService:
    """Service class for media operations"""
    
    def __init__(self, db_manager: DatabaseManager, media_handler: Optional[MediaHandler] = None):
        self.db_manager = db_manager
        self.media_handler = media_handler or MediaHandler()
    
    def create_media_record(self, media_data: Dict[str, Any]) -> Media:
        """Create a new media record in database"""
        # Validate data
        validate_data('media', media_data)
        
        # Check if file exists
        if 'media_path' in media_data and not os.path.exists(media_data['media_path']):
            raise ValidationError(f"Media file not found: {media_data['media_path']}")
        
        # Create media record
        return self.db_manager.create(Media, media_data)
    
    def store_and_register_media(self, file_path: str, entity_type: str, entity_id: int,
                                description: str = "", tags: str = "", author: str = "",
                                is_primary: bool = False) -> Media:
        """Store media file and register in database"""
        
        # Store file using media handler
        metadata = self.media_handler.store_file(
            file_path, entity_type, entity_id, description, tags, author
        )
        
        # Add database-specific fields
        metadata.update({
            'is_primary': is_primary,
            'is_public': True
        })
        
        # Create database record
        return self.create_media_record(metadata)
    
    def get_media_by_id(self, media_id: int) -> Optional[Media]:
        """Get media by ID"""
        return self.db_manager.get_by_id(Media, media_id)
    
    def get_all_media(self, page: int = 1, size: int = 10,
                     filters: Optional[Dict[str, Any]] = None) -> List[Media]:
        """Get all media with pagination and filtering"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Media)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Media, key):
                            query = query.filter(getattr(Media, key) == value)
                
                # Apply ordering (primary first, then by creation date)
                query = query.order_by(desc(Media.is_primary), desc(Media.id_media))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Media records: {e}")
    
    def get_media_by_entity(self, entity_type: str, entity_id: int, 
                           page: int = 1, size: int = 10) -> List[Media]:
        """Get all media for a specific entity"""
        filters = {'entity_type': entity_type, 'entity_id': entity_id}
        return self.get_all_media(page=page, size=size, filters=filters)
    
    def get_media_by_type(self, media_type: str, page: int = 1, size: int = 10) -> List[Media]:
        """Get all media of a specific type"""
        filters = {'media_type': media_type}
        return self.get_all_media(page=page, size=size, filters=filters)
    
    def search_media(self, search_term: str, page: int = 1, size: int = 10) -> List[Media]:
        """Search media by term"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Media)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        Media.media_name.contains(search_term),
                        Media.description.contains(search_term),
                        Media.tags.contains(search_term),
                        Media.author.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply ordering
                query = query.order_by(desc(Media.is_primary), desc(Media.id_media))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search Media records: {e}")
    
    def update_media(self, media_id: int, update_data: Dict[str, Any]) -> Media:
        """Update existing media"""
        # Validate update data
        if update_data:
            validate_data('media', update_data)
        
        # Update media
        return self.db_manager.update(Media, media_id, update_data)
    
    def delete_media(self, media_id: int, delete_file: bool = True) -> bool:
        """Delete media record and optionally the file"""
        try:
            # Get media record
            media = self.get_media_by_id(media_id)
            if not media:
                raise RecordNotFoundError(f"Media with ID {media_id} not found")
            
            # Delete file if requested
            if delete_file and media.media_path and os.path.exists(media.media_path):
                # Use media handler to delete file and thumbnails
                success = self.media_handler.delete_file(
                    media.media_filename, media.entity_type, media.entity_id
                )
                if not success:
                    # If media handler fails, try direct deletion
                    try:
                        os.remove(media.media_path)
                        # Also try to remove thumbnails if they exist
                        if media.thumbnail_path and os.path.exists(media.thumbnail_path):
                            os.remove(media.thumbnail_path)
                    except Exception:
                        pass  # Continue with database deletion even if file deletion fails
            
            # Delete database record
            return self.db_manager.delete(Media, media_id)
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to delete media: {e}")
    
    def count_media(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count media with optional filters"""
        return self.db_manager.count(Media, filters)
    
    def set_primary_media(self, media_id: int, entity_type: str, entity_id: int) -> bool:
        """Set media as primary for an entity"""
        try:
            with self.db_manager.connection.get_session() as session:
                # First, unset any existing primary media for this entity
                session.query(Media).filter(
                    Media.entity_type == entity_type,
                    Media.entity_id == entity_id,
                    Media.is_primary == True
                ).update({Media.is_primary: False})
                
                # Set the selected media as primary
                session.query(Media).filter(
                    Media.id_media == media_id
                ).update({Media.is_primary: True})
                
                session.commit()
                return True
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to set primary media: {e}")
    
    def get_primary_media(self, entity_type: str, entity_id: int) -> Optional[Media]:
        """Get primary media for an entity"""
        try:
            with self.db_manager.connection.get_session() as session:
                return session.query(Media).filter(
                    Media.entity_type == entity_type,
                    Media.entity_id == entity_id,
                    Media.is_primary == True
                ).first()
                
        except Exception as e:
            return None
    
    def get_media_statistics(self) -> Dict[str, Any]:
        """Get media statistics"""
        try:
            # Total counts
            total_media = self.count_media()
            
            # Count by type
            type_counts = {}
            for media_type in ['image', 'document', 'video', 'audio']:
                count = self.count_media({'media_type': media_type})
                type_counts[media_type] = count
            
            # Count by entity type
            entity_counts = {}
            for entity_type in ['site', 'us', 'inventario']:
                count = self.count_media({'entity_type': entity_type})
                entity_counts[entity_type] = count
            
            # Get all media to calculate storage stats
            all_media = self.get_all_media(size=10000)
            total_size = sum(media.file_size or 0 for media in all_media)
            
            # Count public/private
            public_count = self.count_media({'is_public': True})
            private_count = total_media - public_count
            
            # Authors
            authors = set()
            for media in all_media:
                if media.author:
                    authors.add(media.author)
            
            return {
                'total_media': total_media,
                'type_distribution': type_counts,
                'entity_distribution': entity_counts,
                'total_storage_bytes': total_size,
                'total_storage_mb': round(total_size / (1024 * 1024), 2),
                'public_count': public_count,
                'private_count': private_count,
                'unique_authors': len(authors),
                'average_file_size_mb': round((total_size / total_media) / (1024 * 1024), 2) if total_media > 0 else 0
            }
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get media statistics: {e}")
    
    def get_media_by_site_summary(self, site_name: str) -> Dict[str, Any]:
        """Get media summary for a site"""
        try:
            # Get all media for entities in this site
            site_media = []
            
            # Site media
            site_media.extend(self.get_media_by_entity('site', site_name, size=1000))
            
            # TODO: Get US media for this site (need US IDs)
            # TODO: Get inventory media for this site (need inventory IDs)
            
            # Analyze media
            total_count = len(site_media)
            type_counts = {}
            total_size = 0
            primary_media = []
            
            for media in site_media:
                # Count by type
                media_type = media.media_type or 'unknown'
                type_counts[media_type] = type_counts.get(media_type, 0) + 1
                
                # Add to total size
                total_size += media.file_size or 0
                
                # Collect primary media
                if media.is_primary:
                    primary_media.append(media)
            
            return {
                'site': site_name,
                'total_media': total_count,
                'type_distribution': type_counts,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'primary_media_count': len(primary_media),
                'has_documentation': type_counts.get('document', 0) > 0,
                'has_images': type_counts.get('image', 0) > 0,
                'has_videos': type_counts.get('video', 0) > 0
            }
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get site media summary: {e}")
    
    def create_media_collection(self, collection_name: str, entity_type: str, 
                               entity_id: int, media_ids: List[int]) -> Dict[str, Any]:
        """Create a media collection (virtual grouping)"""
        try:
            # This could be implemented as a separate Collection model
            # For now, we'll return a simple collection structure
            
            media_items = []
            for media_id in media_ids:
                media = self.get_media_by_id(media_id)
                if media:
                    media_items.append({
                        'id': media.id_media,
                        'name': media.media_name,
                        'type': media.media_type,
                        'path': media.media_path,
                        'thumbnail': media.thumbnail_path
                    })
            
            collection = {
                'name': collection_name,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'media_count': len(media_items),
                'media_items': media_items,
                'created_date': None  # Would be set when saved to DB
            }
            
            return collection
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to create media collection: {e}")
    
    def export_media_archive(self, entity_type: str, entity_id: int, 
                           archive_path: str, include_metadata: bool = True) -> bool:
        """Export media archive for an entity"""
        try:
            # Use media handler to create archive
            success = self.media_handler.create_media_archive(entity_type, entity_id, archive_path)
            
            if success and include_metadata:
                # Add metadata file to archive
                import zipfile
                import json
                
                # Get media metadata
                media_list = self.get_media_by_entity(entity_type, entity_id, size=1000)
                metadata = {
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'export_date': None,  # Would be set to current date
                    'media_count': len(media_list),
                    'media_items': []
                }
                
                for media in media_list:
                    metadata['media_items'].append({
                        'id': media.id_media,
                        'name': media.media_name,
                        'filename': media.media_filename,
                        'type': media.media_type,
                        'description': media.description,
                        'tags': media.tags,
                        'author': media.author,
                        'file_size': media.file_size,
                        'is_primary': media.is_primary
                    })
                
                # Add metadata to archive
                with zipfile.ZipFile(archive_path, 'a') as zipf:
                    zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            return success
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to export media archive: {e}")

class DocumentationService:
    """Service class for documentation operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_documentation(self, doc_data: Dict[str, Any]) -> Documentation:
        """Create a new documentation record"""
        # Validate data
        validate_data('documentation', doc_data)
        
        # Create documentation
        return self.db_manager.create(Documentation, doc_data)
    
    def get_documentation_by_id(self, doc_id: int) -> Optional[Documentation]:
        """Get documentation by ID"""
        return self.db_manager.get_by_id(Documentation, doc_id)
    
    def get_documentation_by_entity(self, entity_type: str, entity_id: int, 
                                   page: int = 1, size: int = 10) -> List[Documentation]:
        """Get all documentation for a specific entity"""
        filters = {'entity_type': entity_type, 'entity_id': entity_id}
        return self.get_all_documentation(page=page, size=size, filters=filters)
    
    def get_all_documentation(self, page: int = 1, size: int = 10,
                             filters: Optional[Dict[str, Any]] = None) -> List[Documentation]:
        """Get all documentation with pagination and filtering"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Documentation)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Documentation, key):
                            query = query.filter(getattr(Documentation, key) == value)
                
                # Apply ordering (final versions first, then by creation date)
                query = query.order_by(desc(Documentation.is_final), desc(Documentation.date_created))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Documentation records: {e}")
    
    def update_documentation(self, doc_id: int, update_data: Dict[str, Any]) -> Documentation:
        """Update existing documentation"""
        # Validate update data
        if update_data:
            validate_data('documentation', update_data)
        
        return self.db_manager.update(Documentation, doc_id, update_data)
    
    def delete_documentation(self, doc_id: int, delete_file: bool = True) -> bool:
        """Delete documentation record and optionally the file"""
        try:
            # Get documentation record
            doc = self.get_documentation_by_id(doc_id)
            if not doc:
                raise RecordNotFoundError(f"Documentation with ID {doc_id} not found")
            
            # Delete file if requested
            if delete_file and doc.file_path and os.path.exists(doc.file_path):
                try:
                    os.remove(doc.file_path)
                except Exception:
                    pass  # Continue with database deletion even if file deletion fails
            
            # Delete database record
            return self.db_manager.delete(Documentation, doc_id)
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to delete documentation: {e}")
    
    def count_documentation(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documentation with optional filters"""
        return self.db_manager.count(Documentation, filters)