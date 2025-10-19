"""
Pydantic schemas for API request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

# Base schemas

class BaseSchema(BaseModel):
    """Base schema with common fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Site schemas

class SiteBase(BaseModel):
    """Base site schema"""
    sito: str = Field(..., min_length=1, max_length=350, description="Site name")
    nazione: Optional[str] = Field(None, max_length=250, description="Country")
    regione: Optional[str] = Field(None, max_length=250, description="Region")
    comune: Optional[str] = Field(None, max_length=250, description="Municipality")
    provincia: Optional[str] = Field(None, max_length=10, description="Province")
    definizione_sito: Optional[str] = Field(None, max_length=250, description="Site definition")
    descrizione: Optional[str] = Field(None, description="Description")
    sito_path: Optional[str] = Field(None, max_length=500, description="Site path")
    find_check: Optional[bool] = Field(False, description="Find check flag")

class SiteCreate(SiteBase):
    """Schema for creating a site"""
    pass

class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    sito: Optional[str] = Field(None, min_length=1, max_length=350)
    nazione: Optional[str] = Field(None, max_length=250)
    regione: Optional[str] = Field(None, max_length=250)
    comune: Optional[str] = Field(None, max_length=250)
    provincia: Optional[str] = Field(None, max_length=10)
    definizione_sito: Optional[str] = Field(None, max_length=250)
    descrizione: Optional[str] = None
    sito_path: Optional[str] = Field(None, max_length=500)
    find_check: Optional[bool] = None

class SiteResponse(SiteBase, BaseSchema):
    """Schema for site response"""
    id_sito: int = Field(..., description="Site ID")

# US (Stratigraphic Unit) schemas

class USBase(BaseModel):
    """Base US schema"""
    sito: str = Field(..., max_length=350, description="Site name")
    area: Optional[str] = Field(None, max_length=20, description="Area")
    us: int = Field(..., gt=0, description="US number")
    d_stratigrafica: Optional[str] = Field(None, max_length=350, description="Stratigraphic description")
    d_interpretativa: Optional[str] = Field(None, max_length=350, description="Interpretative description")
    descrizione: Optional[str] = Field(None, description="Description")
    interpretazione: Optional[str] = Field(None, description="Interpretation")
    periodo_iniziale: Optional[str] = Field(None, max_length=300, description="Initial period")
    fase_iniziale: Optional[str] = Field(None, max_length=300, description="Initial phase")
    periodo_finale: Optional[str] = Field(None, max_length=300, description="Final period")
    fase_finale: Optional[str] = Field(None, max_length=300, description="Final phase")
    scavato: Optional[str] = Field(None, max_length=20, description="Excavated")
    attivita: Optional[str] = Field(None, max_length=30, description="Activity")
    anno_scavo: Optional[int] = Field(None, ge=1800, le=2100, description="Excavation year")
    metodo_di_scavo: Optional[str] = Field(None, max_length=20, description="Excavation method")
    schedatore: Optional[str] = Field(None, max_length=100, description="Recorder")
    formazione: Optional[str] = Field(None, max_length=20, description="Formation")
    stato_di_conservazione: Optional[str] = Field(None, max_length=20, description="Conservation state")
    colore: Optional[str] = Field(None, max_length=20, description="Color")
    consistenza: Optional[str] = Field(None, max_length=20, description="Consistency")
    struttura: Optional[str] = Field(None, max_length=30, description="Structure")
    
    # Measurements
    quota_relativa: Optional[float] = Field(None, ge=0, description="Relative elevation")
    quota_abs: Optional[float] = Field(None, ge=0, description="Absolute elevation")
    lunghezza_max: Optional[float] = Field(None, ge=0, description="Maximum length")
    altezza_max: Optional[float] = Field(None, ge=0, description="Maximum height")
    altezza_min: Optional[float] = Field(None, ge=0, description="Minimum height")
    profondita_max: Optional[float] = Field(None, ge=0, description="Maximum depth")
    profondita_min: Optional[float] = Field(None, ge=0, description="Minimum depth")
    larghezza_media: Optional[float] = Field(None, ge=0, description="Average width")
    
    # Additional fields
    osservazioni: Optional[str] = Field(None, description="Observations")
    datazione: Optional[str] = Field(None, max_length=100, description="Dating")
    direttore_us: Optional[str] = Field(None, max_length=100, description="US director")
    responsabile_us: Optional[str] = Field(None, max_length=100, description="US responsible")

class USCreate(USBase):
    """Schema for creating a US"""
    pass

class USUpdate(BaseModel):
    """Schema for updating a US"""
    sito: Optional[str] = Field(None, max_length=350)
    area: Optional[str] = Field(None, max_length=20)
    us: Optional[int] = Field(None, gt=0)
    d_stratigrafica: Optional[str] = Field(None, max_length=350)
    d_interpretativa: Optional[str] = Field(None, max_length=350)
    descrizione: Optional[str] = None
    interpretazione: Optional[str] = None
    anno_scavo: Optional[int] = Field(None, ge=1800, le=2100)
    schedatore: Optional[str] = Field(None, max_length=100)
    # ... other optional fields

class USResponse(USBase, BaseSchema):
    """Schema for US response"""
    id_us: int = Field(..., description="US ID")

# Inventario Materiali schemas

class InventarioBase(BaseModel):
    """Base inventory schema"""
    sito: str = Field(..., max_length=350, description="Site name")
    numero_inventario: int = Field(..., gt=0, description="Inventory number")
    tipo_reperto: Optional[str] = Field(None, max_length=20, description="Find type")
    criterio_schedatura: Optional[str] = Field(None, max_length=20, description="Recording criteria")
    definizione: Optional[str] = Field(None, max_length=20, description="Definition")
    descrizione: Optional[str] = Field(None, description="Description")
    area: Optional[str] = Field(None, max_length=20, description="Area")
    us: Optional[int] = Field(None, gt=0, description="US number")
    lavato: Optional[str] = Field(None, max_length=5, description="Washed")
    nr_cassa: Optional[str] = Field(None, max_length=20, description="Box number")
    luogo_conservazione: Optional[str] = Field(None, max_length=350, description="Conservation location")
    stato_conservazione: Optional[str] = Field(None, max_length=200, description="Conservation state")
    datazione_reperto: Optional[str] = Field(None, max_length=100, description="Find dating")
    
    # Technical characteristics
    forme_minime: Optional[int] = Field(None, ge=0, description="Minimum forms")
    forme_massime: Optional[int] = Field(None, ge=0, description="Maximum forms") 
    totale_frammenti: Optional[int] = Field(None, ge=0, description="Total fragments")
    peso: Optional[float] = Field(None, ge=0, description="Weight")
    diametro_orlo: Optional[float] = Field(None, ge=0, description="Rim diameter")
    eve_orlo: Optional[float] = Field(None, ge=0, le=100, description="Rim EVE")
    
    # Classification
    corpo_ceramico: Optional[str] = Field(None, max_length=20, description="Ceramic body")
    rivestimento: Optional[str] = Field(None, max_length=20, description="Surface treatment")
    tipo: Optional[str] = Field(None, max_length=300, description="Type")
    repertato: Optional[str] = Field(None, max_length=2, description="Catalogued")
    diagnostico: Optional[str] = Field(None, max_length=2, description="Diagnostic")

    @validator('lavato', 'repertato', 'diagnostico')
    def validate_yes_no_fields(cls, v):
        if v is not None and v.upper() not in ['SI', 'NO', 'S', 'N']:
            raise ValueError('Must be SI/NO or S/N')
        return v

class InventarioCreate(InventarioBase):
    """Schema for creating inventory item"""
    pass

class InventarioUpdate(BaseModel):
    """Schema for updating inventory item"""
    sito: Optional[str] = Field(None, max_length=350)
    numero_inventario: Optional[int] = Field(None, gt=0)
    tipo_reperto: Optional[str] = Field(None, max_length=20)
    # ... other optional fields

class InventarioResponse(InventarioBase, BaseSchema):
    """Schema for inventory response"""
    id_invmat: int = Field(..., description="Inventory ID")

# Pagination schemas

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[BaseModel]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        from_attributes = True