"""
Inventario Materiali API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from .schemas import InventarioCreate, InventarioUpdate, InventarioResponse, PaginatedResponse
from .dependencies import get_inventario_service
from ..services.inventario_service import InventarioService
from ..utils.exceptions import ValidationError, RecordNotFoundError

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_inventario_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sito: Optional[str] = Query(None, description="Filter by site"),
    tipo_reperto: Optional[str] = Query(None, description="Filter by find type"),
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Get paginated list of inventory items"""
    try:
        filters = {}
        if sito:
            filters['sito'] = sito
        if tipo_reperto:
            filters['tipo_reperto'] = tipo_reperto
        
        items = inventario_service.get_all_inventario(page=page, size=size, filters=filters)
        total = inventario_service.count_inventario(filters=filters)
        
        return PaginatedResponse(
            items=[InventarioResponse.from_orm(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}", response_model=InventarioResponse)
async def get_inventario_item(
    item_id: int,
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Get inventory item by ID"""
    try:
        item = inventario_service.get_inventario_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        return InventarioResponse.from_orm(item)
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=InventarioResponse, status_code=201)
async def create_inventario_item(
    item_data: InventarioCreate,
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Create a new inventory item"""
    try:
        item = inventario_service.create_inventario(item_data.dict())
        return InventarioResponse.from_orm(item)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}", response_model=InventarioResponse)
async def update_inventario_item(
    item_id: int,
    item_data: InventarioUpdate,
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Update an existing inventory item"""
    try:
        update_data = {k: v for k, v in item_data.dict().items() if v is not None}
        item = inventario_service.update_inventario(item_id, update_data)
        return InventarioResponse.from_orm(item)
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_inventario_item(
    item_id: int,
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Delete an inventory item"""
    try:
        success = inventario_service.delete_inventario(item_id)
        if success:
            return {"message": "Inventory item deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Inventory item not found")
    except RecordNotFoundError:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))