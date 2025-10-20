"""
Script di setup per configurare l'ambiente utente di PyArchInit-Mini.

Questo script:
1. Crea la directory ~/.pyarchinit_mini nella home dell'utente
2. Copia il database di esempio
3. Crea la configurazione di default
4. Prepara le directory per media, export, backup
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
import importlib.resources


def get_home_dir() -> Path:
    """Ottiene la home directory dell'utente."""
    return Path.home()


def get_pyarchinit_dir() -> Path:
    """Ottiene il path della directory di PyArchInit-Mini."""
    return get_home_dir() / ".pyarchinit_mini"


def setup_directories() -> dict:
    """
    Crea la struttura di directory nella home dell'utente.

    Returns:
        Dictionary con i path creati
    """
    base_dir = get_pyarchinit_dir()

    directories = {
        'base': base_dir,
        'data': base_dir / 'data',
        'media': base_dir / 'media',
        'export': base_dir / 'export',
        'backup': base_dir / 'backup',
        'config': base_dir / 'config',
        'logs': base_dir / 'logs',
    }

    print(f"Creazione directory PyArchInit-Mini in: {base_dir}")

    for name, path in directories.items():
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Creata directory: {name} -> {path}")
        else:
            print(f"  • Directory esistente: {name} -> {path}")

    # Crea sottodirectory per i media
    media_subdirs = ['images', 'videos', 'documents', 'thumbnails']
    for subdir in media_subdirs:
        subdir_path = directories['media'] / subdir
        subdir_path.mkdir(exist_ok=True)

    return directories


def copy_sample_database(directories: dict) -> Optional[Path]:
    """
    Copia il database di esempio nella directory dati dell'utente.

    Returns:
        Path al database copiato, o None se non trovato
    """
    data_dir = directories['data']
    target_db = data_dir / 'pyarchinit_mini.db'

    # Se esiste già, non sovrascrivere
    if target_db.exists():
        print(f"\n  • Database esistente trovato: {target_db}")
        return target_db

    print("\nCopia del database di esempio...")

    # Prova a trovare il database di esempio nel package
    try:
        # Prova diversi possibili percorsi
        package_paths = [
            Path(__file__).parent.parent.parent / 'data' / 'pyarchinit_mini_sample.db',
            Path(__file__).parent.parent / 'data' / 'pyarchinit_mini_sample.db',
        ]

        source_db = None
        for path in package_paths:
            if path.exists():
                source_db = path
                break

        if source_db:
            shutil.copy2(source_db, target_db)
            print(f"  ✓ Database copiato: {target_db}")
            return target_db
        else:
            print(f"  ⚠ Database di esempio non trovato nel package")
            print(f"  → Verrà creato un database vuoto al primo avvio")
            return None

    except Exception as e:
        print(f"  ⚠ Errore durante la copia del database: {e}")
        return None


def create_default_config(directories: dict):
    """
    Crea un file di configurazione di default.
    """
    config_file = directories['config'] / 'config.yaml'

    if config_file.exists():
        print(f"\n  • File di configurazione esistente: {config_file}")
        return

    print("\nCreazione configurazione di default...")

    config_content = f"""# PyArchInit-Mini Configuration
# Generato automaticamente da pyarchinit-mini-setup

# Database settings
database:
  # SQLite (default)
  url: "sqlite:///{directories['data']}/pyarchinit_mini.db"

  # Per usare PostgreSQL, decommentare e configurare:
  # url: "postgresql://user:password@localhost:5432/pyarchinit"

  # Echo SQL queries (debug)
  echo: false

# API server settings
api:
  host: "0.0.0.0"
  port: 8000
  reload: true
  workers: 1

# Web interface settings
web:
  host: "0.0.0.0"
  port: 5001  # Changed from 5000 to avoid macOS AirPlay conflict
  debug: true
  secret_key: "change-this-in-production"

# Media settings
media:
  base_dir: "{directories['media']}"
  max_upload_size: 104857600  # 100MB in bytes
  allowed_extensions:
    images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
    videos: [".mp4", ".avi", ".mov", ".wmv", ".flv"]
    documents: [".pdf", ".doc", ".docx", ".odt", ".txt"]

# Export settings
export:
  base_dir: "{directories['export']}"
  pdf_dpi: 300
  pdf_quality: 95

# Backup settings
backup:
  base_dir: "{directories['backup']}"
  auto_backup: true
  backup_interval_days: 7
  max_backups: 10

# Logging settings
logging:
  level: "INFO"
  file: "{directories['logs']}/pyarchinit_mini.log"
  max_size_mb: 10
  backup_count: 5
"""

    config_file.write_text(config_content)
    print(f"  ✓ Configurazione creata: {config_file}")


def create_readme(directories: dict):
    """
    Crea un README nella directory utente.
    """
    readme_file = directories['base'] / 'README.txt'

    readme_content = f"""
PyArchInit-Mini - Directory Utente
====================================

Questa directory contiene i dati e la configurazione di PyArchInit-Mini.

Struttura Directory:
-------------------
data/       - Database SQLite e file dati
media/      - File multimediali (immagini, video, documenti)
export/     - Export PDF e altri formati
backup/     - Backup automatici del database
config/     - File di configurazione
logs/       - Log dell'applicazione

Comandi Disponibili:
-------------------
pyarchinit-mini-api     - Avvia il server REST API (porta 8000)
pyarchinit-mini-web     - Avvia l'interfaccia web (porta 5000)
pyarchinit-mini-gui     - Avvia l'interfaccia desktop GUI
pyarchinit-mini         - Avvia l'interfaccia CLI
pyarchinit-mini-setup   - Riesegue questo setup

Configurazione:
--------------
Modifica il file config/config.yaml per personalizzare:
- Database URL (SQLite o PostgreSQL)
- Porte e host per API e Web
- Directory per media ed export
- Opzioni di backup e logging

Documentazione:
--------------
https://pyarchinit-mini.readthedocs.io/

Per Iniziare:
------------
1. Avvia il server API:
   pyarchinit-mini-api

2. Oppure usa l'interfaccia GUI:
   pyarchinit-mini-gui

3. Oppure usa l'interfaccia web:
   pyarchinit-mini-web

Database:
--------
Il database di esempio si trova in: data/pyarchinit_mini.db

Per reimpostare il database, elimina il file e riesegui:
pyarchinit-mini-setup

Supporto:
--------
GitHub: https://github.com/pyarchinit/pyarchinit-mini
Issues: https://github.com/pyarchinit/pyarchinit-mini/issues
"""

    readme_file.write_text(readme_content)
    print(f"\n  ✓ README creato: {readme_file}")


def print_summary(directories: dict):
    """
    Stampa un riepilogo dell'installazione.
    """
    print("\n" + "="*60)
    print("Setup completato con successo!")
    print("="*60)
    print(f"\nDirectory PyArchInit-Mini: {directories['base']}")
    print(f"Database: {directories['data']}/pyarchinit_mini.db")
    print(f"Configurazione: {directories['config']}/config.yaml")

    print("\nComandi disponibili:")
    print("  pyarchinit-mini-api     - Server REST API (porta 8000)")
    print("  pyarchinit-mini-web     - Interfaccia Web (porta 5000)")
    print("  pyarchinit-mini-gui     - Interfaccia Desktop GUI")
    print("  pyarchinit-mini         - Interfaccia CLI")

    print("\nProssimi passi:")
    print("  1. Avvia l'applicazione con uno dei comandi sopra")
    print("  2. Personalizza la configurazione in:")
    print(f"     {directories['config']}/config.yaml")
    print("  3. Consulta la documentazione:")
    print("     https://pyarchinit-mini.readthedocs.io/")

    print("\n" + "="*60)


def main():
    """
    Entry point principale per lo script di setup.
    """
    print("="*60)
    print("PyArchInit-Mini - Setup Ambiente Utente")
    print("="*60)

    try:
        # 1. Crea le directory
        directories = setup_directories()

        # 2. Copia il database di esempio
        copy_sample_database(directories)

        # 3. Crea la configurazione
        create_default_config(directories)

        # 4. Crea il README
        create_readme(directories)

        # 5. Riepilogo
        print_summary(directories)

        return 0

    except Exception as e:
        print(f"\n❌ Errore durante il setup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())