"""
Site Data Transfer Object
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SiteDTO:
    """
    Data Transfer Object for Site data
    This class holds site data without SQLAlchemy session dependencies
    """
    id_sito: int
    sito: str
    nazione: Optional[str] = None
    regione: Optional[str] = None
    comune: Optional[str] = None
    provincia: Optional[str] = None
    definizione_sito: Optional[str] = None
    descrizione: Optional[str] = None
    sito_path: Optional[str] = None
    find_check: Optional[bool] = False
    
    @classmethod
    def from_model(cls, site_model) -> 'SiteDTO':
        """Create DTO from SQLAlchemy model instance"""
        return cls(
            id_sito=site_model.id_sito,
            sito=site_model.sito,
            nazione=site_model.nazione,
            regione=site_model.regione,
            comune=site_model.comune,
            provincia=site_model.provincia,
            definizione_sito=site_model.definizione_sito,
            descrizione=site_model.descrizione,
            sito_path=site_model.sito_path,
            find_check=site_model.find_check
        )
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id_sito': self.id_sito,
            'sito': self.sito,
            'nazione': self.nazione,
            'regione': self.regione,
            'comune': self.comune,
            'provincia': self.provincia,
            'definizione_sito': self.definizione_sito,
            'descrizione': self.descrizione,
            'sito_path': self.sito_path,
            'find_check': self.find_check
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for the site"""
        if self.comune:
            return f"{self.sito} ({self.comune})"
        return self.sito