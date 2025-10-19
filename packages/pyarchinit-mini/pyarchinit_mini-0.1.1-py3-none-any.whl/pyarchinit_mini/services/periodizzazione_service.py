"""
Periodizzazione service - Business logic for chronological periods and dating
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import asc, desc, or_
from ..database.manager import DatabaseManager
from ..models.harris_matrix import Period, Periodizzazione
from ..models.site import Site
from ..utils.validators import validate_data
from ..utils.exceptions import ValidationError, RecordNotFoundError

class PeriodizzazioneService:
    """Service class for periodization operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_period(self, period_data: Dict[str, Any]) -> Period:
        """Create a new archaeological period"""
        # Validate data
        validate_data('period', period_data)
        
        # Check for duplicate period name
        existing_period = self.db_manager.get_by_field(Period, 'period_name', period_data['period_name'])
        if existing_period:
            raise ValidationError(f"Period '{period_data['period_name']}' already exists")
        
        # Create period
        return self.db_manager.create(Period, period_data)
    
    def get_period_by_id(self, period_id: int) -> Optional[Period]:
        """Get period by ID"""
        return self.db_manager.get_by_id(Period, period_id)
    
    def get_all_periods(self, page: int = 1, size: int = 10,
                       filters: Optional[Dict[str, Any]] = None) -> List[Period]:
        """Get all periods with pagination and filtering"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Period)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Period, key):
                            query = query.filter(getattr(Period, key) == value)
                
                # Apply ordering by chronology
                query = query.order_by(asc(Period.start_date), asc(Period.period_name))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Period records: {e}")
    
    def search_periods(self, search_term: str, page: int = 1, size: int = 10) -> List[Period]:
        """Search periods by term"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Period)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        Period.period_name.contains(search_term),
                        Period.phase_name.contains(search_term),
                        Period.description.contains(search_term),
                        Period.chronology.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply ordering
                query = query.order_by(asc(Period.start_date), asc(Period.period_name))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search Period records: {e}")
    
    def update_period(self, period_id: int, update_data: Dict[str, Any]) -> Period:
        """Update existing period"""
        # Validate update data
        if update_data:
            validate_data('period', update_data)
        
        # Check if period name is being changed and if new name already exists
        if 'period_name' in update_data:
            existing_period = self.db_manager.get_by_field(Period, 'period_name', update_data['period_name'])
            if existing_period and existing_period.id_period != period_id:
                raise ValidationError(f"Period '{update_data['period_name']}' already exists")
        
        # Update period
        return self.db_manager.update(Period, period_id, update_data)
    
    def delete_period(self, period_id: int) -> bool:
        """Delete period"""
        # TODO: Check for related records (Periodizzazione) before deletion
        return self.db_manager.delete(Period, period_id)
    
    def count_periods(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count periods with optional filters"""
        return self.db_manager.count(Period, filters)
    
    # Periodizzazione (period assignments) methods
    
    def create_periodizzazione(self, periodizzazione_data: Dict[str, Any]) -> Periodizzazione:
        """Create a new periodization assignment"""
        # Validate data
        validate_data('periodizzazione', periodizzazione_data)
        
        # Verify site exists
        site = self.db_manager.get_by_field(Site, 'sito', periodizzazione_data['sito'])
        if not site:
            raise ValidationError(f"Site '{periodizzazione_data['sito']}' does not exist")
        
        # Check for duplicate periodization for same US
        if periodizzazione_data.get('us'):
            existing_periodizzazione = self._get_periodizzazione_by_us(
                periodizzazione_data['sito'],
                periodizzazione_data.get('area', ''),
                periodizzazione_data['us']
            )
            if existing_periodizzazione:
                raise ValidationError(
                    f"Periodization for US {periodizzazione_data['us']} already exists"
                )
        
        # Create periodizzazione
        return self.db_manager.create(Periodizzazione, periodizzazione_data)
    
    def get_periodizzazione_by_id(self, periodizzazione_id: int) -> Optional[Periodizzazione]:
        """Get periodizzazione by ID"""
        return self.db_manager.get_by_id(Periodizzazione, periodizzazione_id)
    
    def get_all_periodizzazioni(self, page: int = 1, size: int = 10,
                               filters: Optional[Dict[str, Any]] = None) -> List[Periodizzazione]:
        """Get all periodizations with pagination and filtering"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Periodizzazione)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(Periodizzazione, key):
                            query = query.filter(getattr(Periodizzazione, key) == value)
                
                # Apply ordering
                query = query.order_by(asc(Periodizzazione.sito), asc(Periodizzazione.us))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get Periodizzazione records: {e}")
    
    def get_periodizzazioni_by_site(self, site_name: str, page: int = 1, size: int = 10) -> List[Periodizzazione]:
        """Get all periodizations for a specific site"""
        return self.get_all_periodizzazioni(page=page, size=size, filters={'sito': site_name})
    
    def get_periodizzazioni_by_period(self, period_name: str, page: int = 1, size: int = 10) -> List[Periodizzazione]:
        """Get all periodizations for a specific period"""
        filters = {
            'periodo_iniziale': period_name
        }
        return self.get_all_periodizzazioni(page=page, size=size, filters=filters)
    
    def search_periodizzazioni(self, search_term: str, page: int = 1, size: int = 10) -> List[Periodizzazione]:
        """Search periodizations by term"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Periodizzazione)
                
                # Apply search filters
                if search_term:
                    search_filter = or_(
                        Periodizzazione.sito.contains(search_term),
                        Periodizzazione.periodo_iniziale.contains(search_term),
                        Periodizzazione.periodo_finale.contains(search_term),
                        Periodizzazione.fase_iniziale.contains(search_term),
                        Periodizzazione.fase_finale.contains(search_term),
                        Periodizzazione.cultura.contains(search_term),
                        Periodizzazione.datazione_estesa.contains(search_term)
                    )
                    query = query.filter(search_filter)
                
                # Apply ordering
                query = query.order_by(asc(Periodizzazione.sito), asc(Periodizzazione.us))
                
                # Apply pagination
                offset = (page - 1) * size
                return query.offset(offset).limit(size).all()
                
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to search Periodizzazione records: {e}")
    
    def update_periodizzazione(self, periodizzazione_id: int, update_data: Dict[str, Any]) -> Periodizzazione:
        """Update existing periodizzazione"""
        # Validate update data
        if update_data:
            validate_data('periodizzazione', update_data)
        
        # If site is being changed, verify new site exists
        if 'sito' in update_data:
            site = self.db_manager.get_by_field(Site, 'sito', update_data['sito'])
            if not site:
                raise ValidationError(f"Site '{update_data['sito']}' does not exist")
        
        # Update periodizzazione
        return self.db_manager.update(Periodizzazione, periodizzazione_id, update_data)
    
    def delete_periodizzazione(self, periodizzazione_id: int) -> bool:
        """Delete periodizzazione"""
        return self.db_manager.delete(Periodizzazione, periodizzazione_id)
    
    def count_periodizzazioni(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count periodizations with optional filters"""
        return self.db_manager.count(Periodizzazione, filters)
    
    def _get_periodizzazione_by_us(self, sito: str, area: str, us_number: int) -> Optional[Periodizzazione]:
        """Get periodizzazione by US details"""
        try:
            with self.db_manager.connection.get_session() as session:
                query = session.query(Periodizzazione).filter(
                    Periodizzazione.sito == sito,
                    Periodizzazione.us == us_number
                )
                
                if area:
                    query = query.filter(Periodizzazione.area == area)
                else:
                    query = query.filter(
                        (Periodizzazione.area == '') | (Periodizzazione.area.is_(None))
                    )
                
                return query.first()
                
        except Exception:
            return None
    
    def get_dating_summary_by_site(self, site_name: str) -> Dict[str, Any]:
        """Get dating summary for a site"""
        try:
            periodizzazioni = self.get_periodizzazioni_by_site(site_name, size=1000)
            
            # Collect periods
            periods = {}
            cultures = set()
            total_us = len(periodizzazioni)
            dated_us = 0
            
            for periodizzazione in periodizzazioni:
                if periodizzazione.periodo_iniziale:
                    dated_us += 1
                    period = periodizzazione.periodo_iniziale
                    if period not in periods:
                        periods[period] = {
                            'count': 0,
                            'us_list': [],
                            'phases': set(),
                            'reliability': {'alta': 0, 'media': 0, 'bassa': 0}
                        }
                    
                    periods[period]['count'] += 1
                    periods[period]['us_list'].append(periodizzazione.us)
                    
                    if periodizzazione.fase_iniziale:
                        periods[period]['phases'].add(periodizzazione.fase_iniziale)
                    
                    if periodizzazione.affidabilita:
                        reliability = periodizzazione.affidabilita.lower()
                        if reliability in periods[period]['reliability']:
                            periods[period]['reliability'][reliability] += 1
                
                if periodizzazione.cultura:
                    cultures.add(periodizzazione.cultura)
            
            # Convert phases sets to lists for serialization
            for period_data in periods.values():
                period_data['phases'] = list(period_data['phases'])
            
            return {
                'site': site_name,
                'total_us': total_us,
                'dated_us': dated_us,
                'dating_percentage': (dated_us / total_us * 100) if total_us > 0 else 0,
                'periods': periods,
                'cultures': list(cultures),
                'period_count': len(periods),
                'culture_count': len(cultures)
            }
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get dating summary: {e}")
    
    def get_chronological_sequence(self, site_name: str) -> List[Dict[str, Any]]:
        """Get chronological sequence for a site based on US relationships and dating"""
        try:
            # Get all periodizations for the site
            periodizzazioni = self.get_periodizzazioni_by_site(site_name, size=1000)
            
            # Group by period
            period_groups = {}
            for periodizzazione in periodizzazioni:
                period = periodizzazione.periodo_iniziale
                if period:
                    if period not in period_groups:
                        period_groups[period] = {
                            'period': period,
                            'us_list': [],
                            'date_range': None,
                            'phases': set(),
                            'cultures': set()
                        }
                    
                    period_groups[period]['us_list'].append(periodizzazione.us)
                    
                    if periodizzazione.fase_iniziale:
                        period_groups[period]['phases'].add(periodizzazione.fase_iniziale)
                    
                    if periodizzazione.cultura:
                        period_groups[period]['cultures'].add(periodizzazione.cultura)
            
            # Get formal periods to add date ranges
            all_periods = self.get_all_periods(size=1000)
            period_dates = {p.period_name: (p.start_date, p.end_date) for p in all_periods}
            
            # Add date ranges and convert sets to lists
            sequence = []
            for period_name, group in period_groups.items():
                if period_name in period_dates:
                    start_date, end_date = period_dates[period_name]
                    group['date_range'] = f"{start_date or '?'} - {end_date or '?'}"
                    group['start_date'] = start_date
                    group['end_date'] = end_date
                
                group['phases'] = list(group['phases'])
                group['cultures'] = list(group['cultures'])
                sequence.append(group)
            
            # Sort by start date
            sequence.sort(key=lambda x: x.get('start_date') or 0)
            
            return sequence
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get chronological sequence: {e}")
    
    def get_period_statistics(self) -> Dict[str, Any]:
        """Get general statistics about periods and dating"""
        try:
            # Count periods
            period_count = self.count_periods()
            
            # Count periodizations
            periodizzazione_count = self.count_periodizzazioni()
            
            # Get all periodizations to analyze
            all_periodizzazioni = self.get_all_periodizzazioni(size=10000)
            
            # Analyze reliability
            reliability_stats = {'alta': 0, 'media': 0, 'bassa': 0, 'non_specificata': 0}
            period_usage = {}
            culture_usage = {}
            sites_with_dating = set()
            
            for periodizzazione in all_periodizzazioni:
                # Reliability stats
                reliability = periodizzazione.affidabilita
                if reliability and reliability.lower() in reliability_stats:
                    reliability_stats[reliability.lower()] += 1
                else:
                    reliability_stats['non_specificata'] += 1
                
                # Period usage
                if periodizzazione.periodo_iniziale:
                    period = periodizzazione.periodo_iniziale
                    period_usage[period] = period_usage.get(period, 0) + 1
                
                # Culture usage
                if periodizzazione.cultura:
                    culture = periodizzazione.cultura
                    culture_usage[culture] = culture_usage.get(culture, 0) + 1
                
                # Sites with dating
                sites_with_dating.add(periodizzazione.sito)
            
            # Most used periods and cultures
            most_used_periods = sorted(period_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            most_used_cultures = sorted(culture_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_periods': period_count,
                'total_periodizations': periodizzazione_count,
                'sites_with_dating': len(sites_with_dating),
                'reliability_distribution': reliability_stats,
                'most_used_periods': most_used_periods,
                'most_used_cultures': most_used_cultures,
                'unique_periods_used': len(period_usage),
                'unique_cultures_used': len(culture_usage)
            }
            
        except Exception as e:
            from ..utils.exceptions import DatabaseError
            raise DatabaseError(f"Failed to get period statistics: {e}")