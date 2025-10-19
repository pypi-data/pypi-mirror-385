"""
US (Stratigraphic Unit) service - Business logic for US management
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from ..database.manager import DatabaseManager
from ..models.us import US
from ..models.site import Site
from ..dto.us_dto import USDTO
from ..utils.validators import validate_data
from ..utils.exceptions import ValidationError, RecordNotFoundError
from ..utils.stratigraphic_validator import StratigraphicValidator

class USService:
    """Service class for US operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_us(self, us_data: Dict[str, Any]) -> US:
        """Create a new stratigraphic unit"""
        # Validate data
        validate_data('us', us_data)
        
        # Verify site exists
        site = self.db_manager.get_by_field(Site, 'sito', us_data['sito'])
        if not site:
            raise ValidationError(f"Site '{us_data['sito']}' does not exist", 'sito', us_data['sito'])
        
        # Check for duplicate US number in same site/area
        existing_us = self._get_us_by_site_area_number(
            us_data['sito'], 
            us_data.get('area', ''), 
            us_data['us']
        )
        if existing_us:
            raise ValidationError(
                f"US {us_data['us']} already exists in site '{us_data['sito']}', area '{us_data.get('area', '')}'",
                'us',
                us_data['us']
            )
        
        # Create US
        return self.db_manager.create(US, us_data)
    
    def create_us_dto(self, us_data: Dict[str, Any]) -> USDTO:
        """Create a new US and return as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                # Validate data
                validate_data('us', us_data)
                
                # Verify site exists
                site = session.query(Site).filter(Site.sito == us_data['sito']).first()
                if not site:
                    raise ValidationError(f"Site '{us_data['sito']}' does not exist", 'sito', us_data['sito'])
                
                # Check for duplicate US number in same site/area
                existing_us = session.query(US).filter(
                    US.sito == us_data['sito'],
                    US.area == us_data.get('area', ''),
                    US.us == us_data['us']
                ).first()
                
                if existing_us:
                    raise ValidationError(
                        f"US {us_data['us']} already exists in site '{us_data['sito']}', area '{us_data.get('area', '')}'",
                        'us',
                        us_data['us']
                    )
                
                # Create US
                us = US(**us_data)
                session.add(us)
                session.flush()  # Get the ID
                session.refresh(us)  # Refresh to get all data
                
                # Convert to DTO while still in session
                return USDTO.from_model(us)
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to create US: {e}")
    
    def get_us_by_id(self, us_id: int) -> Optional[US]:
        """Get US by ID"""
        return self.db_manager.get_by_id(US, us_id)
    
    def get_us_dto_by_id(self, us_id: int) -> Optional[USDTO]:
        """Get US by ID as DTO"""
        try:
            with self.db_manager.connection.get_session() as session:
                us = session.query(US).filter(US.id_us == us_id).first()
                if us:
                    return USDTO.from_model(us)
                return None
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get US by ID {us_id}: {e}")
    
    def get_all_us(self, page: int = 1, size: int = 10,
                   filters: Optional[Dict[str, Any]] = None) -> List[USDTO]:
        """Get all US with pagination and filtering - returns DTOs"""
        try:
            from sqlalchemy import asc, desc
            with self.db_manager.connection.get_session() as session:
                query = session.query(US)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(US, key):
                            query = query.filter(getattr(US, key) == value)
                
                # Apply ordering
                query = query.order_by(asc(US.us))
                
                # Apply pagination
                offset = (page - 1) * size
                us_list = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [USDTO.from_model(us) for us in us_list]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get US records: {e}")
    
    def update_us(self, us_id: int, update_data: Dict[str, Any]) -> US:
        """Update existing US"""
        # For updates, we don't need full validation (only check specific business rules)
        # Skip validate_data() for updates as it requires all mandatory fields
        
        # If site is being changed, verify new site exists
        if 'sito' in update_data:
            site = self.db_manager.get_by_field(Site, 'sito', update_data['sito'])
            if not site:
                raise ValidationError(f"Site '{update_data['sito']}' does not exist")
        
        # If US number, site, or area is being changed, check for duplicates
        if any(field in update_data for field in ['us', 'sito', 'area']):
            current_us = self.get_us_by_id(us_id)
            if not current_us:
                raise RecordNotFoundError(f"US with ID {us_id} not found")
            
            new_sito = update_data.get('sito', current_us.sito)
            new_area = update_data.get('area', current_us.area or '')
            new_us_num = update_data.get('us', current_us.us)
            
            existing_us = self._get_us_by_site_area_number(new_sito, new_area, new_us_num)
            if existing_us and existing_us.id_us != us_id:
                raise ValidationError(
                    f"US {new_us_num} already exists in site '{new_sito}', area '{new_area}'"
                )
        
        # Update US
        return self.db_manager.update(US, us_id, update_data)
    
    def update_us_dto(self, us_id: int, update_data: Dict[str, Any]) -> Optional[USDTO]:
        """Update existing US and return DTO"""
        try:
            # Perform update in a single session to avoid detached instance errors
            with self.db_manager.connection.get_session() as session:
                us_record = session.query(US).filter(US.id_us == us_id).first()
                if not us_record:
                    from ..utils.exceptions import RecordNotFoundError
                    raise RecordNotFoundError(f"US with ID {us_id} not found")

                # Update fields
                for key, value in update_data.items():
                    if hasattr(us_record, key):
                        setattr(us_record, key, value)

                # Flush to persist changes and refresh
                session.flush()
                session.refresh(us_record)

                # Convert to DTO while still in session
                dto = USDTO.from_model(us_record)

            # Return DTO (session is now closed, but DTO is safe)
            return dto

        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to update US: {e}")
    
    def delete_us(self, us_id: int) -> bool:
        """Delete US"""
        # TODO: Check for related records (Inventario) before deletion
        return self.db_manager.delete(US, us_id)
    
    def count_us(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count US with optional filters"""
        return self.db_manager.count(US, filters)
    
    def search_us(self, search_term: str, page: int = 1, size: int = 10) -> List[USDTO]:
        """Search US by term - returns DTOs"""
        try:
            from sqlalchemy import asc, desc, or_
            with self.db_manager.connection.get_session() as session:
                query = session.query(US)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        US.sito.contains(search_term),
                        US.area.contains(search_term),
                        US.d_stratigrafica.contains(search_term),
                        US.d_interpretativa.contains(search_term),
                        US.descrizione.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply ordering
                query = query.order_by(asc(US.us))
                
                # Apply pagination
                offset = (page - 1) * size
                us_list = query.offset(offset).limit(size).all()
                
                # Convert to DTOs while still in session
                return [USDTO.from_model(us) for us in us_list]
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search US records: {e}")
    
    def get_us_by_site(self, site_name: str, page: int = 1, size: int = 10) -> List[USDTO]:
        """Get all US for a specific site - returns DTOs"""
        return self.get_all_us(page=page, size=size, filters={'sito': site_name})
    
    def get_us_by_site_and_area(self, site_name: str, area: str, 
                               page: int = 1, size: int = 10) -> List[USDTO]:
        """Get all US for a specific site and area - returns DTOs"""
        filters = {'sito': site_name, 'area': area}
        return self.get_all_us(page=page, size=size, filters=filters)
    
    def _get_us_by_site_area_number(self, sito: str, area: str, us_number: int) -> Optional[US]:
        """Get US by site, area and number combination"""
        # This would need a compound query
        query = """
        SELECT * FROM us_table 
        WHERE sito = :sito AND 
              (area = :area OR (area IS NULL AND :area = '')) AND 
              us = :us_number
        LIMIT 1
        """
        
        with self.db_manager.connection.get_session() as session:
            result = session.execute(text(query), {
                'sito': sito,
                'area': area,
                'us_number': us_number
            }).fetchone()
            
            if result:
                # Convert row to US object - this is simplified
                return self.db_manager.get_by_id(US, result[0])  # Assuming first column is ID
            return None
    
    def get_us_statistics(self, us_id: int) -> Dict[str, Any]:
        """Get statistics for a US"""
        us = self.get_us_by_id(us_id)
        if not us:
            raise RecordNotFoundError(f"US with ID {us_id} not found")
        
        # Get count of related inventory items
        inv_count_query = """
        SELECT COUNT(*) FROM inventario_materiali_table 
        WHERE sito = :sito AND 
              (area = :area OR (area IS NULL AND :area = '')) AND
              us = :us_number
        """
        
        inv_count = self.db_manager.execute_raw_query(inv_count_query, {
            'sito': us.sito,
            'area': us.area or '',
            'us_number': us.us
        })[0][0]
        
        return {
            'us_id': us_id,
            'identifier': us.full_identifier,
            'inventory_count': inv_count,
            'site': us.sito,
            'area': us.area,
            'us_number': us.us,
            'excavation_year': us.anno_scavo
        }
    
    def validate_stratigraphic_paradoxes(self, site_name: str, area: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate stratigraphic relationships for paradoxes
        
        Args:
            site_name: Site to validate
            area: Optional area to filter by
            
        Returns:
            Validation report with detected paradoxes
        """
        # Get all US for the site
        filters = {'sito': site_name}
        if area:
            filters['area'] = area
            
        # Get all US records (no pagination for complete validation)
        us_list = self.get_all_us(page=1, size=10000, filters=filters)
        
        # Convert DTOs to dicts for validator
        us_data_list = []
        for us_dto in us_list:
            us_dict = us_dto.__dict__.copy()
            # Remove any internal attributes
            us_dict = {k: v for k, v in us_dict.items() if not k.startswith('_')}
            us_data_list.append(us_dict)
        
        # Validate using stratigraphic validator
        validator = StratigraphicValidator()
        report = validator.get_validation_report(us_data_list)
        
        # Add site/area info to report
        report['site'] = site_name
        report['area'] = area or 'All areas'
        
        return report
    
    def validate_us_relationships(self, us_id: int) -> List[str]:
        """
        Validate relationships for a specific US
        
        Args:
            us_id: US ID to validate
            
        Returns:
            List of validation errors
        """
        us_dto = self.get_us_dto_by_id(us_id)
        if not us_dto:
            raise RecordNotFoundError(f"US with ID {us_id} not found")
        
        # Get all US for the same site
        us_list = self.get_us_by_site(us_dto.sito, page=1, size=10000)
        
        # Convert to dict list
        us_data_list = []
        for us in us_list:
            us_dict = us.__dict__.copy()
            us_dict = {k: v for k, v in us_dict.items() if not k.startswith('_')}
            us_data_list.append(us_dict)
        
        # Validate
        validator = StratigraphicValidator()
        validator.validate_all(us_data_list)
        
        # Get errors for specific US
        return validator.validate_unit_relationships(us_dto.us)
    
    def generate_relationship_fixes(self, site_name: str, area: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Generate fixes for missing reciprocal relationships and missing US
        
        Args:
            site_name: Site to check
            area: Optional area to filter by
            
        Returns:
            Dictionary with 'updates' and 'creates' lists
        """
        # Get all US for the site
        filters = {'sito': site_name}
        if area:
            filters['area'] = area
            
        # Get all US records
        us_list = self.get_all_us(page=1, size=10000, filters=filters)
        
        # Convert DTOs to dicts
        us_data_list = []
        for us_dto in us_list:
            us_dict = us_dto.__dict__.copy()
            us_dict = {k: v for k, v in us_dict.items() if not k.startswith('_')}
            us_data_list.append(us_dict)
        
        # Generate fixes
        validator = StratigraphicValidator()
        return validator.generate_relationship_fixes(us_data_list)
    
    def apply_relationship_fixes(self, fixes: Dict[str, List[Dict]], apply_creates: bool = True) -> Dict[str, int]:
        """
        Apply the generated fixes
        
        Args:
            fixes: Dictionary with 'updates' and 'creates' lists
            apply_creates: Whether to create missing US records
            
        Returns:
            Dictionary with counts of applied fixes
        """
        results = {
            'updated': 0,
            'created': 0,
            'errors': []
        }
        
        # Apply updates to existing US
        for update in fixes.get('updates', []):
            try:
                if update['us_id']:
                    # Update using ID
                    self.update_us(
                        update['us_id'], 
                        {'rapporti': update['new_value']}
                    )
                else:
                    # Find US by site/area/number and update
                    us = self._get_us_by_site_area_number(
                        update['sito'], 
                        update['area'], 
                        update['us']
                    )
                    if us:
                        self.update_us(us.id_us, {'rapporti': update['new_value']})
                
                results['updated'] += 1
            except Exception as e:
                results['errors'].append(f"Error updating US {update['us']}: {str(e)}")
        
        # Create missing US if requested
        if apply_creates:
            for create_data in fixes.get('creates', []):
                try:
                    # Remove metadata fields before creation
                    us_data = {k: v for k, v in create_data.items() 
                             if k not in ['created_from', 'reason']}
                    
                    self.create_us(us_data)
                    results['created'] += 1
                except Exception as e:
                    results['errors'].append(
                        f"Error creating US {create_data['us']}: {str(e)}"
                    )
        
        return results