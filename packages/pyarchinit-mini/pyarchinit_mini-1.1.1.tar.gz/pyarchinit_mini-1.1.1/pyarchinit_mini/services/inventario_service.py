"""
Inventario Materiali service - Business logic for inventory management
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from ..database.manager import DatabaseManager
from ..models.inventario_materiali import InventarioMateriali
from ..models.site import Site
from ..models.us import US
from ..dto.inventario_dto import InventarioDTO
from ..utils.validators import validate_data
from ..utils.exceptions import ValidationError, RecordNotFoundError

class InventarioService:
    """Service class for inventory operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_inventario(self, inv_data: Dict[str, Any]) -> InventarioMateriali:
        """Create a new inventory item"""
        # Validate data
        validate_data('inventario', inv_data)
        
        # Verify site exists
        site = self.db_manager.get_by_field(Site, 'sito', inv_data['sito'])
        if not site:
            raise ValidationError(f"Site '{inv_data['sito']}' does not exist", 'sito', inv_data['sito'])
        
        # Check for duplicate inventory number in same site
        existing_inv = self._get_by_site_and_number(
            inv_data['sito'],
            inv_data['numero_inventario']
        )
        if existing_inv:
            raise ValidationError(
                f"Inventory number {inv_data['numero_inventario']} already exists in site '{inv_data['sito']}'",
                'numero_inventario',
                inv_data['numero_inventario']
            )
        
        # TODO: Verify US exists if specified
        if inv_data.get('us'):
            self._validate_us_exists(inv_data['sito'], inv_data.get('area', ''), inv_data['us'])
        
        # Create inventory item
        return self.db_manager.create(InventarioMateriali, inv_data)
    
    def create_inventario_dto(self, inv_data: Dict[str, Any]) -> InventarioDTO:
        """Create a new inventory item and return as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                # Validate data
                validate_data('inventario', inv_data)
                
                # Verify site exists
                site = session.query(Site).filter(Site.sito == inv_data['sito']).first()
                if not site:
                    raise ValidationError(f"Site '{inv_data['sito']}' does not exist", 'sito', inv_data['sito'])
                
                # Check for duplicate inventory number in same site
                existing_inv = session.query(InventarioMateriali).filter(
                    InventarioMateriali.sito == inv_data['sito'],
                    InventarioMateriali.numero_inventario == inv_data['numero_inventario']
                ).first()
                
                if existing_inv:
                    raise ValidationError(
                        f"Inventory number {inv_data['numero_inventario']} already exists in site '{inv_data['sito']}'",
                        'numero_inventario',
                        inv_data['numero_inventario']
                    )
                
                # TODO: Verify US exists if specified
                # Disabled for now to avoid complex query issues
                # if inv_data.get('us'):
                #     self._validate_us_exists_session(session, inv_data['sito'], inv_data.get('area', ''), inv_data['us'])
                
                # Create inventory item
                inv = InventarioMateriali(**inv_data)
                session.add(inv)
                session.flush()  # Get the ID
                session.refresh(inv)  # Refresh to get all data
                
                # Convert to DTO while still in session
                return InventarioDTO.from_model(inv)
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to create InventarioMateriali: {e}")
    
    def _validate_us_exists_session(self, session, sito: str, area: str, us_number: int):
        """Validate that a US exists within an existing session"""
        from sqlalchemy import or_
        # This is a simplified check - in reality would use proper foreign keys
        count = session.query(US).filter(
            US.sito == sito,
            or_(US.area == area, (US.area.is_(None) & (area == ''))),
            US.us == us_number
        ).count()
        
        if count == 0:
            raise ValidationError(
                f"US {us_number} does not exist in site '{sito}', area '{area}'",
                'us',
                us_number
            )
    
    def get_inventario_by_id(self, inv_id: int) -> Optional[InventarioMateriali]:
        """Get inventory item by ID"""
        return self.db_manager.get_by_id(InventarioMateriali, inv_id)
    
    def get_inventario_dto_by_id(self, inv_id: int) -> Optional[InventarioDTO]:
        """Get inventory item by ID as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                item = session.query(InventarioMateriali).filter(InventarioMateriali.id_invmat == inv_id).first()
                if item:
                    return InventarioDTO.from_model(item)
                return None
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get InventarioMateriali by ID {inv_id}: {e}")
    
    def get_all_inventario(self, page: int = 1, size: int = 10,
                          filters: Optional[Dict[str, Any]] = None) -> List[InventarioDTO]:
        """Get all inventory items with pagination and filtering - returns DTOs"""
        try:
            from sqlalchemy import asc, desc
            with self.db_manager.connection.get_session() as session:
                query = session.query(InventarioMateriali)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(InventarioMateriali, key):
                            query = query.filter(getattr(InventarioMateriali, key) == value)
                
                # Apply ordering
                query = query.order_by(asc(InventarioMateriali.numero_inventario))
                
                # Apply pagination
                offset = (page - 1) * size
                items = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [InventarioDTO.from_model(item) for item in items]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get InventarioMateriali records: {e}")
    
    def update_inventario(self, inv_id: int, update_data: Dict[str, Any]) -> InventarioMateriali:
        """Update existing inventory item"""
        # For updates, we don't need full validation (only check specific business rules)
        # Skip validate_data() for updates as it requires all mandatory fields
        
        # If site is being changed, verify new site exists
        if 'sito' in update_data:
            site = self.db_manager.get_by_field(Site, 'sito', update_data['sito'])
            if not site:
                raise ValidationError(f"Site '{update_data['sito']}' does not exist")
        
        # If inventory number or site is being changed, check for duplicates
        if 'numero_inventario' in update_data or 'sito' in update_data:
            current_inv = self.get_inventario_by_id(inv_id)
            if not current_inv:
                raise RecordNotFoundError(f"Inventory item with ID {inv_id} not found")
            
            new_sito = update_data.get('sito', current_inv.sito)
            new_numero = update_data.get('numero_inventario', current_inv.numero_inventario)
            
            existing_inv = self._get_by_site_and_number(new_sito, new_numero)
            if existing_inv and existing_inv.id_invmat != inv_id:
                raise ValidationError(
                    f"Inventory number {new_numero} already exists in site '{new_sito}'"
                )
        
        # Validate US if specified
        if 'us' in update_data and update_data['us']:
            current_inv = current_inv or self.get_inventario_by_id(inv_id)
            sito = update_data.get('sito', current_inv.sito)
            area = update_data.get('area', current_inv.area or '')
            self._validate_us_exists(sito, area, update_data['us'])
        
        # Update inventory item
        return self.db_manager.update(InventarioMateriali, inv_id, update_data)
    
    def delete_inventario(self, inv_id: int) -> bool:
        """Delete inventory item"""
        return self.db_manager.delete(InventarioMateriali, inv_id)
    
    def count_inventario(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count inventory items with optional filters"""
        return self.db_manager.count(InventarioMateriali, filters)
    
    def search_inventario(self, search_term: str, page: int = 1, size: int = 10) -> List[InventarioDTO]:
        """Search inventory items by term - returns DTOs"""
        try:
            from sqlalchemy import asc, desc, or_
            with self.db_manager.connection.get_session() as session:
                query = session.query(InventarioMateriali)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        InventarioMateriali.sito.contains(search_term),
                        InventarioMateriali.tipo_reperto.contains(search_term),
                        InventarioMateriali.definizione.contains(search_term),
                        InventarioMateriali.descrizione.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply ordering
                query = query.order_by(asc(InventarioMateriali.numero_inventario))
                
                # Apply pagination
                offset = (page - 1) * size
                items = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [InventarioDTO.from_model(item) for item in items]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search InventarioMateriali records: {e}")
    
    def get_inventario_by_site(self, site_name: str, page: int = 1, size: int = 10) -> List[InventarioDTO]:
        """Get all inventory items for a specific site - returns DTOs"""
        return self.get_all_inventario(page=page, size=size, filters={'sito': site_name})
    
    def get_inventario_by_us(self, site_name: str, area: str, us_number: int,
                            page: int = 1, size: int = 10) -> List[InventarioDTO]:
        """Get all inventory items for a specific US - returns DTOs"""
        filters = {'sito': site_name, 'area': area, 'us': us_number}
        return self.get_all_inventario(page=page, size=size, filters=filters)
    
    def get_inventario_by_type(self, tipo_reperto: str, page: int = 1, size: int = 10) -> List[InventarioDTO]:
        """Get all inventory items of a specific type - returns DTOs"""
        return self.get_all_inventario(page=page, size=size, filters={'tipo_reperto': tipo_reperto})
    
    def _get_by_site_and_number(self, sito: str, numero: int) -> Optional[InventarioMateriali]:
        """Get inventory item by site and number"""
        query = """
        SELECT * FROM inventario_materiali_table 
        WHERE sito = :sito AND numero_inventario = :numero
        LIMIT 1
        """
        
        with self.db_manager.connection.get_session() as session:
            result = session.execute(text(query), {
                'sito': sito,
                'numero': numero
            }).fetchone()
            
            if result:
                return self.db_manager.get_by_id(InventarioMateriali, result[0])
            return None
    
    def _validate_us_exists(self, sito: str, area: str, us_number: int):
        """Validate that a US exists"""
        # This is a simplified check - in reality would use proper foreign keys
        query = """
        SELECT COUNT(*) FROM us_table 
        WHERE sito = :sito AND 
              (area = :area OR (area IS NULL AND :area = '')) AND 
              us = :us_number
        """
        
        count = self.db_manager.execute_raw_query(query, {
            'sito': sito,
            'area': area,
            'us_number': us_number
        })[0][0]
        
        if count == 0:
            raise ValidationError(
                f"US {us_number} does not exist in site '{sito}', area '{area}'",
                'us',
                us_number
            )
    
    def get_inventory_statistics(self, inv_id: int) -> Dict[str, Any]:
        """Get statistics for an inventory item"""
        inv = self.get_inventario_by_id(inv_id)
        if not inv:
            raise RecordNotFoundError(f"Inventory item with ID {inv_id} not found")
        
        return {
            'inventory_id': inv_id,
            'inventory_number': inv.numero_inventario,
            'site': inv.sito,
            'type': inv.tipo_reperto,
            'context': inv.context_info,
            'total_fragments': inv.totale_frammenti,
            'weight': inv.peso,
            'diagnostic': inv.diagnostico == 'SI' if inv.diagnostico else False,
            'catalogued': inv.repertato == 'SI' if inv.repertato else False
        }
    
    def get_type_statistics(self, site_name: Optional[str] = None) -> Dict[str, int]:
        """Get statistics by find type"""
        base_query = "SELECT tipo_reperto, COUNT(*) FROM inventario_materiali_table"
        
        if site_name:
            query = f"{base_query} WHERE sito = :sito GROUP BY tipo_reperto"
            results = self.db_manager.execute_raw_query(query, {'sito': site_name})
        else:
            query = f"{base_query} GROUP BY tipo_reperto"
            results = self.db_manager.execute_raw_query(query)
        
        return {row[0] or 'Unknown': row[1] for row in results}
    
    def get_all_inventario_dto(self, page: int = 1, size: int = 10) -> List:
        """Get all inventario items as DTOs (session-safe)"""
        try:
            with self.db_manager.connection.get_session() as session:
                offset = (page - 1) * size
                inventarios = session.query(InventarioMateriali).offset(offset).limit(size).all()
                
                # Convert to simple dicts (like DTOs) while still in session
                dto_list = []
                for inv in inventarios:
                    dto_dict = {
                        'id_invmat': inv.id_invmat,
                        'sito': inv.sito,
                        'numero_inventario': inv.numero_inventario,
                        'tipo_reperto': inv.tipo_reperto,
                        'definizione': inv.definizione,
                        'area': inv.area,
                        'us': inv.us,
                        'peso': inv.peso,
                        'stato_conservazione': inv.stato_conservazione,
                        'schedatore': getattr(inv, 'schedatore', None),
                        'date_scheda': getattr(inv, 'date_scheda', None),
                        'punto_rinv': getattr(inv, 'punto_rinv', None),
                        'negativo_photo': getattr(inv, 'negativo_photo', None),
                        'diapositiva': getattr(inv, 'diapositiva', None)
                    }
                    dto_list.append(dto_dict)
                
                return dto_list
                
        except Exception as e:
            from ..exceptions import DatabaseError
            raise DatabaseError(f"Failed to get inventario as DTOs: {e}")