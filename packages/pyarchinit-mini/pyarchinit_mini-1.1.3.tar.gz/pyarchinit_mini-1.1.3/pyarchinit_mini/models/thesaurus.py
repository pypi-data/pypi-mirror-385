"""
Thesaurus model for controlled vocabularies
Based on PyArchInit thesaurus system
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel

class ThesaurusSigle(BaseModel):
    """
    Thesaurus for controlled vocabularies and abbreviations
    Based on pyarchinit_thesaurus_sigle table
    """
    __tablename__ = 'pyarchinit_thesaurus_sigle'
    
    # Primary key
    id_thesaurus_sigle = Column(Integer, primary_key=True, autoincrement=True)
    
    # Table reference
    nome_tabella = Column(Text, nullable=False)  # Which table this vocabulary applies to
    
    # Vocabulary entries
    sigla = Column(Text, nullable=False)  # Short code/abbreviation
    sigla_estesa = Column(Text)  # Extended form
    descrizione = Column(Text)  # Description
    
    # Classification
    tipologia_sigla = Column(Text)  # Type of abbreviation
    lingua = Column(String(2), default='it')  # Language code
    
    # Metadata
    fonte = Column(Text)  # Source reference
    note = Column(Text)  # Additional notes
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('nome_tabella', 'sigla', 'lingua', name='thesaurus_unique'),
    )
    
    def __repr__(self):
        return f"<ThesaurusSigle(id={self.id_thesaurus_sigle}, " \
               f"tabella='{self.nome_tabella}', sigla='{self.sigla}')>"
    
    @property
    def display_value(self):
        """Display value for UI"""
        if self.sigla_estesa:
            return f"{self.sigla} - {self.sigla_estesa}"
        return self.sigla

class ThesaurusField(BaseModel):
    """
    Field-specific thesaurus entries
    For detailed field vocabularies
    """
    __tablename__ = 'thesaurus_field'
    
    # Primary key
    id_field = Column(Integer, primary_key=True, autoincrement=True)
    
    # Field reference
    table_name = Column(Text, nullable=False)
    field_name = Column(Text, nullable=False)
    
    # Vocabulary entry
    value = Column(Text, nullable=False)
    label = Column(Text)  # Human-readable label
    description = Column(Text)
    
    # Hierarchy support
    parent_id = Column(Integer, ForeignKey('thesaurus_field.id_field'))
    sort_order = Column(Integer, default=0)
    
    # Status
    active = Column(String(1), default='1')  # 1=active, 0=inactive
    
    # Language support
    language = Column(String(2), default='it')
    
    # Relationships
    children = relationship("ThesaurusField", backref="parent", remote_side=[id_field])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('table_name', 'field_name', 'value', 'language', name='field_value_unique'),
    )
    
    def __repr__(self):
        return f"<ThesaurusField(table='{self.table_name}', " \
               f"field='{self.field_name}', value='{self.value}')>"
    
    @property
    def display_name(self):
        """Display name for UI"""
        return self.label if self.label else self.value

class ThesaurusCategory(BaseModel):
    """
    Categories for organizing thesaurus entries
    """
    __tablename__ = 'thesaurus_category'
    
    # Primary key
    id_category = Column(Integer, primary_key=True, autoincrement=True)
    
    # Category information
    category_name = Column(Text, nullable=False)
    category_code = Column(String(20))
    description = Column(Text)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey('thesaurus_category.id_category'))
    level = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    
    # Status
    active = Column(String(1), default='1')
    
    # Relationships
    children = relationship("ThesaurusCategory", backref="parent", remote_side=[id_category])
    
    def __repr__(self):
        return f"<ThesaurusCategory(id={self.id_category}, name='{self.category_name}')>"

# Predefined thesaurus mappings for common archaeological fields
THESAURUS_MAPPINGS = {
    'site_table': {
        'tipologia_sito': [
            'Abitato', 'Necropoli', 'Santuario', 'Insediamento', 'Villa', 
            'Castelliere', 'Fortezza', 'Ponte', 'Acquedotto', 'Teatro',
            'Anfiteatro', 'Foro', 'Basilica', 'Terme', 'Domus'
        ],
        'definizione_sito': [
            'Scavo stratigrafico', 'Ricognizione', 'Controllo archeologico',
            'Scavo d\'emergenza', 'Sondaggio', 'Prospezione geofisica'
        ],
        'periodo_iniziale': [
            'Paleolitico', 'Mesolitico', 'Neolitico', 'Eneolitico',
            'Età del Bronzo', 'Età del Ferro', 'Età Romana',
            'Tardoantico', 'Altomedioevo', 'Medioevo', 'Postmedioevo'
        ]
    },
    'us_table': {
        'tipo_us': [
            'Strato', 'Struttura', 'Interface', 'Riempimento', 'Deposito',
            'Taglio', 'Crollo', 'Livellamento', 'Preparazione', 'Pavimento'
        ],
        'formazione': [
            'Naturale', 'Antropica', 'Mista'
        ],
        'consistenza': [
            'Compatta', 'Semicompatta', 'Sciolsa', 'Molto sciolsa'
        ],
        'colore': [
            'Marrone', 'Marrone scuro', 'Marrone chiaro', 'Grigio',
            'Grigio scuro', 'Grigio chiaro', 'Nero', 'Giallo',
            'Rossastro', 'Biancastro'
        ]
    },
    'inventario_materiali_table': {
        'tipo_reperto': [
            'Ceramica', 'Metallo', 'Vetro', 'Osso', 'Pietra',
            'Legno', 'Tessuto', 'Plastica', 'Moneta', 'Laterizio'
        ],
        'stato_conservazione': [
            'Ottimo', 'Buono', 'Discreto', 'Cattivo', 'Pessimo',
            'Frammentario', 'Lacunoso', 'Integro'
        ],
        'corpo_ceramico': [
            'Depurato', 'Semi-depurato', 'Grezzo', 'Fine',
            'Medio-fine', 'Grossolano'
        ],
        'rivestimento': [
            'Verniciato', 'Ingobbato', 'Dipinto', 'Graffito',
            'Inciso', 'Impresso', 'Nudo'
        ]
    }
}