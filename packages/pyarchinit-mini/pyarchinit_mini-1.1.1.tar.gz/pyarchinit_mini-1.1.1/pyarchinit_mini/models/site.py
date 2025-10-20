"""
Site model for archaeological sites management
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import BaseModel

class Site(BaseModel):
    """
    Archaeological site model
    Adapted from PyArchInit SITE entity
    """
    __tablename__ = 'site_table'
    
    id_sito = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), nullable=False, unique=True)
    nazione = Column(String(250))
    regione = Column(String(250)) 
    comune = Column(String(250))
    provincia = Column(String(10))
    definizione_sito = Column(String(250))
    descrizione = Column(Text)
    sito_path = Column(String(500))
    find_check = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Site(id={self.id_sito}, nome='{self.sito}', comune='{self.comune}')>"
    
    @property
    def display_name(self):
        """Human readable name for the site"""
        return f"{self.sito} ({self.comune}, {self.provincia})"