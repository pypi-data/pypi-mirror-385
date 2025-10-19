"""
Base model class for all PyArchInit-Mini models
"""

from datetime import datetime
from sqlalchemy import DateTime, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    """
    Base model class with common fields and methods
    """
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data):
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)