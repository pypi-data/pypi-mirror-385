"""
Export/Import Service for PyArchInit-Mini

Handles Excel and CSV export/import for Sites, US, and Inventario Materiali
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ExportImportService:
    """Service for exporting and importing data to/from Excel and CSV"""

    def __init__(self, db_manager):
        """
        Initialize export/import service

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def export_to_excel(self, data: List[Dict[str, Any]], output_path: str,
                       sheet_name: str = "Sheet1") -> str:
        """
        Export data to Excel file

        Args:
            data: List of dictionaries containing data
            output_path: Path for output Excel file
            sheet_name: Name of the sheet (default: Sheet1)

        Returns:
            Path to created Excel file

        Raises:
            ImportError: If pandas or openpyxl not installed
            ValueError: If data is empty
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas and openpyxl are required for Excel export. "
                "Install with: pip install 'pyarchinit-mini[export]'"
            )

        if not data:
            raise ValueError("No data to export")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Export to Excel
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(output_path, sheet_name=sheet_name, index=False, engine='openpyxl')

        logger.info(f"Exported {len(data)} records to Excel: {output_path}")
        return str(output_path)

    def export_to_csv(self, data: List[Dict[str, Any]], output_path: str,
                     delimiter: str = ',', encoding: str = 'utf-8') -> str:
        """
        Export data to CSV file

        Args:
            data: List of dictionaries containing data
            output_path: Path for output CSV file
            delimiter: CSV delimiter (default: ',')
            encoding: File encoding (default: 'utf-8')

        Returns:
            Path to created CSV file

        Raises:
            ImportError: If pandas not installed
            ValueError: If data is empty
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for CSV export. "
                "Install with: pip install 'pyarchinit-mini[export]'"
            )

        if not data:
            raise ValueError("No data to export")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Export to CSV
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, sep=delimiter, index=False, encoding=encoding)

        logger.info(f"Exported {len(data)} records to CSV: {output_path}")
        return str(output_path)

    def import_from_excel(self, file_path: str, sheet_name: Union[str, int] = 0) -> List[Dict[str, Any]]:
        """
        Import data from Excel file

        Args:
            file_path: Path to Excel file
            sheet_name: Name or index of sheet to read (default: 0)

        Returns:
            List of dictionaries containing imported data

        Raises:
            ImportError: If pandas or openpyxl not installed
            FileNotFoundError: If file doesn't exist
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas and openpyxl are required for Excel import. "
                "Install with: pip install 'pyarchinit-mini[export]'"
            )

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

        # Convert NaN to None for database compatibility
        df = df.where(pd.notnull(df), None)

        # Convert to list of dicts
        data = df.to_dict('records')

        logger.info(f"Imported {len(data)} records from Excel: {file_path}")
        return data

    def import_from_csv(self, file_path: str, delimiter: str = ',',
                       encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Import data from CSV file

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter (default: ',')
            encoding: File encoding (default: 'utf-8')

        Returns:
            List of dictionaries containing imported data

        Raises:
            ImportError: If pandas not installed
            FileNotFoundError: If file doesn't exist
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for CSV import. "
                "Install with: pip install 'pyarchinit-mini[export]'"
            )

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        # Read CSV file
        df = pd.read_csv(file_path, sep=delimiter, encoding=encoding)

        # Convert NaN to None for database compatibility
        df = df.where(pd.notnull(df), None)

        # Convert to list of dicts
        data = df.to_dict('records')

        logger.info(f"Imported {len(data)} records from CSV: {file_path}")
        return data

    def export_sites_to_excel(self, output_path: str) -> str:
        """Export all sites to Excel"""
        from ..models.site import Site

        with self.db_manager.connection.get_session() as session:
            sites = session.query(Site).all()
            data = [site.to_dict() for site in sites]

        return self.export_to_excel(data, output_path, sheet_name="Sites")

    def export_sites_to_csv(self, output_path: str) -> str:
        """Export all sites to CSV"""
        from ..models.site import Site

        with self.db_manager.connection.get_session() as session:
            sites = session.query(Site).all()
            data = [site.to_dict() for site in sites]

        return self.export_to_csv(data, output_path)

    def export_us_to_excel(self, output_path: str, site_name: Optional[str] = None) -> str:
        """
        Export US to Excel

        Args:
            output_path: Output file path
            site_name: Optional site name to filter by
        """
        from ..models.us import US

        with self.db_manager.connection.get_session() as session:
            query = session.query(US)
            if site_name:
                query = query.filter(US.sito == site_name)

            us_records = query.all()
            data = [us.to_dict() for us in us_records]

        sheet_name = f"US_{site_name}" if site_name else "US"
        return self.export_to_excel(data, output_path, sheet_name=sheet_name)

    def export_us_to_csv(self, output_path: str, site_name: Optional[str] = None) -> str:
        """Export US to CSV"""
        from ..models.us import US

        with self.db_manager.connection.get_session() as session:
            query = session.query(US)
            if site_name:
                query = query.filter(US.sito == site_name)

            us_records = query.all()
            data = [us.to_dict() for us in us_records]

        return self.export_to_csv(data, output_path)

    def export_inventario_to_excel(self, output_path: str, site_name: Optional[str] = None) -> str:
        """
        Export Inventario to Excel

        Args:
            output_path: Output file path
            site_name: Optional site name to filter by
        """
        from ..models.inventario_materiali import InventarioMateriali

        with self.db_manager.connection.get_session() as session:
            query = session.query(InventarioMateriali)
            if site_name:
                query = query.filter(InventarioMateriali.sito == site_name)

            inventory = query.all()
            data = [item.to_dict() for item in inventory]

        sheet_name = f"Inventario_{site_name}" if site_name else "Inventario"
        return self.export_to_excel(data, output_path, sheet_name=sheet_name)

    def export_inventario_to_csv(self, output_path: str, site_name: Optional[str] = None) -> str:
        """Export Inventario to CSV"""
        from ..models.inventario_materiali import InventarioMateriali

        with self.db_manager.connection.get_session() as session:
            query = session.query(InventarioMateriali)
            if site_name:
                query = query.filter(InventarioMateriali.sito == site_name)

            inventory = query.all()
            data = [item.to_dict() for item in inventory]

        return self.export_to_csv(data, output_path)

    def batch_import_sites_from_csv(self, file_path: str, skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Batch import sites from CSV

        Args:
            file_path: Path to CSV file
            skip_duplicates: Skip sites that already exist (default: True)

        Returns:
            Dictionary with import statistics
        """
        from ..models.site import Site
        from ..utils.validators import SiteValidator

        data = self.import_from_csv(file_path)

        imported = 0
        skipped = 0
        errors = []

        with self.db_manager.connection.get_session() as session:
            for row in data:
                try:
                    # Validate data
                    SiteValidator.validate(row)

                    # Check if site already exists
                    existing = session.query(Site).filter(
                        Site.sito == row['sito']
                    ).first()

                    if existing and skip_duplicates:
                        skipped += 1
                        continue

                    # Create new site
                    site = Site(**row)
                    session.add(site)
                    imported += 1

                except Exception as e:
                    errors.append({
                        'row': row,
                        'error': str(e)
                    })

            session.commit()

        logger.info(f"Batch import completed: {imported} imported, {skipped} skipped, {len(errors)} errors")

        return {
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'total': len(data)
        }

    def batch_import_us_from_csv(self, file_path: str, skip_duplicates: bool = True) -> Dict[str, Any]:
        """Batch import US from CSV"""
        from ..models.us import US
        from ..utils.validators import USValidator

        data = self.import_from_csv(file_path)

        imported = 0
        skipped = 0
        errors = []

        with self.db_manager.connection.get_session() as session:
            for row in data:
                try:
                    # Validate data
                    USValidator.validate(row)

                    # Check if US already exists
                    existing = session.query(US).filter(
                        US.sito == row['sito'],
                        US.us == row['us']
                    ).first()

                    if existing and skip_duplicates:
                        skipped += 1
                        continue

                    # Create new US
                    us = US(**row)
                    session.add(us)
                    imported += 1

                except Exception as e:
                    errors.append({
                        'row': row,
                        'error': str(e)
                    })

            session.commit()

        logger.info(f"Batch import US completed: {imported} imported, {skipped} skipped, {len(errors)} errors")

        return {
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'total': len(data)
        }

    def batch_import_inventario_from_csv(self, file_path: str, skip_duplicates: bool = True) -> Dict[str, Any]:
        """Batch import Inventario from CSV"""
        from ..models.inventario_materiali import InventarioMateriali
        from ..utils.validators import InventarioValidator

        data = self.import_from_csv(file_path)

        imported = 0
        skipped = 0
        errors = []

        with self.db_manager.connection.get_session() as session:
            for row in data:
                try:
                    # Validate data
                    InventarioValidator.validate(row)

                    # Check if inventory item already exists
                    existing = session.query(InventarioMateriali).filter(
                        InventarioMateriali.sito == row['sito'],
                        InventarioMateriali.numero_inventario == row['numero_inventario']
                    ).first()

                    if existing and skip_duplicates:
                        skipped += 1
                        continue

                    # Create new inventory item
                    item = InventarioMateriali(**row)
                    session.add(item)
                    imported += 1

                except Exception as e:
                    errors.append({
                        'row': row,
                        'error': str(e)
                    })

            session.commit()

        logger.info(f"Batch import Inventario completed: {imported} imported, {skipped} skipped, {len(errors)} errors")

        return {
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'total': len(data)
        }
