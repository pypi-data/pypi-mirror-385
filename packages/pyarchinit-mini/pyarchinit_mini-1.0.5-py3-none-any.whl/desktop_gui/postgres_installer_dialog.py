#!/usr/bin/env python3
"""
PostgreSQL Installation Dialog for PyArchInit-Mini
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging

logger = logging.getLogger(__name__)

class PostgreSQLInstallerDialog:
    """
    Dialog for PostgreSQL installation and setup
    """
    
    def __init__(self, parent, postgres_installer, callback=None):
        self.parent = parent
        self.postgres_installer = postgres_installer
        self.callback = callback
        self.installation_thread = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Installazione PostgreSQL")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_window()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.dialog, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create interface
        self.create_interface()
        
        # Check current status
        self.check_postgres_status()
    
    def center_window(self):
        """Center dialog window on parent"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_interface(self):
        """Create the main interface"""
        # Title
        title_label = ttk.Label(self.main_frame, 
                               text="Installazione e Configurazione PostgreSQL",
                               font=('TkDefaultFont', 12, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Status frame
        status_frame = ttk.LabelFrame(self.main_frame, text="Stato Attuale")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status labels
        self.status_label = ttk.Label(status_frame, text="Verificando stato PostgreSQL...")
        self.status_label.pack(anchor="w", padx=10, pady=5)
        
        self.version_label = ttk.Label(status_frame, text="")
        self.version_label.pack(anchor="w", padx=10, pady=2)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progresso Installazione")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Pronto per l'installazione")
        self.progress_label.pack(anchor="w", padx=10, pady=2)
        
        # Log frame
        log_frame = ttk.LabelFrame(self.main_frame, text="Log Installazione")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self.main_frame, text="Configurazione Database")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configuration fields
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.X, padx=10, pady=5)
        
        # Database name
        ttk.Label(config_grid, text="Nome Database:").grid(row=0, column=0, sticky="w", pady=2)
        self.db_name_entry = ttk.Entry(config_grid, width=20)
        self.db_name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=2)
        self.db_name_entry.insert(0, "pyarchinit_db")
        
        # Database user
        ttk.Label(config_grid, text="Utente Database:").grid(row=0, column=2, sticky="w", padx=(15, 5), pady=2)
        self.db_user_entry = ttk.Entry(config_grid, width=20)
        self.db_user_entry.grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=2)
        self.db_user_entry.insert(0, "pyarchinit")
        
        # Database password
        ttk.Label(config_grid, text="Password Database:").grid(row=1, column=0, sticky="w", pady=2)
        self.db_password_entry = ttk.Entry(config_grid, width=20, show="*")
        self.db_password_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=2)
        self.db_password_entry.insert(0, "pyarchinit")
        
        # Admin password
        ttk.Label(config_grid, text="Password Admin:").grid(row=1, column=2, sticky="w", padx=(15, 5), pady=2)
        self.admin_password_entry = ttk.Entry(config_grid, width=20, show="*")
        self.admin_password_entry.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=2)
        self.admin_password_entry.insert(0, "pyarchinit")
        
        config_grid.columnconfigure(1, weight=1)
        config_grid.columnconfigure(3, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Action buttons
        self.install_button = ttk.Button(buttons_frame, text="Installa PostgreSQL", 
                                        command=self.start_installation)
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.create_db_button = ttk.Button(buttons_frame, text="Crea Database", 
                                          command=self.create_database)
        self.create_db_button.pack(side=tk.LEFT, padx=5)
        
        self.test_button = ttk.Button(buttons_frame, text="Test Connessione", 
                                     command=self.test_connection)
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(buttons_frame, text="Chiudi", command=self.close).pack(side=tk.RIGHT)
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\\n")
        self.log_text.see(tk.END)
        self.dialog.update_idletasks()
    
    def update_progress(self, value, message=""):
        """Update progress bar and message"""
        self.progress_var.set(value)
        if message:
            self.progress_label.config(text=message)
        self.dialog.update_idletasks()
    
    def check_postgres_status(self):
        """Check current PostgreSQL status"""
        try:
            is_installed = self.postgres_installer.check_postgres_installed()
            
            if is_installed:
                version = self.postgres_installer.get_postgres_version()
                self.status_label.config(text="✓ PostgreSQL è installato")
                self.version_label.config(text=f"Versione: {version}" if version else "Versione non rilevata")
                
                # Disable install button if already installed
                self.install_button.config(state="disabled")
                self.log_message("PostgreSQL risulta già installato nel sistema")
                
                # Show connection info
                conn_info = self.postgres_installer.get_connection_info()
                self.log_message(f"Informazioni connessione predefinite:")
                self.log_message(f"  Host: {conn_info['host']}")
                self.log_message(f"  Porta: {conn_info['port']}")
                self.log_message(f"  Database: {conn_info['database']}")
                self.log_message(f"  Utente: {conn_info['user']}")
                
            else:
                self.status_label.config(text="⚠ PostgreSQL non installato")
                self.version_label.config(text="")
                self.log_message("PostgreSQL non è installato nel sistema")
                self.log_message("Cliccare 'Installa PostgreSQL' per procedere con l'installazione")
                
        except Exception as e:
            self.status_label.config(text="✗ Errore nel controllo stato")
            self.log_message(f"Errore nel controllo stato PostgreSQL: {str(e)}")
    
    def start_installation(self):
        """Start PostgreSQL installation in background thread"""
        if self.installation_thread and self.installation_thread.is_alive():
            messagebox.showwarning("Attenzione", "Installazione già in corso")
            return
        
        # Confirm installation
        if not messagebox.askyesno("Conferma Installazione", 
                                  "Procedere con l'installazione di PostgreSQL?\\n\\n"
                                  "Questo processo potrebbe richiedere diversi minuti "
                                  "e potrebbe richiedere privilegi di amministratore."):
            return
        
        # Disable buttons during installation
        self.install_button.config(state="disabled")
        self.create_db_button.config(state="disabled")
        self.test_button.config(state="disabled")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start installation thread
        self.installation_thread = threading.Thread(target=self.install_postgres_thread)
        self.installation_thread.daemon = True
        self.installation_thread.start()
    
    def install_postgres_thread(self):
        """PostgreSQL installation thread"""
        try:
            self.log_message("Avvio installazione PostgreSQL...")
            self.update_progress(10, "Preparazione installazione...")
            
            # Install PostgreSQL
            result = self.postgres_installer.install_postgres()
            
            if result['success']:
                self.update_progress(80, "PostgreSQL installato con successo")
                self.log_message(f"✓ {result['message']}")
                
                if 'version' in result:
                    self.log_message(f"Versione installata: {result['version']}")
                
                # Update status
                self.dialog.after(0, lambda: self.status_label.config(text="✓ PostgreSQL installato"))
                self.dialog.after(0, lambda: self.version_label.config(text=f"Versione: {result.get('version', 'Sconosciuta')}"))
                
                self.update_progress(100, "Installazione completata")
                self.log_message("Installazione PostgreSQL completata con successo!")
                self.log_message("Ora è possibile creare il database PyArchInit")
                
            else:
                self.update_progress(0, "Installazione fallita")
                self.log_message(f"✗ Errore installazione: {result['message']}")
                messagebox.showerror("Errore", f"Installazione fallita: {result['message']}")
                
        except Exception as e:
            self.update_progress(0, "Errore durante installazione")
            self.log_message(f"✗ Errore imprevisto: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante installazione: {str(e)}")
        
        finally:
            # Re-enable buttons
            self.dialog.after(0, lambda: self.install_button.config(state="normal"))
            self.dialog.after(0, lambda: self.create_db_button.config(state="normal"))
            self.dialog.after(0, lambda: self.test_button.config(state="normal"))
    
    def create_database(self):
        """Create PyArchInit database"""
        try:
            # Get configuration values
            db_name = self.db_name_entry.get().strip()
            db_user = self.db_user_entry.get().strip()
            db_password = self.db_password_entry.get()
            admin_password = self.admin_password_entry.get()
            
            if not all([db_name, db_user, db_password, admin_password]):
                messagebox.showerror("Errore", "Tutti i campi di configurazione sono obbligatori")
                return
            
            self.log_message("Creazione database PyArchInit...")
            self.update_progress(10, "Creazione database...")
            
            # Prepare connection parameters
            connection_params = {
                'host': 'localhost',
                'port': 5432,
                'db_name': db_name,
                'db_user': db_user,
                'db_password': db_password,
                'admin_user': 'postgres',
                'admin_password': admin_password
            }
            
            # Create database
            result = self.postgres_installer.create_pyarchinit_database(connection_params)
            
            if result['success']:
                self.update_progress(100, "Database creato con successo")
                self.log_message(f"✓ {result['message']}")
                self.log_message(f"Database: {result['database']}")
                self.log_message(f"Utente: {result['user']}")
                self.log_message(f"PostGIS: {'Abilitato' if result.get('postgis_enabled') else 'Non disponibile'}")
                self.log_message(f"Stringa connessione: {result['connection_string']}")
                
                messagebox.showinfo("Successo", 
                                   f"Database '{db_name}' creato con successo!\\n\\n"
                                   f"Stringa di connessione:\\n{result['connection_string']}")
                
                # Call callback with connection string
                if self.callback:
                    self.callback(result['connection_string'])
                    
            else:
                self.update_progress(0, "Creazione database fallita")
                self.log_message(f"✗ Errore: {result['message']}")
                messagebox.showerror("Errore", f"Creazione database fallita: {result['message']}")
                
        except Exception as e:
            self.update_progress(0, "Errore durante creazione database")
            self.log_message(f"✗ Errore imprevisto: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante creazione database: {str(e)}")
    
    def test_connection(self):
        """Test database connection"""
        try:
            db_name = self.db_name_entry.get().strip()
            db_user = self.db_user_entry.get().strip()
            db_password = self.db_password_entry.get()
            
            if not all([db_name, db_user, db_password]):
                messagebox.showerror("Errore", "Configurazione database incompleta")
                return
            
            self.log_message("Test connessione database...")
            
            # Test connection using postgres_installer
            from ..database.connection import DatabaseConnection
            
            connection_string = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"
            test_connection = DatabaseConnection(connection_string)
            
            if test_connection.test_connection():
                self.log_message("✓ Connessione database riuscita")
                messagebox.showinfo("Successo", "Connessione al database riuscita!")
            else:
                self.log_message("✗ Connessione database fallita")
                messagebox.showerror("Errore", "Connessione al database fallita")
                
            test_connection.close()
            
        except Exception as e:
            self.log_message(f"✗ Errore connessione: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante test connessione: {str(e)}")
    
    def close(self):
        """Close dialog"""
        # Check if installation is running
        if self.installation_thread and self.installation_thread.is_alive():
            if messagebox.askyesno("Conferma", "Installazione in corso. Chiudere comunque?"):
                self.dialog.destroy()
        else:
            self.dialog.destroy()