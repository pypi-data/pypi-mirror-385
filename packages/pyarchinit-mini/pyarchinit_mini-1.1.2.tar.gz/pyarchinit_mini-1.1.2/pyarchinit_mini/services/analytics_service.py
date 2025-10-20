"""
Analytics Service for PyArchInit-Mini

Provides data aggregation and statistics for dashboard charts and analytics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func, distinct

from ..database.manager import DatabaseManager
from ..models.site import Site
from ..models.us import US
from ..models.inventario_materiali import InventarioMateriali


class AnalyticsService:
    """Service for generating analytics and statistics"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize analytics service

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get overview statistics for dashboard

        Returns:
            Dictionary with overview stats
        """
        with self.db_manager.connection.get_session() as session:
            total_sites = session.query(func.count(Site.id_sito)).scalar() or 0
            total_us = session.query(func.count(US.id_us)).scalar() or 0
            total_inventario = session.query(func.count(InventarioMateriali.id_invmat)).scalar() or 0

            # Get distinct values
            total_regions = session.query(func.count(distinct(Site.regione))).filter(
                Site.regione.isnot(None),
                Site.regione != ''
            ).scalar() or 0

            total_provinces = session.query(func.count(distinct(Site.provincia))).filter(
                Site.provincia.isnot(None),
                Site.provincia != ''
            ).scalar() or 0

            return {
                'total_sites': total_sites,
                'total_us': total_us,
                'total_inventario': total_inventario,
                'total_regions': total_regions,
                'total_provinces': total_provinces
            }

    def get_sites_by_region(self) -> Dict[str, int]:
        """
        Get count of sites grouped by region

        Returns:
            Dictionary mapping region names to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                Site.regione,
                func.count(Site.id_sito).label('count')
            ).filter(
                Site.regione.isnot(None),
                Site.regione != ''
            ).group_by(Site.regione).all()

            return {region: count for region, count in results if region}

    def get_sites_by_province(self, limit: int = 10) -> Dict[str, int]:
        """
        Get count of sites grouped by province

        Args:
            limit: Maximum number of provinces to return

        Returns:
            Dictionary mapping province names to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                Site.provincia,
                func.count(Site.id_sito).label('count')
            ).filter(
                Site.provincia.isnot(None),
                Site.provincia != ''
            ).group_by(Site.provincia).order_by(
                func.count(Site.id_sito).desc()
            ).limit(limit).all()

            return {provincia: count for provincia, count in results if provincia}

    def get_us_by_period(self) -> Dict[str, int]:
        """
        Get count of US grouped by initial period

        Returns:
            Dictionary mapping period names to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                US.periodo_iniziale,
                func.count(US.id_us).label('count')
            ).filter(
                US.periodo_iniziale.isnot(None),
                US.periodo_iniziale != ''
            ).group_by(US.periodo_iniziale).all()

            return {period: count for period, count in results if period}

    def get_us_by_type(self) -> Dict[str, int]:
        """
        Get count of US grouped by unit type

        Returns:
            Dictionary mapping unit types to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                US.unita_tipo,
                func.count(US.id_us).label('count')
            ).filter(
                US.unita_tipo.isnot(None),
                US.unita_tipo != ''
            ).group_by(US.unita_tipo).all()

            return {unit_type: count for unit_type, count in results if unit_type}

    def get_inventario_by_type(self, limit: int = 10) -> Dict[str, int]:
        """
        Get count of inventory items grouped by artifact type

        Args:
            limit: Maximum number of types to return

        Returns:
            Dictionary mapping artifact types to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                InventarioMateriali.tipo_reperto,
                func.count(InventarioMateriali.id_invmat).label('count')
            ).filter(
                InventarioMateriali.tipo_reperto.isnot(None),
                InventarioMateriali.tipo_reperto != ''
            ).group_by(InventarioMateriali.tipo_reperto).order_by(
                func.count(InventarioMateriali.id_invmat).desc()
            ).limit(limit).all()

            return {tipo: count for tipo, count in results if tipo}

    def get_inventario_by_conservation(self) -> Dict[str, int]:
        """
        Get count of inventory items grouped by conservation state

        Returns:
            Dictionary mapping conservation states to counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                InventarioMateriali.stato_conservazione,
                func.count(InventarioMateriali.id_invmat).label('count')
            ).filter(
                InventarioMateriali.stato_conservazione.isnot(None),
                InventarioMateriali.stato_conservazione != ''
            ).group_by(InventarioMateriali.stato_conservazione).all()

            return {state: count for state, count in results if state}

    def get_us_by_site(self, limit: int = 10) -> Dict[str, int]:
        """
        Get count of US grouped by site

        Args:
            limit: Maximum number of sites to return

        Returns:
            Dictionary mapping site names to US counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                US.sito,
                func.count(US.id_us).label('count')
            ).filter(
                US.sito.isnot(None),
                US.sito != ''
            ).group_by(US.sito).order_by(
                func.count(US.id_us).desc()
            ).limit(limit).all()

            return {site: count for site, count in results if site}

    def get_inventario_by_site(self, limit: int = 10) -> Dict[str, int]:
        """
        Get count of inventory items grouped by site

        Args:
            limit: Maximum number of sites to return

        Returns:
            Dictionary mapping site names to inventory counts
        """
        with self.db_manager.connection.get_session() as session:
            results = session.query(
                InventarioMateriali.sito,
                func.count(InventarioMateriali.id_invmat).label('count')
            ).filter(
                InventarioMateriali.sito.isnot(None),
                InventarioMateriali.sito != ''
            ).group_by(InventarioMateriali.sito).order_by(
                func.count(InventarioMateriali.id_invmat).desc()
            ).limit(limit).all()

            return {site: count for site, count in results if site}

    def get_complete_dashboard_data(self) -> Dict[str, Any]:
        """
        Get all analytics data for dashboard in a single call

        Returns:
            Dictionary with all dashboard data
        """
        return {
            'overview': self.get_overview_stats(),
            'sites_by_region': self.get_sites_by_region(),
            'sites_by_province': self.get_sites_by_province(limit=10),
            'us_by_period': self.get_us_by_period(),
            'us_by_type': self.get_us_by_type(),
            'us_by_site': self.get_us_by_site(limit=10),
            'inventario_by_type': self.get_inventario_by_type(limit=10),
            'inventario_by_conservation': self.get_inventario_by_conservation(),
            'inventario_by_site': self.get_inventario_by_site(limit=10)
        }
