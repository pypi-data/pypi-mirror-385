"""
Material inventory model - Complete PyArchInit compatibility
"""

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel

class InventarioMateriali(BaseModel):
    """
    Material inventory model
    Complete implementation from PyArchInit INVENTARIO_MATERIALI entity
    """
    __tablename__ = 'inventario_materiali_table'
    
    # Primary key and identification
    id_invmat = Column(Integer, primary_key=True, autoincrement=True)
    sito = Column(Text, ForeignKey('site_table.sito', ondelete='CASCADE'), nullable=False)
    numero_inventario = Column(Integer, nullable=False)
    
    # Classification and description
    tipo_reperto = Column(Text)
    criterio_schedatura = Column(Text)
    definizione = Column(Text)
    descrizione = Column(Text)
    
    # Context information
    area = Column(Text)
    us = Column(Text)  # Changed to Text as per original schema
    
    # Physical state and processing
    lavato = Column(String(3))  # Changed to String(3) as per original
    nr_cassa = Column(Text)
    luogo_conservazione = Column(Text)
    stato_conservazione = Column(String(200))
    
    # Dating and documentation
    datazione_reperto = Column(String(200))
    elementi_reperto = Column(Text)
    misurazioni = Column(Text)
    rif_biblio = Column(Text)
    
    # Technical characteristics
    tecnologie = Column(Text)
    forme_minime = Column(Integer)
    forme_massime = Column(Integer)
    totale_frammenti = Column(Integer)
    
    # Ceramic specific fields
    corpo_ceramico = Column(String(200))
    rivestimento = Column(String(200))
    diametro_orlo = Column(Numeric(7, 3))  # Changed to Numeric as per original
    peso = Column(Numeric(9, 3))  # Changed to Numeric as per original
    tipo = Column(String(200))
    eve_orlo = Column(Numeric(7, 3))  # Changed to Numeric as per original
    
    # Classification flags
    repertato = Column(String(3))  # Changed to String(3) as per original
    diagnostico = Column(String(3))  # Changed to String(3) as per original
    
    # Additional identification and context
    n_reperto = Column(Integer)
    tipo_contenitore = Column(String(200))
    struttura = Column(String(200))
    years = Column(Integer)
    
    # Additional fields from original PyArchInit schema
    schedatore = Column(Text)  # Who catalogued the item
    date_scheda = Column(Text)  # Date of cataloguing
    punto_rinv = Column(Text)  # Find point/location
    negativo_photo = Column(Text)  # Photo negative reference
    diapositiva = Column(Text)  # Slide reference
    
    # Relationships
    site_ref = relationship("Site", foreign_keys=[sito], 
                           primaryjoin="InventarioMateriali.sito == Site.sito")
    
    # Note: US relationship would need proper foreign key setup
    # us_ref = relationship("US", foreign_keys=[sito, area, us])
    
    def __repr__(self):
        return f"<InventarioMateriali(id={self.id_invmat}, sito='{self.sito}', " \
               f"numero={self.numero_inventario}, tipo='{self.tipo_reperto}')>"
    
    @property
    def display_name(self):
        """Human readable identifier"""
        return f"Inv. {self.numero_inventario} - {self.tipo_reperto} ({self.sito})"
    
    @property
    def context_info(self):
        """Context information as string"""
        context_parts = []
        if self.area:
            context_parts.append(f"Area {self.area}")
        if self.us:
            context_parts.append(f"US {self.us}")
        return " - ".join(context_parts) if context_parts else "Nessun contesto"