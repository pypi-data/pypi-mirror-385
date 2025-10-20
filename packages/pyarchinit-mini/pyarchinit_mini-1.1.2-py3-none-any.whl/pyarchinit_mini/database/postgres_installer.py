"""
PostgreSQL Installation and Setup Manager for PyArchInit-Mini
"""

import os
import sys
import platform
import subprocess
import urllib.request
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import shutil
import tempfile

logger = logging.getLogger(__name__)

class PostgreSQLInstaller:
    """
    Manages PostgreSQL installation on different platforms
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.postgres_data_dir = None
        self.postgres_port = 5432
        self.postgres_user = "postgres"
        self.postgres_password = "pyarchinit"
        
    def check_postgres_installed(self) -> bool:
        """Check if PostgreSQL is already installed and accessible"""
        try:
            # Try to find psql command
            if shutil.which('psql'):
                return True
            
            # Check common installation paths
            common_paths = [
                '/usr/bin/psql',
                '/usr/local/bin/psql',
                '/opt/homebrew/bin/psql',
                'C:\\Program Files\\PostgreSQL\\*\\bin\\psql.exe',
                '/Applications/Postgres.app/Contents/Versions/*/bin/psql'
            ]
            
            for path in common_paths:
                if os.path.exists(path) or any(Path().glob(path)):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking PostgreSQL installation: {e}")
            return False
    
    def get_postgres_version(self) -> Optional[str]:
        """Get installed PostgreSQL version"""
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from output like "psql (PostgreSQL) 14.9"
                import re
                match = re.search(r'(\d+\.?\d*)', result.stdout)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None
    
    def install_postgres_macos(self) -> Dict[str, Any]:
        """Install PostgreSQL on macOS using Homebrew"""
        try:
            # Check if Homebrew is installed
            if not shutil.which('brew'):
                return {
                    'success': False,
                    'message': 'Homebrew non trovato. Installare prima Homebrew da https://brew.sh'
                }
            
            logger.info("Installing PostgreSQL via Homebrew...")
            
            # Update Homebrew
            subprocess.run(['brew', 'update'], check=True, capture_output=True)
            
            # Install PostgreSQL
            result = subprocess.run(['brew', 'install', 'postgresql@14'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': f'Errore installazione PostgreSQL: {result.stderr}'
                }
            
            # Start PostgreSQL service
            subprocess.run(['brew', 'services', 'start', 'postgresql@14'], 
                          capture_output=True)
            
            return {
                'success': True,
                'message': 'PostgreSQL installato con successo via Homebrew',
                'version': '14',
                'service': 'postgresql@14'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Timeout durante installazione PostgreSQL'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore durante installazione PostgreSQL: {e}'
            }
    
    def install_postgres_windows(self) -> Dict[str, Any]:
        """Install PostgreSQL on Windows"""
        try:
            # Download PostgreSQL installer
            installer_url = "https://get.enterprisedb.com/postgresql/postgresql-14.9-1-windows-x64.exe"
            installer_path = os.path.join(tempfile.gettempdir(), "postgresql_installer.exe")
            
            logger.info("Downloading PostgreSQL installer for Windows...")
            urllib.request.urlretrieve(installer_url, installer_path)
            
            # Prepare installation command
            install_cmd = [
                installer_path,
                '--mode', 'unattended',
                '--superpassword', self.postgres_password,
                '--servicename', 'postgresql-14',
                '--servicepassword', self.postgres_password,
                '--serverport', str(self.postgres_port)
            ]
            
            # Run installer
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
            
            # Clean up installer
            if os.path.exists(installer_path):
                os.remove(installer_path)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'PostgreSQL installato con successo',
                    'version': '14.9',
                    'port': self.postgres_port,
                    'password': self.postgres_password
                }
            else:
                return {
                    'success': False,
                    'message': f'Errore installazione PostgreSQL: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore durante installazione PostgreSQL: {e}'
            }
    
    def install_postgres_linux(self) -> Dict[str, Any]:
        """Install PostgreSQL on Linux"""
        try:
            # Detect Linux distribution
            if os.path.exists('/etc/debian_version'):
                return self._install_postgres_debian()
            elif os.path.exists('/etc/redhat-release'):
                return self._install_postgres_redhat()
            else:
                return {
                    'success': False,
                    'message': 'Distribuzione Linux non supportata automaticamente. Installare PostgreSQL manualmente.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore durante installazione PostgreSQL: {e}'
            }
    
    def _install_postgres_debian(self) -> Dict[str, Any]:
        """Install PostgreSQL on Debian/Ubuntu"""
        try:
            # Update package list
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            
            # Install PostgreSQL
            subprocess.run(['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib'], 
                          check=True, capture_output=True, timeout=300)
            
            # Start PostgreSQL service
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                          capture_output=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], 
                          capture_output=True)
            
            # Set password for postgres user
            subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', 
                          f"ALTER USER postgres PASSWORD '{self.postgres_password}';"], 
                          capture_output=True)
            
            return {
                'success': True,
                'message': 'PostgreSQL installato con successo su Debian/Ubuntu',
                'version': 'latest',
                'password': self.postgres_password
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Errore installazione PostgreSQL: {e}'
            }
    
    def _install_postgres_redhat(self) -> Dict[str, Any]:
        """Install PostgreSQL on RedHat/CentOS/Fedora"""
        try:
            # Try dnf first (Fedora), then yum (CentOS/RHEL)
            package_manager = 'dnf' if shutil.which('dnf') else 'yum'
            
            # Install PostgreSQL
            subprocess.run(['sudo', package_manager, 'install', '-y', 'postgresql-server', 'postgresql'], 
                          check=True, capture_output=True, timeout=300)
            
            # Initialize database
            subprocess.run(['sudo', 'postgresql-setup', 'initdb'], 
                          capture_output=True)
            
            # Start PostgreSQL service
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                          capture_output=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], 
                          capture_output=True)
            
            return {
                'success': True,
                'message': 'PostgreSQL installato con successo su RedHat/CentOS/Fedora',
                'version': 'latest'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Errore installazione PostgreSQL: {e}'
            }
    
    def create_pyarchinit_database(self, connection_params: Dict[str, str]) -> Dict[str, Any]:
        """Create PyArchInit database and user"""
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # Connect as superuser
            conn = psycopg2.connect(
                host=connection_params.get('host', 'localhost'),
                port=connection_params.get('port', 5432),
                user=connection_params.get('admin_user', 'postgres'),
                password=connection_params.get('admin_password', self.postgres_password),
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cur = conn.cursor()
            
            # Create user if not exists
            db_user = connection_params.get('db_user', 'pyarchinit')
            db_password = connection_params.get('db_password', 'pyarchinit')
            
            cur.execute(f"""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{db_user}') THEN
                        CREATE USER {db_user} WITH PASSWORD '{db_password}';
                    END IF;
                END $$;
            """)
            
            # Create database if not exists
            db_name = connection_params.get('db_name', 'pyarchinit_db')
            
            cur.execute(f"""
                SELECT 1 FROM pg_database WHERE datname = '{db_name}'
            """)
            
            if not cur.fetchone():
                cur.execute(f"""
                    CREATE DATABASE {db_name}
                    WITH OWNER = {db_user}
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'en_US.UTF-8'
                    LC_CTYPE = 'en_US.UTF-8'
                    TEMPLATE = template0;
                """)
            
            # Grant privileges
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
            
            cur.close()
            conn.close()
            
            # Connect to new database and create PostGIS extension
            conn = psycopg2.connect(
                host=connection_params.get('host', 'localhost'),
                port=connection_params.get('port', 5432),
                user=db_user,
                password=db_password,
                database=db_name
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cur = conn.cursor()
            
            # Try to create PostGIS extension (optional for pyarchinit-mini)
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                postgis_enabled = True
            except Exception:
                postgis_enabled = False
                logger.warning("PostGIS extension not available")
            
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': f'Database {db_name} creato con successo',
                'database': db_name,
                'user': db_user,
                'postgis_enabled': postgis_enabled,
                'connection_string': f"postgresql://{db_user}:{db_password}@{connection_params.get('host', 'localhost')}:{connection_params.get('port', 5432)}/{db_name}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Errore creazione database: {e}'
            }
    
    def install_postgres(self) -> Dict[str, Any]:
        """Install PostgreSQL based on the current platform"""
        if self.check_postgres_installed():
            return {
                'success': True,
                'message': 'PostgreSQL già installato',
                'version': self.get_postgres_version()
            }
        
        logger.info(f"Installing PostgreSQL on {self.system}...")
        
        if self.system == 'darwin':
            return self.install_postgres_macos()
        elif self.system == 'windows':
            return self.install_postgres_windows()
        elif self.system == 'linux':
            return self.install_postgres_linux()
        else:
            return {
                'success': False,
                'message': f'Sistema operativo {self.system} non supportato'
            }
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get default connection information"""
        return {
            'host': 'localhost',
            'port': self.postgres_port,
            'database': 'pyarchinit_db',
            'user': 'pyarchinit',
            'password': 'pyarchinit',
            'connection_string': f"postgresql://pyarchinit:pyarchinit@localhost:{self.postgres_port}/pyarchinit_db"
        }