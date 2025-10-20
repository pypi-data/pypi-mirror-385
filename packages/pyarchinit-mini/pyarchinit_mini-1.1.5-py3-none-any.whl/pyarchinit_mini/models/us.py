"""
Stratigraphic Unit (US) model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class US(BaseModel):
    """
    Stratigraphic Unit model
    Adapted from PyArchInit US entity with key fields
    """
    __tablename__ = 'us_table'
    
    # Primary key and identification
    id_us = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    area = Column(String(20))
    us = Column(Integer, nullable=False)
    
    # Basic stratigraphic information
    d_stratigrafica = Column(String(350))
    d_interpretativa = Column(String(350))
    descrizione = Column(Text)
    interpretazione = Column(Text)
    
    # Chronological data
    periodo_iniziale = Column(String(300))
    fase_iniziale = Column(String(300))
    periodo_finale = Column(String(300))
    fase_finale = Column(String(300))
    
    # Excavation data
    scavato = Column(String(20))
    attivita = Column(String(30))
    anno_scavo = Column(Integer)
    metodo_di_scavo = Column(String(20))
    data_schedatura = Column(Date)
    schedatore = Column(String(100))
    
    # Physical characteristics
    formazione = Column(String(20))
    stato_di_conservazione = Column(String(20))
    colore = Column(String(20))
    consistenza = Column(String(20))
    struttura = Column(String(30))
    
    # Documentation and relationships
    inclusi = Column(Text)
    campioni = Column(Text)
    rapporti = Column(Text)
    documentazione = Column(Text)
    cont_per = Column(Text)
    order_layer = Column(Integer)
    
    # USM specific fields (Unità Stratigrafiche Murarie)
    unita_tipo = Column(String(200))
    settore = Column(String(200))
    quad_par = Column(String(200))
    ambient = Column(String(200))
    saggio = Column(String(200))
    
    # Additional ICCD alignment fields
    n_catalogo_generale = Column(String(25))
    n_catalogo_interno = Column(String(25))
    n_catalogo_internazionale = Column(String(25))
    soprintendenza = Column(String(200))
    
    # Measurements
    quota_relativa = Column(Float)
    quota_abs = Column(Float)
    lunghezza_max = Column(Float)
    altezza_max = Column(Float)
    altezza_min = Column(Float)
    profondita_max = Column(Float)
    profondita_min = Column(Float)
    larghezza_media = Column(Float)
    
    # Additional data
    osservazioni = Column(Text)
    datazione = Column(String(100))
    flottazione = Column(String(5))
    setacciatura = Column(String(5))
    affidabilita = Column(String(5))
    direttore_us = Column(String(100))
    responsabile_us = Column(String(100))
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito], 
                           primaryjoin="US.sito == Site.sito")
    
    def __repr__(self):
        return f"<US(id={self.id_us}, sito='{self.sito}', area='{self.area}', us={self.us})>"
    
    @property
    def display_name(self):
        """Human readable identifier for the US"""
        return f"US {self.us} - Area {self.area} ({self.sito})"
    
    @property
    def full_identifier(self):
        """Complete identifier: Site.Area.US"""
        return f"{self.sito}.{self.area}.{self.us}"