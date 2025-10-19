"""
Harris Matrix models for stratigraphic relationships
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import BaseModel

class HarrisMatrix(BaseModel):
    """
    Harris Matrix relationships between stratigraphic units
    """
    __tablename__ = 'harris_matrix_table'
    
    id_matrix = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    area = Column(String(20))
    us_sopra = Column(Integer, nullable=False)  # US above
    us_sotto = Column(Integer, nullable=False)  # US below
    tipo_rapporto = Column(String(50))  # Type of relationship
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito])
    
    def __repr__(self):
        return f"<HarrisMatrix(sito='{self.sito}', {self.us_sopra} -> {self.us_sotto})>"

class USRelationships(BaseModel):
    """
    Detailed stratigraphic relationships between US
    """
    __tablename__ = 'us_relationships_table'
    
    id_relationship = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    us_from = Column(Integer, nullable=False)
    us_to = Column(Integer, nullable=False)
    relationship_type = Column(String(100))  # 'sopra', 'sotto', 'taglia', 'riempie', etc.
    description = Column(Text)
    certainty = Column(String(20))  # 'certa', 'probabile', 'dubbia'
    
    def __repr__(self):
        return f"<USRelationship({self.us_from} {self.relationship_type} {self.us_to})>"

class Period(BaseModel):
    """
    Archaeological periods and phases
    """
    __tablename__ = 'period_table'
    
    id_period = Column(Integer, primary_key=True, autoincrement=True)
    period_name = Column(String(200), nullable=False)
    phase_name = Column(String(200))
    start_date = Column(Integer)  # Anno inizio
    end_date = Column(Integer)    # Anno fine
    description = Column(Text)
    chronology = Column(String(100))  # Sistema cronologico
    
    def __repr__(self):
        return f"<Period('{self.period_name}', {self.start_date}-{self.end_date})>"

class Periodizzazione(BaseModel):
    """
    Periodization assignments for archaeological contexts
    Links US and other entities to chronological periods
    """
    __tablename__ = 'periodizzazione_table'
    
    id_periodizzazione = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(String(350), ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    area = Column(String(20))
    us = Column(Integer)
    
    # Period assignment
    periodo_iniziale = Column(String(200))  # Initial period
    fase_iniziale = Column(String(200))     # Initial phase
    periodo_finale = Column(String(200))    # Final period
    fase_finale = Column(String(200))       # Final phase
    
    # Dating precision
    datazione_estesa = Column(String(300))  # Extended dating description
    motivazione = Column(Text)              # Reasoning for dating
    
    # Relationships to formal periods
    period_id_initial = Column(Integer, ForeignKey('period_table.id_period'))
    period_id_final = Column(Integer, ForeignKey('period_table.id_period'))
    
    # Material culture associations
    cultura = Column(String(200))           # Cultural attribution
    datazione_radiocarbonica = Column(String(100))  # Radiocarbon dating
    
    # Confidence and notes
    affidabilita = Column(String(50))       # 'alta', 'media', 'bassa'
    note = Column(Text)
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito])
    initial_period = relationship("Period", foreign_keys=[period_id_initial])
    final_period = relationship("Period", foreign_keys=[period_id_final])
    
    def __repr__(self):
        return f"<Periodizzazione({self.sito} US{self.us}: {self.periodo_iniziale}-{self.periodo_finale})>"
    
    @property
    def dating_range(self) -> str:
        """Get formatted dating range"""
        if self.periodo_iniziale and self.periodo_finale:
            if self.periodo_iniziale == self.periodo_finale:
                return f"{self.periodo_iniziale}"
            else:
                return f"{self.periodo_iniziale} - {self.periodo_finale}"
        elif self.periodo_iniziale:
            return f"{self.periodo_iniziale}+"
        elif self.periodo_finale:
            return f"ante {self.periodo_finale}"
        else:
            return "Non datato"