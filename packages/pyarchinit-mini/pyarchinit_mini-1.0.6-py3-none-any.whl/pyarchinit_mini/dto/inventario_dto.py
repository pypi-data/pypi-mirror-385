"""
Inventario Data Transfer Object
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InventarioDTO:
    """
    Data Transfer Object for Inventario (Material Inventory) data
    This class holds inventory data without SQLAlchemy session dependencies
    """
    id_invmat: int
    sito: str
    numero_inventario: int
    tipo_reperto: Optional[str] = None
    definizione: Optional[str] = None
    descrizione: Optional[str] = None
    area: Optional[str] = None
    us: Optional[int] = None
    peso: Optional[float] = None
    
    @classmethod
    def from_model(cls, inventario_model) -> 'InventarioDTO':
        """Create DTO from SQLAlchemy model instance"""
        return cls(
            id_invmat=inventario_model.id_invmat,
            sito=inventario_model.sito,
            numero_inventario=inventario_model.numero_inventario,
            tipo_reperto=inventario_model.tipo_reperto,
            definizione=inventario_model.definizione,
            descrizione=inventario_model.descrizione,
            area=inventario_model.area,
            us=inventario_model.us,
            peso=inventario_model.peso
        )
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id_invmat': self.id_invmat,
            'sito': self.sito,
            'numero_inventario': self.numero_inventario,
            'tipo_reperto': self.tipo_reperto,
            'definizione': self.definizione,
            'descrizione': self.descrizione,
            'area': self.area,
            'us': self.us,
            'peso': self.peso
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for the inventory item"""
        return f"{self.sito} - {self.numero_inventario}"