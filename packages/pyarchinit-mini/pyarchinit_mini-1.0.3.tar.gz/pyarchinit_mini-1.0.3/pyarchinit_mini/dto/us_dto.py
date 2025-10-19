"""
US Data Transfer Object
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class USDTO:
    """
    Data Transfer Object for US (Stratigraphic Unit) data
    This class holds US data without SQLAlchemy session dependencies
    """
    id_us: int
    sito: str
    area: Optional[str] = None
    us: Optional[int] = None
    d_stratigrafica: Optional[str] = None
    d_interpretativa: Optional[str] = None
    descrizione: Optional[str] = None
    interpretazione: Optional[str] = None
    
    # Chronological data
    periodo_iniziale: Optional[str] = None
    fase_iniziale: Optional[str] = None
    periodo_finale: Optional[str] = None
    fase_finale: Optional[str] = None
    
    # Excavation data
    scavato: Optional[str] = None
    attivita: Optional[str] = None
    anno_scavo: Optional[int] = None
    metodo_di_scavo: Optional[str] = None
    data_schedatura: Optional[str] = None  # Date as string for DTO
    schedatore: Optional[str] = None
    
    # Physical characteristics
    formazione: Optional[str] = None
    stato_di_conservazione: Optional[str] = None
    colore: Optional[str] = None
    consistenza: Optional[str] = None
    struttura: Optional[str] = None
    
    # Documentation and relationships
    inclusi: Optional[str] = None
    campioni: Optional[str] = None
    rapporti: Optional[str] = None
    documentazione: Optional[str] = None
    cont_per: Optional[str] = None
    order_layer: Optional[int] = None
    
    # USM specific fields
    unita_tipo: Optional[str] = None
    settore: Optional[str] = None
    quad_par: Optional[str] = None
    ambient: Optional[str] = None
    saggio: Optional[str] = None
    
    # ICCD fields
    n_catalogo_generale: Optional[str] = None
    n_catalogo_interno: Optional[str] = None
    n_catalogo_internazionale: Optional[str] = None
    soprintendenza: Optional[str] = None
    
    # Measurements
    quota_relativa: Optional[float] = None
    quota_abs: Optional[float] = None
    lunghezza_max: Optional[float] = None
    altezza_max: Optional[float] = None
    altezza_min: Optional[float] = None
    profondita_max: Optional[float] = None
    profondita_min: Optional[float] = None
    larghezza_media: Optional[float] = None
    
    # Additional data
    osservazioni: Optional[str] = None
    datazione: Optional[str] = None
    flottazione: Optional[str] = None
    setacciatura: Optional[str] = None
    affidabilita: Optional[str] = None
    direttore_us: Optional[str] = None
    responsabile_us: Optional[str] = None
    
    @classmethod
    def from_model(cls, us_model) -> 'USDTO':
        """Create DTO from SQLAlchemy model instance"""
        return cls(
            id_us=us_model.id_us,
            sito=us_model.sito,
            area=us_model.area,
            us=us_model.us,
            d_stratigrafica=us_model.d_stratigrafica,
            d_interpretativa=us_model.d_interpretativa,
            descrizione=us_model.descrizione,
            interpretazione=us_model.interpretazione,
            
            # Chronological data
            periodo_iniziale=us_model.periodo_iniziale,
            fase_iniziale=us_model.fase_iniziale,
            periodo_finale=us_model.periodo_finale,
            fase_finale=us_model.fase_finale,
            
            # Excavation data
            scavato=us_model.scavato,
            attivita=us_model.attivita,
            anno_scavo=us_model.anno_scavo,
            metodo_di_scavo=us_model.metodo_di_scavo,
            data_schedatura=str(us_model.data_schedatura) if us_model.data_schedatura else None,
            schedatore=us_model.schedatore,
            
            # Physical characteristics
            formazione=us_model.formazione,
            stato_di_conservazione=us_model.stato_di_conservazione,
            colore=us_model.colore,
            consistenza=us_model.consistenza,
            struttura=us_model.struttura,
            
            # Documentation and relationships
            inclusi=us_model.inclusi,
            campioni=us_model.campioni,
            rapporti=us_model.rapporti,
            documentazione=us_model.documentazione,
            cont_per=us_model.cont_per,
            order_layer=us_model.order_layer,
            
            # USM specific fields
            unita_tipo=us_model.unita_tipo,
            settore=us_model.settore,
            quad_par=us_model.quad_par,
            ambient=us_model.ambient,
            saggio=us_model.saggio,
            
            # ICCD fields
            n_catalogo_generale=us_model.n_catalogo_generale,
            n_catalogo_interno=us_model.n_catalogo_interno,
            n_catalogo_internazionale=us_model.n_catalogo_internazionale,
            soprintendenza=us_model.soprintendenza,
            
            # Measurements
            quota_relativa=us_model.quota_relativa,
            quota_abs=us_model.quota_abs,
            lunghezza_max=us_model.lunghezza_max,
            altezza_max=us_model.altezza_max,
            altezza_min=us_model.altezza_min,
            profondita_max=us_model.profondita_max,
            profondita_min=us_model.profondita_min,
            larghezza_media=us_model.larghezza_media,
            
            # Additional data
            osservazioni=us_model.osservazioni,
            datazione=us_model.datazione,
            flottazione=us_model.flottazione,
            setacciatura=us_model.setacciatura,
            affidabilita=us_model.affidabilita,
            direttore_us=us_model.direttore_us,
            responsabile_us=us_model.responsabile_us
        )
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id_us': self.id_us,
            'sito': self.sito,
            'area': self.area,
            'us': self.us,
            'd_stratigrafica': self.d_stratigrafica,
            'd_interpretativa': self.d_interpretativa,
            'descrizione': self.descrizione,
            'interpretazione': self.interpretazione,
            
            # Chronological data
            'periodo_iniziale': self.periodo_iniziale,
            'fase_iniziale': self.fase_iniziale,
            'periodo_finale': self.periodo_finale,
            'fase_finale': self.fase_finale,
            
            # Excavation data
            'scavato': self.scavato,
            'attivita': self.attivita,
            'anno_scavo': self.anno_scavo,
            'metodo_di_scavo': self.metodo_di_scavo,
            'data_schedatura': self.data_schedatura,
            'schedatore': self.schedatore,
            
            # Physical characteristics
            'formazione': self.formazione,
            'stato_di_conservazione': self.stato_di_conservazione,
            'colore': self.colore,
            'consistenza': self.consistenza,
            'struttura': self.struttura,
            
            # Documentation and relationships
            'inclusi': self.inclusi,
            'campioni': self.campioni,
            'rapporti': self.rapporti,
            'documentazione': self.documentazione,
            'cont_per': self.cont_per,
            'order_layer': self.order_layer,
            
            # USM specific fields
            'unita_tipo': self.unita_tipo,
            'settore': self.settore,
            'quad_par': self.quad_par,
            'ambient': self.ambient,
            'saggio': self.saggio,
            
            # ICCD fields
            'n_catalogo_generale': self.n_catalogo_generale,
            'n_catalogo_interno': self.n_catalogo_interno,
            'n_catalogo_internazionale': self.n_catalogo_internazionale,
            'soprintendenza': self.soprintendenza,
            
            # Measurements
            'quota_relativa': self.quota_relativa,
            'quota_abs': self.quota_abs,
            'lunghezza_max': self.lunghezza_max,
            'altezza_max': self.altezza_max,
            'altezza_min': self.altezza_min,
            'profondita_max': self.profondita_max,
            'profondita_min': self.profondita_min,
            'larghezza_media': self.larghezza_media,
            
            # Additional data
            'osservazioni': self.osservazioni,
            'datazione': self.datazione,
            'flottazione': self.flottazione,
            'setacciatura': self.setacciatura,
            'affidabilita': self.affidabilita,
            'direttore_us': self.direttore_us,
            'responsabile_us': self.responsabile_us
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for the US"""
        return f"{self.sito} - US {self.us}"