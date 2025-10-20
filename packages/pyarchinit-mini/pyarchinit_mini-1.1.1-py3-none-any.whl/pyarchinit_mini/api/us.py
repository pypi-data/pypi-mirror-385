"""
US (Stratigraphic Unit) API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from .schemas import USCreate, USUpdate, USResponse, PaginatedResponse
from .dependencies import get_us_service
from ..services.us_service import USService
from ..utils.exceptions import ValidationError, RecordNotFoundError

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_us_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sito: Optional[str] = Query(None, description="Filter by site"),
    area: Optional[str] = Query(None, description="Filter by area"),
    us_service: USService = Depends(get_us_service)
):
    """Get paginated list of stratigraphic units"""
    try:
        filters = {}
        if sito:
            filters['sito'] = sito
        if area:
            filters['area'] = area
        
        us_list = us_service.get_all_us(page=page, size=size, filters=filters)
        total = us_service.count_us(filters=filters)
        
        return PaginatedResponse(
            items=[USResponse.from_orm(us) for us in us_list],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{us_id}", response_model=USResponse)
async def get_us(
    us_id: int,
    us_service: USService = Depends(get_us_service)
):
    """Get US by ID"""
    try:
        us = us_service.get_us_by_id(us_id)
        if not us:
            raise HTTPException(status_code=404, detail="US not found")
        return USResponse.from_orm(us)
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="US not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=USResponse, status_code=201)
async def create_us(
    us_data: USCreate,
    us_service: USService = Depends(get_us_service)
):
    """Create a new stratigraphic unit"""
    try:
        us = us_service.create_us(us_data.dict())
        return USResponse.from_orm(us)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{us_id}", response_model=USResponse)
async def update_us(
    us_id: int,
    us_data: USUpdate,
    us_service: USService = Depends(get_us_service)
):
    """Update an existing stratigraphic unit"""
    try:
        update_data = {k: v for k, v in us_data.dict().items() if v is not None}
        us = us_service.update_us(us_id, update_data)
        return USResponse.from_orm(us)
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="US not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{us_id}")
async def delete_us(
    us_id: int,
    us_service: USService = Depends(get_us_service)
):
    """Delete a stratigraphic unit"""
    try:
        success = us_service.delete_us(us_id)
        if success:
            return {"message": "US deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="US not found")
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="US not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))