"""
CLI commands for Export/Import functionality
"""

import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
import os

console = Console()


@click.group()
def export_import():
    """Export and import data to/from Excel and CSV"""
    pass


@export_import.command('export-sites')
@click.option('--format', '-f', type=click.Choice(['excel', 'csv']), default='csv',
              help='Export format (excel or csv)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def export_sites(format, output, database_url):
    """Export all sites to Excel or CSV"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Export
        console.print(f"[cyan]Esportando siti in formato {format.upper()}...[/cyan]")

        if format == 'excel':
            output_path = service.export_sites_to_excel(output)
        else:
            output_path = service.export_sites_to_csv(output)

        console.print(f"[green]✓ Export completato: {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'export: {e}[/red]")
        raise click.Abort()


@export_import.command('export-us')
@click.option('--format', '-f', type=click.Choice(['excel', 'csv']), default='csv',
              help='Export format (excel or csv)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path')
@click.option('--site', '-s', help='Filter by site name (optional)')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def export_us(format, output, site, database_url):
    """Export US (Stratigraphic Units) to Excel or CSV"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Export
        site_msg = f" per sito '{site}'" if site else ""
        console.print(f"[cyan]Esportando US{site_msg} in formato {format.upper()}...[/cyan]")

        if format == 'excel':
            output_path = service.export_us_to_excel(output, site)
        else:
            output_path = service.export_us_to_csv(output, site)

        console.print(f"[green]✓ Export completato: {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'export: {e}[/red]")
        raise click.Abort()


@export_import.command('export-inventario')
@click.option('--format', '-f', type=click.Choice(['excel', 'csv']), default='csv',
              help='Export format (excel or csv)')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path')
@click.option('--site', '-s', help='Filter by site name (optional)')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def export_inventario(format, output, site, database_url):
    """Export Inventario (material finds) to Excel or CSV"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Export
        site_msg = f" per sito '{site}'" if site else ""
        console.print(f"[cyan]Esportando inventario{site_msg} in formato {format.upper()}...[/cyan]")

        if format == 'excel':
            output_path = service.export_inventario_to_excel(output, site)
        else:
            output_path = service.export_inventario_to_csv(output, site)

        console.print(f"[green]✓ Export completato: {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'export: {e}[/red]")
        raise click.Abort()


@export_import.command('import-sites')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--skip-duplicates/--no-skip-duplicates', default=True,
              help='Skip duplicate records (default: yes)')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def import_sites(csv_file, skip_duplicates, database_url):
    """Import sites from CSV file"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Import
        console.print(f"[cyan]Importando siti da {csv_file}...[/cyan]")
        result = service.batch_import_sites_from_csv(csv_file, skip_duplicates)

        # Display results
        table = Table(title="Risultati Import Siti")
        table.add_column("Statistica", style="cyan")
        table.add_column("Valore", style="green")

        table.add_row("Totale record", str(result['total']))
        table.add_row("Importati", str(result['imported']))
        table.add_row("Saltati (duplicati)", str(result['skipped']))
        table.add_row("Errori", str(len(result['errors'])))

        console.print(table)

        # Show errors if any
        if result['errors']:
            console.print("\n[yellow]Primi errori riscontrati:[/yellow]")
            for i, err in enumerate(result['errors'][:5], 1):
                console.print(f"{i}. {err['error']}")

        if result['imported'] > 0:
            console.print(f"\n[green]✓ Import completato con successo[/green]")
        else:
            console.print(f"\n[yellow]⚠ Nessun record importato[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'import: {e}[/red]")
        raise click.Abort()


@export_import.command('import-us')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--skip-duplicates/--no-skip-duplicates', default=True,
              help='Skip duplicate records (default: yes)')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def import_us(csv_file, skip_duplicates, database_url):
    """Import US from CSV file"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Import
        console.print(f"[cyan]Importando US da {csv_file}...[/cyan]")
        result = service.batch_import_us_from_csv(csv_file, skip_duplicates)

        # Display results
        table = Table(title="Risultati Import US")
        table.add_column("Statistica", style="cyan")
        table.add_column("Valore", style="green")

        table.add_row("Totale record", str(result['total']))
        table.add_row("Importati", str(result['imported']))
        table.add_row("Saltati (duplicati)", str(result['skipped']))
        table.add_row("Errori", str(len(result['errors'])))

        console.print(table)

        # Show errors if any
        if result['errors']:
            console.print("\n[yellow]Primi errori riscontrati:[/yellow]")
            for i, err in enumerate(result['errors'][:5], 1):
                console.print(f"{i}. {err['error']}")

        if result['imported'] > 0:
            console.print(f"\n[green]✓ Import completato con successo[/green]")
        else:
            console.print(f"\n[yellow]⚠ Nessun record importato[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'import: {e}[/red]")
        raise click.Abort()


@export_import.command('import-inventario')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--skip-duplicates/--no-skip-duplicates', default=True,
              help='Skip duplicate records (default: yes)')
@click.option('--database-url', '-d', envvar='DATABASE_URL',
              help='Database connection URL')
def import_inventario(csv_file, skip_duplicates, database_url):
    """Import Inventario from CSV file"""
    try:
        from pyarchinit_mini.database import DatabaseConnection, DatabaseManager
        from pyarchinit_mini.services.export_import_service import ExportImportService

        # Setup database
        db_url = database_url or "sqlite:///./pyarchinit_mini.db"
        db_conn = DatabaseConnection(db_url)
        db_manager = DatabaseManager(db_conn)

        # Initialize service
        service = ExportImportService(db_manager)

        # Import
        console.print(f"[cyan]Importando inventario da {csv_file}...[/cyan]")
        result = service.batch_import_inventario_from_csv(csv_file, skip_duplicates)

        # Display results
        table = Table(title="Risultati Import Inventario")
        table.add_column("Statistica", style="cyan")
        table.add_column("Valore", style="green")

        table.add_row("Totale record", str(result['total']))
        table.add_row("Importati", str(result['imported']))
        table.add_row("Saltati (duplicati)", str(result['skipped']))
        table.add_row("Errori", str(len(result['errors'])))

        console.print(table)

        # Show errors if any
        if result['errors']:
            console.print("\n[yellow]Primi errori riscontrati:[/yellow]")
            for i, err in enumerate(result['errors'][:5], 1):
                console.print(f"{i}. {err['error']}")

        if result['imported'] > 0:
            console.print(f"\n[green]✓ Import completato con successo[/green]")
        else:
            console.print(f"\n[yellow]⚠ Nessun record importato[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Errore durante l'import: {e}[/red]")
        raise click.Abort()


if __name__ == '__main__':
    export_import()
