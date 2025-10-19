"""
Site API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from .schemas import SiteCreate, SiteUpdate, SiteResponse, PaginatedResponse
from .dependencies import get_site_service
from ..services.site_service import SiteService
from ..utils.exceptions import ValidationError, RecordNotFoundError, DuplicateRecordError

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_sites(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    nazione: Optional[str] = Query(None, description="Filter by country"),
    regione: Optional[str] = Query(None, description="Filter by region"),
    comune: Optional[str] = Query(None, description="Filter by municipality"),
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get paginated list of sites with optional filtering and search
    """
    try:
        # Build filters
        filters = {}
        if nazione:
            filters['nazione'] = nazione
        if regione:
            filters['regione'] = regione
        if comune:
            filters['comune'] = comune
        
        # Get sites
        if search:
            sites = site_service.search_sites(search, page=page, size=size, filters=filters)
        else:
            sites = site_service.get_all_sites(page=page, size=size, filters=filters)
        
        # Get total count for pagination
        total = site_service.count_sites(filters=filters)
        
        return PaginatedResponse(
            items=[SiteResponse.from_orm(site) for site in sites],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get site by ID
    """
    try:
        site = site_service.get_site_by_id(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return SiteResponse.from_orm(site)
    
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-name/{site_name}", response_model=SiteResponse)
async def get_site_by_name(
    site_name: str,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get site by name
    """
    try:
        site = site_service.get_site_by_name(site_name)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return SiteResponse.from_orm(site)
    
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=SiteResponse, status_code=201)
async def create_site(
    site_data: SiteCreate,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Create a new site
    """
    try:
        site = site_service.create_site(site_data.dict())
        return SiteResponse.from_orm(site)
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateRecordError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Update an existing site
    """
    try:
        # Only include non-None values in update
        update_data = {k: v for k, v in site_data.dict().items() if v is not None}
        site = site_service.update_site(site_id, update_data)
        return SiteResponse.from_orm(site)
    
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Site not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateRecordError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{site_id}")
async def delete_site(
    site_id: int,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Delete a site
    """
    try:
        success = site_service.delete_site(site_id)
        if success:
            return JSONResponse(
                status_code=200,
                content={"message": "Site deleted successfully"}
            )
        else:
            raise HTTPException(status_code=404, detail="Site not found")
    
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{site_id}/stats")
async def get_site_stats(
    site_id: int,
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get statistics for a site (US count, inventory count, etc.)
    """
    try:
        stats = site_service.get_site_statistics(site_id)
        return stats
    
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Site not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations/countries")
async def get_countries(
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get list of unique countries from sites
    """
    try:
        countries = site_service.get_unique_countries()
        return {"countries": countries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations/regions")
async def get_regions(
    nazione: Optional[str] = Query(None, description="Filter by country"),
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get list of unique regions, optionally filtered by country
    """
    try:
        regions = site_service.get_unique_regions(nazione)
        return {"regions": regions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations/municipalities")
async def get_municipalities(
    nazione: Optional[str] = Query(None, description="Filter by country"),
    regione: Optional[str] = Query(None, description="Filter by region"),
    site_service: SiteService = Depends(get_site_service)
):
    """
    Get list of unique municipalities, optionally filtered by country and region
    """
    try:
        municipalities = site_service.get_unique_municipalities(nazione, regione)
        return {"municipalities": municipalities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))