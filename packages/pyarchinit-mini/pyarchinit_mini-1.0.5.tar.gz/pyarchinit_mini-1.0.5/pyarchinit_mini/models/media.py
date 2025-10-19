"""
Media management models (images, documents, etc.)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import BaseModel

class Media(BaseModel):
    """
    Media files (images, documents, videos) linked to archaeological records
    """
    __tablename__ = 'media_table'
    
    id_media = Column(Integer, primary_key=True, autoincrement=True)
    
    # Entity linking
    entity_type = Column(String(50), nullable=False)  # 'site', 'us', 'inventario', etc.
    entity_id = Column(Integer, nullable=False)
    
    # Media information
    media_name = Column(String(300), nullable=False)
    media_filename = Column(String(500), nullable=False)
    media_path = Column(String(1000))
    media_type = Column(String(50))  # 'image', 'document', 'video', 'audio'
    mime_type = Column(String(100))
    file_size = Column(Integer)  # bytes
    
    # Metadata
    description = Column(Text)
    tags = Column(Text)  # JSON or comma-separated
    copyright_info = Column(String(500))
    author = Column(String(200))
    
    # Technical metadata
    width = Column(Integer)  # for images
    height = Column(Integer)  # for images
    duration = Column(Float)  # for videos/audio
    resolution = Column(String(50))
    
    # Status
    is_primary = Column(Boolean, default=False)  # Primary image for entity
    is_public = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Media('{self.media_name}', {self.entity_type}:{self.entity_id})>"
    
    @property
    def is_image(self):
        return self.media_type == 'image'
    
    @property
    def is_document(self):
        return self.media_type == 'document'

class MediaThumb(BaseModel):
    """
    Thumbnails for media files
    """
    __tablename__ = 'media_thumb_table'
    
    id_thumb = Column(Integer, primary_key=True, autoincrement=True)
    id_media = Column(Integer, ForeignKey('media_table.id_media'), nullable=False)
    
    thumb_path = Column(String(1000))
    thumb_data = Column(LargeBinary)  # Store small thumbnails directly in DB
    thumb_size = Column(String(20))   # 'small', 'medium', 'large'
    width = Column(Integer)
    height = Column(Integer)
    
    # Relationship
    media = relationship("Media", backref="thumbnails")
    
    def __repr__(self):
        return f"<MediaThumb(media_id={self.id_media}, size={self.thumb_size})>"

class Documentation(BaseModel):
    """
    Documentation files and reports
    """
    __tablename__ = 'documentation_table'
    
    id_doc = Column(Integer, primary_key=True, autoincrement=True)
    
    # Entity linking
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    
    # Document info
    doc_type = Column(String(100))  # 'report', 'analysis', 'photo_log', etc.
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # File info
    file_path = Column(String(1000))
    file_format = Column(String(20))  # 'pdf', 'doc', 'txt', etc.
    
    # Metadata
    author = Column(String(200))
    date_created = Column(DateTime)
    version = Column(String(20))
    language = Column(String(10))
    
    # Status
    is_final = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Documentation('{self.title}', {self.entity_type}:{self.entity_id})>"