#!/usr/bin/env python3
"""
Desktop GUI for PyArchInit-Mini using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import tempfile
import threading

# Add parent directory to path for imports
sys.path.append('..')

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService
from pyarchinit_mini.services.periodizzazione_service import PeriodizzazioneService
from pyarchinit_mini.services.media_service import MediaService
from pyarchinit_mini.services.thesaurus_service import ThesaurusService
from pyarchinit_mini.database.postgres_installer import PostgreSQLInstaller
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
from pyarchinit_mini.media_manager.media_handler import MediaHandler

# Import dialog classes
from .dialogs import (
    SiteDialog,
    InventarioDialog,
    HarrisMatrixDialog,
    PDFExportDialog,
    MediaManagerDialog,
    StatisticsDialog,
    DatabaseConfigDialog
)
from .us_dialog_extended import ExtendedUSDialog
from .inventario_dialog_extended import ExtendedInventarioDialog
from .thesaurus_dialog import ThesaurusDialog
from .postgres_installer_dialog import PostgreSQLInstallerDialog
from .export_import_dialog import show_export_import_dialog
from .analytics_dialog import show_analytics_dialog
from .graphml_export_dialog import show_graphml_export_dialog

class PyArchInitGUI:
    """Main GUI application for PyArchInit-Mini"""
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("PyArchInit-Mini - Archaeological Data Management")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize database and services
        self.setup_database()
        
        # Initialize status variables
        self.current_site = tk.StringVar()
        self.status_text = tk.StringVar(value="Pronto")
        
        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        
        # Load initial data
        self.refresh_data()
        
    def setup_database(self):
        """Initialize database connection and services"""
        try:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./pyarchinit_mini.db")
            self.db_conn = DatabaseConnection.from_url(database_url)
            self.db_conn.create_tables()
            self.db_manager = DatabaseManager(self.db_conn)
            
            # Run database migrations
            try:
                migrations_applied = self.db_manager.run_migrations()
                if migrations_applied > 0:
                    print(f"Applied {migrations_applied} database migrations")
            except Exception as e:
                print(f"Warning: Migration error: {e}")
                # Continue anyway - migrations are not critical for basic functionality
            
            # Initialize services
            self.site_service = SiteService(self.db_manager)
            self.us_service = USService(self.db_manager)
            self.inventario_service = InventarioService(self.db_manager)
            self.periodizzazione_service = PeriodizzazioneService(self.db_manager)
            self.media_service = MediaService(self.db_manager)
            self.thesaurus_service = ThesaurusService(self.db_manager)
            self.postgres_installer = PostgreSQLInstaller()
            self.matrix_generator = HarrisMatrixGenerator(self.db_manager, self.us_service)
            self.matrix_visualizer = PyArchInitMatrixVisualizer()
            self.pdf_generator = PDFGenerator()
            self.media_handler = MediaHandler()
            
            print("Database and services initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure custom styles
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#2E86AB")
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo Database SQLite", command=self.create_new_database)
        file_menu.add_separator()
        file_menu.add_command(label="Nuovo Sito", command=self.new_site_dialog)
        file_menu.add_command(label="Nuova US", command=self.new_us_dialog)
        file_menu.add_command(label="Nuovo Reperto", command=self.new_inventario_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Configura Database", command=self.show_database_config)
        file_menu.add_command(label="Installa PostgreSQL", command=self.show_postgres_installer)
        file_menu.add_separator()
        file_menu.add_command(label="Carica Database di Esempio", command=self.load_sample_database)
        file_menu.add_command(label="Import Database", command=self.import_database)
        file_menu.add_command(label="Export Database", command=self.export_database)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizza", menu=view_menu)
        view_menu.add_command(label="Dashboard", command=lambda: self.show_tab("dashboard"))
        view_menu.add_command(label="Siti", command=lambda: self.show_tab("sites"))
        view_menu.add_command(label="US", command=lambda: self.show_tab("us"))
        view_menu.add_command(label="Inventario", command=lambda: self.show_tab("inventario"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Harris Matrix", command=self.show_harris_matrix_dialog)
        tools_menu.add_command(label="Export GraphML (yEd)", command=self.show_graphml_export_dialog)
        tools_menu.add_separator()
        tools_menu.add_command(label="Gestione Thesaurus", command=self.show_thesaurus_dialog)
        tools_menu.add_separator()
        tools_menu.add_command(label="Media Manager", command=self.show_media_manager)
        tools_menu.add_command(label="Export PDF", command=self.show_pdf_export_dialog)
        tools_menu.add_command(label="Export/Import Dati", command=self.show_export_import_dialog)
        tools_menu.add_command(label="Statistiche", command=self.show_statistics_dialog)
        tools_menu.add_command(label="Analytics Dashboard", command=self.show_analytics_dashboard)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Informazioni", command=self.show_about_dialog)
        help_menu.add_command(label="Guida Utente", command=self.show_help_dialog)
    
    def create_main_interface(self):
        """Create main application interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_sites_tab()
        self.create_us_tab()
        self.create_inventario_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Create application toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(toolbar, text="PyArchInit-Mini", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Current site selection
        site_frame = ttk.Frame(toolbar)
        site_frame.pack(side=tk.RIGHT, padx=10)
        ttk.Label(site_frame, text="Sito Corrente:").pack(side=tk.LEFT, padx=(0, 5))
        self.site_combobox = ttk.Combobox(site_frame, textvariable=self.current_site, width=30)
        self.site_combobox.pack(side=tk.LEFT)
        self.site_combobox.bind('<<ComboboxSelected>>', self.on_site_changed)
        
        # Quick action buttons
        ttk.Button(toolbar, text="Nuovo Sito", command=self.new_site_dialog).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_data).pack(side=tk.RIGHT, padx=(0, 5))
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT)
        
        # Database info
        db_type = self.db_conn.connection_string.split('://')[0].upper()
        ttk.Label(status_frame, text=f"Database: {db_type}").pack(side=tk.RIGHT)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Create scrollable frame
        canvas = tk.Canvas(dashboard_frame)
        scrollbar = ttk.Scrollbar(dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Dashboard content
        self.create_dashboard_content(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store reference for updates
        self.dashboard_frame = scrollable_frame
    
    def create_dashboard_content(self, parent):
        """Create dashboard content widgets"""
        # Statistics section
        stats_frame = ttk.LabelFrame(parent, text="Statistiche Generali", padding=15)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create statistics grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Statistics cards
        self.stats_labels = {}
        stats_info = [
            ("total_sites", "Siti Archeologici", 0),
            ("total_us", "Unità Stratigrafiche", 1),
            ("total_inventory", "Reperti Catalogati", 2),
            ("total_media", "File Multimediali", 3)
        ]
        
        for stat_key, stat_label, col in stats_info:
            card_frame = ttk.Frame(stats_grid, relief="raised", borderwidth=1)
            card_frame.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
            stats_grid.columnconfigure(col, weight=1)
            
            ttk.Label(card_frame, text="0", font=("Arial", 20, "bold")).pack(pady=5)
            ttk.Label(card_frame, text=stat_label).pack()
            
            self.stats_labels[stat_key] = card_frame.winfo_children()[0]
        
        # Recent activity section
        activity_frame = ttk.LabelFrame(parent, text="Attività Recente", padding=15)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Activity tree
        self.activity_tree = ttk.Treeview(activity_frame, columns=("Type", "Name", "Date"), show="headings", height=10)
        self.activity_tree.heading("Type", text="Tipo")
        self.activity_tree.heading("Name", text="Nome")
        self.activity_tree.heading("Date", text="Data")
        
        self.activity_tree.column("Type", width=100)
        self.activity_tree.column("Name", width=300)
        self.activity_tree.column("Date", width=150)
        
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        activity_scrollbar.pack(side="right", fill="y")
        
        # Quick actions section
        actions_frame = ttk.LabelFrame(parent, text="Azioni Rapide", padding=15)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack()
        
        quick_actions = [
            ("Nuovo Sito", self.new_site_dialog, 0, 0),
            ("Nuova US", self.new_us_dialog, 0, 1),
            ("Nuovo Reperto", self.new_inventario_dialog, 0, 2),
            ("Harris Matrix", self.show_harris_matrix_dialog, 1, 0),
            ("Export PDF", self.export_pdf_dialog, 1, 1),
            ("Gestione Media", self.show_media_manager, 1, 2)
        ]
        
        for text, command, row, col in quick_actions:
            ttk.Button(actions_grid, text=text, command=command, width=15).grid(row=row, column=col, padx=5, pady=5)
    
    def create_sites_tab(self):
        """Create sites management tab"""
        sites_frame = ttk.Frame(self.notebook)
        self.notebook.add(sites_frame, text="Siti")
        
        # Toolbar
        sites_toolbar = ttk.Frame(sites_frame)
        sites_toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(sites_toolbar, text="Nuovo Sito", command=self.new_site_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(sites_toolbar, text="Modifica", command=self.edit_selected_site).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(sites_toolbar, text="Elimina", command=self.delete_selected_site).pack(side=tk.LEFT, padx=(0, 10))
        
        # Search
        search_frame = ttk.Frame(sites_toolbar)
        search_frame.pack(side=tk.RIGHT)
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
        self.sites_search_var = tk.StringVar()
        self.sites_search_var.trace("w", self.on_sites_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.sites_search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Sites list
        list_frame = ttk.Frame(sites_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview for sites
        self.sites_tree = ttk.Treeview(list_frame, columns=("Nome", "Comune", "Provincia", "Nazione"), show="headings")
        self.sites_tree.heading("Nome", text="Nome Sito")
        self.sites_tree.heading("Comune", text="Comune")
        self.sites_tree.heading("Provincia", text="Provincia")
        self.sites_tree.heading("Nazione", text="Nazione")
        
        self.sites_tree.column("Nome", width=250)
        self.sites_tree.column("Comune", width=150)
        self.sites_tree.column("Provincia", width=100)
        self.sites_tree.column("Nazione", width=100)
        
        sites_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.sites_tree.yview)
        self.sites_tree.configure(yscrollcommand=sites_scrollbar.set)
        
        self.sites_tree.pack(side="left", fill="both", expand=True)
        sites_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.sites_tree.bind("<Double-1>", lambda e: self.edit_selected_site())
    
    def create_us_tab(self):
        """Create US management tab"""
        us_frame = ttk.Frame(self.notebook)
        self.notebook.add(us_frame, text="US")
        
        # Toolbar
        us_toolbar = ttk.Frame(us_frame)
        us_toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(us_toolbar, text="Nuova US", command=self.new_us_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(us_toolbar, text="Modifica", command=self.edit_selected_us).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(us_toolbar, text="Elimina", command=self.delete_selected_us).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(us_toolbar, text="Esporta PDF", command=self.export_us_pdf).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(us_toolbar, text="Valida Paradossi", command=self.validate_stratigraphic_paradoxes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(us_toolbar, text="Fix Rapporti", command=self.fix_stratigraphic_relationships).pack(side=tk.LEFT, padx=(0, 10))
        
        # Search function
        search_frame = ttk.Frame(us_toolbar)
        search_frame.pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
        self.us_search_var = tk.StringVar()
        self.us_search_var.trace("w", self.on_us_search)
        us_search_entry = ttk.Entry(search_frame, textvariable=self.us_search_var, width=25)
        us_search_entry.pack(side=tk.LEFT)
        
        # Filter by site
        site_frame = ttk.Frame(us_toolbar)
        site_frame.pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(site_frame, text="Sito:").pack(side=tk.LEFT, padx=(0, 5))
        self.us_site_filter = ttk.Combobox(site_frame, width=20)
        self.us_site_filter.pack(side=tk.LEFT)
        self.us_site_filter.bind('<<ComboboxSelected>>', self.on_us_filter_changed)
        
        # US list
        list_frame = ttk.Frame(us_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview for US
        self.us_tree = ttk.Treeview(list_frame, columns=("Sito", "Area", "US", "Descrizione", "Anno"), show="headings")
        self.us_tree.heading("Sito", text="Sito")
        self.us_tree.heading("Area", text="Area")
        self.us_tree.heading("US", text="US")
        self.us_tree.heading("Descrizione", text="Descrizione")
        self.us_tree.heading("Anno", text="Anno")
        
        self.us_tree.column("Sito", width=150)
        self.us_tree.column("Area", width=100)
        self.us_tree.column("US", width=80)
        self.us_tree.column("Descrizione", width=300)
        self.us_tree.column("Anno", width=80)
        
        us_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.us_tree.yview)
        self.us_tree.configure(yscrollcommand=us_scrollbar.set)
        
        self.us_tree.pack(side="left", fill="both", expand=True)
        us_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.us_tree.bind("<Double-1>", lambda e: self.edit_selected_us())
    
    def create_inventario_tab(self):
        """Create inventory management tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="Inventario")
        
        # Toolbar
        inv_toolbar = ttk.Frame(inv_frame)
        inv_toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(inv_toolbar, text="Nuovo Reperto", command=self.new_inventario_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inv_toolbar, text="Modifica", command=self.edit_selected_inventario).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inv_toolbar, text="Elimina", command=self.delete_selected_inventario).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(inv_toolbar, text="Esporta PDF", command=self.export_inventario_pdf).pack(side=tk.LEFT, padx=(0, 10))
        
        # Search function
        search_frame = ttk.Frame(inv_toolbar)
        search_frame.pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
        self.inv_search_var = tk.StringVar()
        self.inv_search_var.trace("w", self.on_inventario_search)
        inv_search_entry = ttk.Entry(search_frame, textvariable=self.inv_search_var, width=25)
        inv_search_entry.pack(side=tk.LEFT)
        
        # Filters
        site_frame = ttk.Frame(inv_toolbar)
        site_frame.pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(site_frame, text="Sito:").pack(side=tk.LEFT, padx=(0, 5))
        self.inv_site_filter = ttk.Combobox(site_frame, width=15)
        self.inv_site_filter.pack(side=tk.LEFT)
        self.inv_site_filter.bind('<<ComboboxSelected>>', self.on_inventario_filter_changed)
        
        type_frame = ttk.Frame(inv_toolbar)
        type_frame.pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Label(type_frame, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))
        self.inv_type_filter = ttk.Combobox(type_frame, values=["", "Ceramica", "Metallo", "Pietra", "Osso", "Vetro"], width=15)
        self.inv_type_filter.pack(side=tk.LEFT)
        self.inv_type_filter.bind('<<ComboboxSelected>>', self.on_inventario_filter_changed)
        
        # Inventory list
        list_frame = ttk.Frame(inv_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview for inventory
        self.inv_tree = ttk.Treeview(list_frame, columns=("Sito", "Numero", "Tipo", "Definizione", "US", "Peso"), show="headings")
        self.inv_tree.heading("Sito", text="Sito")
        self.inv_tree.heading("Numero", text="N. Inv.")
        self.inv_tree.heading("Tipo", text="Tipo")
        self.inv_tree.heading("Definizione", text="Definizione")
        self.inv_tree.heading("US", text="US")
        self.inv_tree.heading("Peso", text="Peso (g)")
        
        self.inv_tree.column("Sito", width=120)
        self.inv_tree.column("Numero", width=80)
        self.inv_tree.column("Tipo", width=100)
        self.inv_tree.column("Definizione", width=200)
        self.inv_tree.column("US", width=60)
        self.inv_tree.column("Peso", width=80)
        
        inv_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inv_tree.yview)
        self.inv_tree.configure(yscrollcommand=inv_scrollbar.set)
        
        self.inv_tree.pack(side="left", fill="both", expand=True)
        inv_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.inv_tree.bind("<Double-1>", lambda e: self.edit_selected_inventario())
    
    def refresh_data(self):
        """Refresh all data in the interface"""
        self.status_text.set("Aggiornamento dati...")
        self.root.update_idletasks()
        
        try:
            # Update site combobox - now using DTOs (no session issues)
            sites = self.site_service.get_all_sites(size=200)
            site_names = [site.sito for site in sites]
            self.site_combobox['values'] = site_names
            
            # Update filter comboboxes
            self.us_site_filter['values'] = [""] + site_names
            self.inv_site_filter['values'] = [""] + site_names
            
            # Refresh tabs
            self.refresh_dashboard()
            self.refresh_sites()
            self.refresh_us()
            self.refresh_inventario()
            
            self.status_text.set("Dati aggiornati")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in refresh_data: {error_details}")
            self.status_text.set(f"Errore aggiornamento: {str(e)}")
            messagebox.showerror("Errore", f"Errore durante l'aggiornamento: {str(e)}\n\nDettagli: {error_details}")
    
    def refresh_dashboard(self):
        """Refresh dashboard statistics"""
        try:
            # Get statistics
            total_sites = self.site_service.count_sites()
            total_us = self.us_service.count_us()
            total_inventory = self.inventario_service.count_inventario()
            
            # Update stats labels
            self.stats_labels["total_sites"].config(text=str(total_sites))
            self.stats_labels["total_us"].config(text=str(total_us))
            self.stats_labels["total_inventory"].config(text=str(total_inventory))
            self.stats_labels["total_media"].config(text="0")  # TODO: implement media count
            
            # Update recent activity
            self.refresh_activity_log()
            
        except Exception as e:
            # Log error but don't print to console
            pass
    
    def refresh_activity_log(self):
        """Refresh activity log in dashboard"""
        # Clear existing items
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        try:
            # Get recent sites - now using DTOs (no session issues)
            recent_sites = self.site_service.get_all_sites(size=5)
            for site in recent_sites:
                self.activity_tree.insert("", "end", values=("Sito", site.sito, "Recente"))
            
            # Get recent US - now using DTOs (no session issues)
            recent_us = self.us_service.get_all_us(size=5)
            for us in recent_us:
                us_info = f"{us.sito} - US {us.us}"
                self.activity_tree.insert("", "end", values=("US", us_info, "Recente"))
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in refresh_activity_log: {error_details}")
            # Re-raise the exception so it's caught by refresh_data
            raise
    
    def refresh_sites(self):
        """Refresh sites list"""
        # Clear existing items
        for item in self.sites_tree.get_children():
            self.sites_tree.delete(item)
        
        try:
            search_term = self.sites_search_var.get().strip()
            if search_term:
                sites = self.site_service.search_sites(search_term, size=100)
            else:
                sites = self.site_service.get_all_sites(size=100)
            
            for site in sites:
                # Using DTO data (no session issues)
                site_data = (
                    site.sito,
                    site.comune or "-",
                    site.provincia or "-",
                    site.nazione or "-"
                )
                site_id = str(site.id_sito)
                self.sites_tree.insert("", "end", values=site_data, tags=(site_id,))
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in refresh_sites: {error_details}")
            # Re-raise the exception so it's caught by refresh_data
            raise
    
    def refresh_us(self):
        """Refresh US list"""
        # Clear existing items
        for item in self.us_tree.get_children():
            self.us_tree.delete(item)
        
        try:
            # Check if there's a search term
            search_term = getattr(self, 'us_search_var', None)
            search_text = search_term.get().strip() if search_term else ""
            
            if search_text:
                us_list = self.us_service.search_us(search_text, size=100)
            else:
                filters = {}
                site_filter = self.us_site_filter.get()
                if site_filter:
                    filters['sito'] = site_filter
                
                us_list = self.us_service.get_all_us(size=100, filters=filters)
            
            for us in us_list:
                # Using DTO data (no session issues)
                d_strat = us.d_stratigrafica or ""
                description = d_strat[:50] + "..." if len(d_strat) > 50 else (d_strat or "-")
                us_data = (
                    us.sito or "-",
                    us.area or "-",
                    str(us.us),
                    description,
                    str(us.anno_scavo) if us.anno_scavo else "-"
                )
                us_id = str(us.id_us)
                self.us_tree.insert("", "end", values=us_data, tags=(us_id,))
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in refresh_us: {error_details}")
            # Re-raise the exception so it's caught by refresh_data
            raise
    
    def refresh_inventario(self):
        """Refresh inventory list"""
        # Clear existing items
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        try:
            # Check if there's a search term
            search_term = getattr(self, 'inv_search_var', None)
            search_text = search_term.get().strip() if search_term else ""
            
            if search_text:
                inventory_list = self.inventario_service.search_inventario(search_text, size=100)
            else:
                filters = {}
                site_filter = self.inv_site_filter.get()
                type_filter = self.inv_type_filter.get()
                
                if site_filter:
                    filters['sito'] = site_filter
                if type_filter:
                    filters['tipo_reperto'] = type_filter
                
                inventory_list = self.inventario_service.get_all_inventario(size=100, filters=filters)
            
            for item in inventory_list:
                # Using DTO data (no session issues)
                inv_data = (
                    item.sito or "-",
                    str(item.numero_inventario),
                    item.tipo_reperto or "-",
                    item.definizione or "-",
                    str(item.us) if item.us else "-",
                    str(item.peso) if item.peso else "-"
                )
                item_id = str(item.id_invmat)
                self.inv_tree.insert("", "end", values=inv_data, tags=(item_id,))
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in refresh_inventario: {error_details}")
            # Re-raise the exception so it's caught by refresh_data
            raise
    
    # Event handlers
    def on_site_changed(self, event=None):
        """Handle site selection change"""
        selected_site = self.current_site.get()
        if selected_site:
            self.status_text.set(f"Sito selezionato: {selected_site}")
    
    def on_sites_search(self, *args):
        """Handle sites search"""
        self.refresh_sites()
    
    def on_us_filter_changed(self, event=None):
        """Handle US filter change"""
        self.refresh_us()
    
    def on_inventario_filter_changed(self, event=None):
        """Handle inventory filter change"""
        self.refresh_inventario()
    
    def on_us_search(self, *args):
        """Handle US search"""
        self.refresh_us()
    
    def on_inventario_search(self, *args):
        """Handle inventory search"""
        self.refresh_inventario()
    
    def show_tab(self, tab_name):
        """Show specific tab"""
        tab_map = {
            "dashboard": 0,
            "sites": 1,
            "us": 2,
            "inventario": 3
        }
        if tab_name in tab_map:
            self.notebook.select(tab_map[tab_name])
    
    # Dialog methods
    def new_site_dialog(self):
        """Show new site dialog"""
        SiteDialog(self.root, self.site_service, self.media_service, callback=self.refresh_data)
    
    def new_us_dialog(self):
        """Show new US dialog"""
        sites = self.site_service.get_all_sites(size=100)
        site_names = [site.sito for site in sites]
        ExtendedUSDialog(self.root, self.us_service, self.site_service, self.matrix_generator,
                        self.periodizzazione_service, site_names, self.db_manager, callback=self.refresh_data)
    
    def new_inventario_dialog(self):
        """Show new inventory dialog"""
        ExtendedInventarioDialog(self.root, self.inventario_service, self.site_service, 
                               self.thesaurus_service, self.media_service, 
                               callback=self.refresh_data)
    
    def edit_selected_site(self):
        """Edit selected site"""
        selection = self.sites_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona un sito da modificare")
            return
        
        site_id = int(self.sites_tree.item(selection[0])['tags'][0])
        site = self.site_service.get_site_dto_by_id(site_id)
        
        if site:
            SiteDialog(self.root, self.site_service, self.media_service, site=site, callback=self.refresh_data)
    
    def delete_selected_site(self):
        """Delete selected site"""
        selection = self.sites_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona un sito da eliminare")
            return
        
        if messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare il sito selezionato?"):
            try:
                site_id = int(self.sites_tree.item(selection[0])['tags'][0])
                self.site_service.delete_site(site_id)
                self.refresh_data()
                messagebox.showinfo("Successo", "Sito eliminato con successo")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione: {str(e)}")
    
    def edit_selected_us(self):
        """Edit selected US"""
        selection = self.us_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona una US da modificare")
            return
        
        us_id = int(self.us_tree.item(selection[0])['tags'][0])
        us = self.us_service.get_us_dto_by_id(us_id)
        
        if us:
            sites = self.site_service.get_all_sites(size=100)
            site_names = [site.sito for site in sites]
            ExtendedUSDialog(self.root, self.us_service, self.site_service, self.matrix_generator,
                           self.periodizzazione_service, site_names, self.db_manager, us=us, callback=self.refresh_data)
    
    def delete_selected_us(self):
        """Delete selected US"""
        selection = self.us_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona una US da eliminare")
            return
        
        if messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare la US selezionata?"):
            try:
                us_id = int(self.us_tree.item(selection[0])['tags'][0])
                self.us_service.delete_us(us_id)
                self.refresh_data()
                messagebox.showinfo("Successo", "US eliminata con successo")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione: {str(e)}")
    
    def edit_selected_inventario(self):
        """Edit selected inventory item"""
        selection = self.inv_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona un reperto da modificare")
            return
        
        inv_id = int(self.inv_tree.item(selection[0])['tags'][0])
        item = self.inventario_service.get_inventario_dto_by_id(inv_id)
        
        if item:
            ExtendedInventarioDialog(self.root, self.inventario_service, self.site_service, 
                                   self.thesaurus_service, self.media_service, 
                                   inventario=item, callback=self.refresh_data)
    
    def delete_selected_inventario(self):
        """Delete selected inventory item"""
        selection = self.inv_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona un reperto da eliminare")
            return
        
        if messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare il reperto selezionato?"):
            try:
                inv_id = int(self.inv_tree.item(selection[0])['tags'][0])
                self.inventario_service.delete_inventario(inv_id)
                self.refresh_data()
                messagebox.showinfo("Successo", "Reperto eliminato con successo")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione: {str(e)}")
    
    def show_harris_matrix_dialog(self):
        """Show Harris Matrix dialog"""
        sites = self.site_service.get_all_sites(size=100)
        if not sites:
            messagebox.showwarning("Avviso", "Nessun sito disponibile per generare la Harris Matrix")
            return

        HarrisMatrixDialog(self.root, self.matrix_generator, self.matrix_visualizer, sites,
                          self.site_service, self.us_service, self.db_manager)

    def show_graphml_export_dialog(self):
        """Show GraphML export dialog"""
        show_graphml_export_dialog(self.root, self.matrix_generator, self.matrix_visualizer, self.site_service)

    def export_pdf_dialog(self):
        """Show PDF export dialog"""
        sites = self.site_service.get_all_sites(size=100)
        if not sites:
            messagebox.showwarning("Avviso", "Nessun sito disponibile per l'export")
            return
        
        PDFExportDialog(self.root, self.pdf_generator, self.site_service, self.us_service, self.inventario_service, sites)
    
    def export_us_pdf(self):
        """Export currently visible US records as PDF"""
        try:
            # Get all visible US records from the treeview
            us_ids = []
            for item in self.us_tree.get_children():
                us_id = int(self.us_tree.item(item)['tags'][0])
                us_ids.append(us_id)
            
            if not us_ids:
                messagebox.showwarning("Avviso", "Nessuna US da esportare")
                return
            
            # Get US records
            us_list = []
            for us_id in us_ids:
                us = self.us_service.get_us_dto_by_id(us_id)
                if us:
                    # Convert to dict for PDF generator
                    us_dict = us.__dict__.copy()
                    # Remove any SQLAlchemy internal attributes
                    us_dict = {k: v for k, v in us_dict.items() if not k.startswith('_')}
                    us_list.append(us_dict)
            
            if not us_list:
                messagebox.showwarning("Avviso", "Nessuna US trovata")
                return
            
            # Group by site
            us_by_site = {}
            for us in us_list:
                site = us.get('sito', 'Unknown')
                if site not in us_by_site:
                    us_by_site[site] = []
                us_by_site[site].append(us)
            
            # Ask user for logo
            from tkinter import filedialog
            logo_path = filedialog.askopenfilename(
                title="Seleziona il logo (opzionale)",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            
            # Ask user for output directory
            output_dir = filedialog.askdirectory(title="Seleziona cartella di destinazione")
            if not output_dir:
                return
            
            # Generate PDFs
            generated_files = []
            for site, site_us_list in us_by_site.items():
                try:
                    # Create filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"US_{site.replace(' ', '_')}_{timestamp}.pdf"
                    full_path = os.path.join(output_dir, filename)
                    
                    pdf_path = self.pdf_generator.generate_us_pdf(
                        site_name=site,
                        us_list=site_us_list,
                        output_path=full_path,
                        logo_path=logo_path if logo_path else None
                    )
                    generated_files.append(pdf_path)
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore generazione PDF per sito {site}: {str(e)}")
            
            if generated_files:
                message = f"PDF esportati con successo:\n" + "\n".join(generated_files)
                messagebox.showinfo("Successo", message)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione PDF: {str(e)}")
    
    def export_inventario_pdf(self):
        """Export currently visible inventory records as PDF"""
        try:
            # Get all visible inventory records from the treeview
            inv_ids = []
            for item in self.inv_tree.get_children():
                inv_id = int(self.inv_tree.item(item)['tags'][0])
                inv_ids.append(inv_id)
            
            if not inv_ids:
                messagebox.showwarning("Avviso", "Nessun reperto da esportare")
                return
            
            # Get inventory records
            inv_list = []
            for inv_id in inv_ids:
                inv = self.inventario_service.get_inventario_dto_by_id(inv_id)
                if inv:
                    # Convert to dict for PDF generator
                    inv_dict = inv.__dict__.copy()
                    # Remove any SQLAlchemy internal attributes
                    inv_dict = {k: v for k, v in inv_dict.items() if not k.startswith('_')}
                    inv_list.append(inv_dict)
            
            if not inv_list:
                messagebox.showwarning("Avviso", "Nessun reperto trovato")
                return
            
            # Group by site
            inv_by_site = {}
            for inv in inv_list:
                site = inv.get('sito', 'Unknown')
                if site not in inv_by_site:
                    inv_by_site[site] = []
                inv_by_site[site].append(inv)
            
            # Ask user for logo
            from tkinter import filedialog
            logo_path = filedialog.askopenfilename(
                title="Seleziona il logo (opzionale)",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            
            # Ask user for output directory
            output_dir = filedialog.askdirectory(title="Seleziona cartella di destinazione")
            if not output_dir:
                return
            
            # Generate PDFs
            generated_files = []
            for site, site_inv_list in inv_by_site.items():
                try:
                    # Create filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"Inventario_{site.replace(' ', '_')}_{timestamp}.pdf"
                    full_path = os.path.join(output_dir, filename)
                    
                    pdf_path = self.pdf_generator.generate_inventory_pdf(
                        site_name=site,
                        inventory_list=site_inv_list,
                        output_path=full_path,
                        logo_path=logo_path if logo_path else None
                    )
                    generated_files.append(pdf_path)
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore generazione PDF per sito {site}: {str(e)}")
            
            if generated_files:
                message = f"PDF esportati con successo:\n" + "\n".join(generated_files)
                messagebox.showinfo("Successo", message)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione PDF: {str(e)}")
    
    def validate_stratigraphic_paradoxes(self):
        """Validate stratigraphic paradoxes for current site"""
        try:
            # Get current site
            site_name = self.current_site.get()
            if not site_name:
                messagebox.showwarning("Selezione", "Seleziona un sito")
                return
            
            # Get validation report
            report = self.us_service.validate_stratigraphic_paradoxes(site_name)
            
            # Show results
            if report['valid']:
                messagebox.showinfo(
                    "Validazione Stratigrafica",
                    f"Nessun paradosso trovato!\n\n"
                    f"Sito: {report['site']}\n"
                    f"Unità controllate: {report['units_checked']}\n"
                    f"Relazioni trovate: {report['relationships_found']}"
                )
            else:
                # Create detailed error window
                error_window = tk.Toplevel(self.root)
                error_window.title("Paradossi Stratigrafici Rilevati")
                error_window.geometry("600x400")
                
                # Header
                header_frame = ttk.Frame(error_window)
                header_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ttk.Label(
                    header_frame, 
                    text=f"Trovati {report['error_count']} paradossi stratigrafici",
                    style="Title.TLabel"
                ).pack()
                
                ttk.Label(
                    header_frame,
                    text=f"Sito: {report['site']} | Unità: {report['units_checked']} | Relazioni: {report['relationships_found']}"
                ).pack()
                
                # Error list
                error_frame = ttk.Frame(error_window)
                error_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
                
                # Scrolled text for errors
                error_text = scrolledtext.ScrolledText(
                    error_frame, 
                    wrap=tk.WORD, 
                    width=70, 
                    height=20
                )
                error_text.pack(fill=tk.BOTH, expand=True)
                
                # Add errors
                error_text.insert("1.0", "PARADOSSI RILEVATI:\n\n")
                for i, error in enumerate(report['errors'], 1):
                    error_text.insert(tk.END, f"{i}. {error}\n\n")
                
                error_text.config(state='disabled')
                
                # Close button
                ttk.Button(
                    error_window, 
                    text="Chiudi", 
                    command=error_window.destroy
                ).pack(pady=10)
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la validazione: {str(e)}")
    
    def fix_stratigraphic_relationships(self):
        """Fix missing reciprocal stratigraphic relationships"""
        try:
            # Get current site
            site_name = self.current_site.get()
            if not site_name:
                messagebox.showwarning("Selezione", "Seleziona un sito")
                return
            
            # Generate fixes
            fixes = self.us_service.generate_relationship_fixes(site_name)
            
            total_fixes = len(fixes.get('updates', [])) + len(fixes.get('creates', []))
            
            if total_fixes == 0:
                messagebox.showinfo(
                    "Fix Relazioni",
                    f"Nessuna correzione necessaria!\n\n"
                    f"Tutte le relazioni reciproche sono già presenti."
                )
                return
            
            # Create fix preview window
            fix_window = tk.Toplevel(self.root)
            fix_window.title("Fix Relazioni Stratigrafiche")
            fix_window.geometry("800x600")
            
            # Header
            header_frame = ttk.Frame(fix_window)
            header_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(
                header_frame,
                text=f"Trovate {total_fixes} correzioni da applicare",
                style="Title.TLabel"
            ).pack()
            
            ttk.Label(
                header_frame,
                text=f"Aggiornamenti: {len(fixes.get('updates', []))} | "
                     f"Nuove US da creare: {len(fixes.get('creates', []))}"
            ).pack()
            
            # Fix details
            detail_frame = ttk.Frame(fix_window)
            detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            # Create notebook for different fix types
            notebook = ttk.Notebook(detail_frame)
            notebook.pack(fill=tk.BOTH, expand=True)
            
            # Updates tab
            if fixes.get('updates'):
                updates_frame = ttk.Frame(notebook)
                notebook.add(updates_frame, text="Relazioni Reciproche Mancanti")
                
                updates_text = scrolledtext.ScrolledText(
                    updates_frame, 
                    wrap=tk.WORD, 
                    width=80, 
                    height=20
                )
                updates_text.pack(fill=tk.BOTH, expand=True)
                
                for i, update in enumerate(fixes['updates'], 1):
                    updates_text.insert(tk.END, 
                        f"{i}. US {update['us']} (Sito: {update['sito']}, Area: {update['area']})\n"
                        f"   Motivo: {update['reason']}\n"
                        f"   Vecchio valore: {update['old_value'] or '(vuoto)'}\n"
                        f"   Nuovo valore: {update['new_value']}\n\n"
                    )
                
                updates_text.config(state='disabled')
            
            # Creates tab
            if fixes.get('creates'):
                creates_frame = ttk.Frame(notebook)
                notebook.add(creates_frame, text="US Mancanti da Creare")
                
                creates_text = scrolledtext.ScrolledText(
                    creates_frame, 
                    wrap=tk.WORD, 
                    width=80, 
                    height=20
                )
                creates_text.pack(fill=tk.BOTH, expand=True)
                
                for i, create in enumerate(fixes['creates'], 1):
                    creates_text.insert(tk.END,
                        f"{i}. Nuova US {create['us']} (Sito: {create['sito']}, Area: {create['area']})\n"
                        f"   Motivo: {create['reason']}\n"
                        f"   Descrizione: {create['d_stratigrafica']}\n"
                        f"   Rapporti: {create['rapporti']}\n\n"
                    )
                
                creates_text.config(state='disabled')
            
            # Checkbox for creating missing US
            create_missing_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                fix_window,
                text="Crea US mancanti",
                variable=create_missing_var
            ).pack(pady=5)
            
            # Buttons
            button_frame = ttk.Frame(fix_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            def apply_fixes():
                try:
                    # Apply fixes
                    results = self.us_service.apply_relationship_fixes(
                        fixes, 
                        apply_creates=create_missing_var.get()
                    )
                    
                    # Show results
                    message = f"Fix applicati con successo!\n\n"
                    message += f"US aggiornate: {results['updated']}\n"
                    if create_missing_var.get():
                        message += f"US create: {results['created']}\n"
                    
                    if results['errors']:
                        message += f"\nErrori:\n"
                        for error in results['errors'][:5]:  # Show first 5 errors
                            message += f"- {error}\n"
                        if len(results['errors']) > 5:
                            message += f"... e altri {len(results['errors']) - 5} errori"
                    
                    messagebox.showinfo("Fix Completato", message)
                    
                    # Refresh US list
                    self.refresh_us()
                    
                    # Close window
                    fix_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore durante l'applicazione dei fix: {str(e)}")
            
            ttk.Button(
                button_frame,
                text="Applica Fix",
                command=apply_fixes,
                style="Accent.TButton"
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Annulla",
                command=fix_window.destroy
            ).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la generazione dei fix: {str(e)}")
    
    def show_media_manager(self):
        """Show media manager dialog"""
        try:
            MediaManagerDialog(self.root, self.media_handler)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura media manager: {str(e)}")
    
    def show_statistics_dialog(self):
        """Show statistics dialog"""
        StatisticsDialog(self.root, self.site_service, self.us_service, self.inventario_service)
    
    def show_database_config(self):
        """Show database configuration dialog"""
        DatabaseConfigDialog(self.root, callback=self.reconnect_database)
    
    def reconnect_database(self, connection_string):
        """Reconnect to database with new connection string"""
        try:
            # Close current connection
            self.db_conn.close()
            
            # Create new connection
            self.db_conn = DatabaseConnection.from_url(connection_string)
            self.db_conn.create_tables()
            self.db_manager = DatabaseManager(self.db_conn)
            
            # Reinitialize services
            self.site_service = SiteService(self.db_manager)
            self.us_service = USService(self.db_manager)
            self.inventario_service = InventarioService(self.db_manager)
            self.periodizzazione_service = PeriodizzazioneService(self.db_manager)
            self.media_service = MediaService(self.db_manager)
            self.matrix_generator = HarrisMatrixGenerator(self.db_manager, self.us_service)
            
            # Refresh data
            self.refresh_data()
            
            messagebox.showinfo("Successo", "Connessione al database aggiornata con successo")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella connessione al database: {str(e)}")
    
    def create_new_database(self):
        """Create a new empty SQLite database"""
        try:
            # Ask user where to save the new database
            new_db_path = filedialog.asksaveasfilename(
                title="Crea Nuovo Database SQLite",
                defaultextension=".db",
                filetypes=[("SQLite files", "*.db"), ("All files", "*.*")],
                initialvalue="nuovo_database.db"
            )

            if not new_db_path:
                return

            # Check if file already exists
            if os.path.exists(new_db_path):
                if not messagebox.askyesno("File Esistente",
                                          f"Il file {new_db_path} esiste già.\n"
                                          f"Vuoi sovrascriverlo?"):
                    return
                os.remove(new_db_path)

            # Create new database connection
            from pyarchinit_mini.database.connection import DatabaseConnection
            new_conn = DatabaseConnection.sqlite(new_db_path)

            # Create all tables
            new_conn.create_tables()

            # Initialize database manager and run migrations
            new_manager = DatabaseManager(new_conn)
            new_manager.run_migrations()

            # Close the new connection
            new_conn.close()

            # Ask if user wants to switch to the new database
            if messagebox.askyesno("Database Creato",
                                  f"Nuovo database creato con successo:\n{new_db_path}\n\n"
                                  f"Vuoi passare al nuovo database ora?"):
                # Reconnect to the new database
                self.db_conn.close()
                self.db_conn = DatabaseConnection.sqlite(new_db_path)
                self.setup_database()
                self.refresh_data()

                messagebox.showinfo("Successo", f"Ora stai usando il nuovo database:\n{new_db_path}")
            else:
                messagebox.showinfo("Completato", f"Database creato in:\n{new_db_path}")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Errore", f"Errore durante la creazione del database:\n{str(e)}\n\nDettagli:\n{error_details}")

    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """
PyArchInit-Mini v0.1.0

Sistema di gestione dati archeologici standalone

Sviluppato per la gestione di:
• Siti archeologici
• Unità stratigrafiche (US)
• Inventario materiali
• Harris Matrix
• Media e documentazione

Tecnologie:
• Python 3.x
• Tkinter GUI
• SQLAlchemy ORM
• SQLite/PostgreSQL

© 2024 PyArchInit Team
        """
        messagebox.showinfo("Informazioni", about_text)
    
    def show_help_dialog(self):
        """Show help dialog"""
        help_text = """
GUIDA RAPIDA PYARCHINIT-MINI

NAVIGAZIONE:
• Usa le tab per navigare tra le sezioni
• Dashboard: panoramica generale e statistiche
• Siti: gestione siti archeologici
• US: gestione unità stratigrafiche
• Inventario: gestione reperti

GESTIONE DATI:
• Clic destro per azioni rapide
• Doppio clic per modificare
• Usa i filtri per cercare dati specifici
• Toolbar per azioni principali

STRUMENTI:
• Harris Matrix: genera matrici stratigrafiche
• Export PDF: crea rapporti in PDF
• Gestione Media: organizza file multimediali
• Statistiche: analizza i dati

SCORCIATOIE:
• Ctrl+N: Nuovo elemento
• F5: Aggiorna dati
• Ctrl+Q: Esci
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Guida Utente")
        help_window.geometry("500x400")
        help_window.resizable(False, False)
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="Chiudi", command=help_window.destroy).pack(pady=10)
    
    def import_database(self):
        """Import database from file"""
        filename = filedialog.askopenfilename(
            title="Seleziona file database da importare",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Verify the file is a valid SQLite database
                import sqlite3
                test_conn = sqlite3.connect(filename)
                cursor = test_conn.cursor()
                
                # Check if it's a PyArchInit database by looking for key tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                test_conn.close()
                
                required_tables = ['site_table', 'us_table', 'inventario_materiali_table']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    if messagebox.askyesno("Database Non Compatibile", 
                                          f"Il database selezionato non sembra essere un database PyArchInit.\n"
                                          f"Tabelle mancanti: {', '.join(missing_tables)}\n\n"
                                          f"Vuoi comunque procedere con l'import?"):
                        # Proceed with import anyway
                        pass
                    else:
                        return
                
                # Ask user how to import
                import_choice = messagebox.askyesnocancel(
                    "Modalità Import",
                    "Come vuoi importare il database?\n\n"
                    "SÌ = Sostituisci database corrente\n"
                    "NO = Copia come nuovo database\n"
                    "Annulla = Annulla operazione"
                )
                
                if import_choice is None:  # Cancel
                    return
                elif import_choice:  # Yes - Replace current
                    self.replace_current_database(filename)
                else:  # No - Copy as new
                    self.copy_as_new_database(filename)
                    
            except sqlite3.Error as e:
                messagebox.showerror("Errore", f"File non valido o corrotto: {str(e)}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'import: {str(e)}")
    
    def replace_current_database(self, source_file):
        """Replace current database with imported one"""
        try:
            import shutil
            import os
            
            # Get current database path
            current_db = self.db_conn.connection_string.replace("sqlite:///", "")
            backup_db = current_db + ".backup"
            
            # Create backup of current database
            if os.path.exists(current_db):
                shutil.copy2(current_db, backup_db)
                messagebox.showinfo("Backup", f"Backup creato: {backup_db}")
            
            # Copy imported database
            shutil.copy2(source_file, current_db)
            
            # Reconnect to new database
            self.setup_database()
            self.refresh_data()
            
            messagebox.showinfo("Import Completato", 
                               f"Database importato e sostituito con successo!\n"
                               f"Backup precedente: {backup_db}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore sostituzione database: {str(e)}")
    
    def copy_as_new_database(self, source_file):
        """Copy imported database as new file"""
        try:
            import shutil
            import os
            
            # Ask where to save the copy
            new_filename = filedialog.asksaveasfilename(
                title="Salva database importato come",
                defaultextension=".db",
                filetypes=[("SQLite files", "*.db"), ("All files", "*.*")],
                initialvalue="imported_database.db"
            )
            
            if new_filename:
                # Copy the file
                shutil.copy2(source_file, new_filename)
                
                # Ask if user wants to switch to the new database
                if messagebox.askyesno("Cambia Database", 
                                      f"Database copiato in: {new_filename}\n\n"
                                      f"Vuoi passare al nuovo database ora?"):
                    # Update connection to new database
                    from pyarchinit_mini.database.connection import DatabaseConnection
                    self.db_conn = DatabaseConnection.sqlite(new_filename)
                    self.setup_database()
                    self.refresh_data()
                    
                    messagebox.showinfo("Successo", f"Ora stai usando: {new_filename}")
                else:
                    messagebox.showinfo("Completato", f"Database copiato in: {new_filename}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore copia database: {str(e)}")
    
    def load_sample_database(self):
        """Load the sample database"""
        import os
        sample_db_path = os.path.join("data", "pyarchinit_mini_sample.db")
        
        if os.path.exists(sample_db_path):
            try:
                # Create backup of current database if exists
                current_db = self.db_conn.connection_string.replace("sqlite:///", "")
                backup_db = current_db + ".backup"
                
                if os.path.exists(current_db):
                    import shutil
                    shutil.copy2(current_db, backup_db)
                
                # Switch to sample database
                from pyarchinit_mini.database.connection import DatabaseConnection
                self.db_conn = DatabaseConnection.sqlite(sample_db_path)
                self.setup_database()
                self.refresh_data()
                
                messagebox.showinfo("Database di Esempio Caricato", 
                                   "Database di esempio caricato con successo!\n\n"
                                   "Contenuto:\n"
                                   "• 1 Sito archeologico\n"
                                   "• 100 Unità Stratigrafiche\n"
                                   "• 50 Materiali\n"
                                   "• 70+ Relazioni stratigrafiche\n\n"
                                   f"Backup precedente: {backup_db}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore caricamento database di esempio: {str(e)}")
        else:
            if messagebox.askyesno("Database Mancante", 
                                  "Il database di esempio non esiste.\n"
                                  "Vuoi crearlo ora?"):
                self.create_sample_database()
    
    def create_sample_database(self):
        """Create sample database"""
        try:
            import subprocess
            import sys
            import os
            
            script_path = os.path.join("scripts", "populate_simple_data.py")
            if os.path.exists(script_path):
                # Show progress dialog
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Creazione Database")
                progress_window.geometry("400x200")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                ttk.Label(progress_window, text="Creazione database di esempio in corso...", 
                         font=("Arial", 12)).pack(pady=20)
                
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(pady=20, padx=40, fill=tk.X)
                progress_bar.start()
                
                status_label = ttk.Label(progress_window, text="Generazione dati...")
                status_label.pack(pady=10)
                
                progress_window.update()
                
                # Run the script
                result = subprocess.run([sys.executable, script_path], 
                                      capture_output=True, text=True)
                
                progress_bar.stop()
                progress_window.destroy()
                
                if result.returncode == 0:
                    # Switch to the newly created sample database
                    sample_db_path = os.path.join("data", "pyarchinit_mini_sample.db")
                    from pyarchinit_mini.database.connection import DatabaseConnection
                    self.db_conn = DatabaseConnection.sqlite(sample_db_path)
                    self.setup_database()
                    self.refresh_data()
                    
                    messagebox.showinfo("Successo", 
                                       "Database di esempio creato e caricato con successo!\n\n"
                                       "Contenuto:\n"
                                       "• 1 Sito archeologico\n"
                                       "• 100 US con relazioni\n"
                                       "• 50 Materiali")
                else:
                    messagebox.showerror("Errore", f"Errore creazione database: {result.stderr}")
            else:
                messagebox.showerror("Errore", "Script di creazione database non trovato")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la creazione: {str(e)}")
    
    def export_database(self):
        """Export database to file"""
        filename = filedialog.asksaveasfilename(
            title="Salva database",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            try:
                # TODO: Implement database export
                messagebox.showinfo("TODO", "Funzionalità in sviluppo")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'export: {str(e)}")
    
    def show_thesaurus_dialog(self):
        """Show thesaurus management dialog"""
        try:
            ThesaurusDialog(self.root, self.thesaurus_service, callback=self.refresh_data)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura thesaurus: {str(e)}")
    
    def show_postgres_installer(self):
        """Show PostgreSQL installer dialog"""
        try:
            def on_postgres_installed(connection_string):
                """Callback when PostgreSQL is installed and database created"""
                if messagebox.askyesno("Connessione Database", 
                                      "Database PostgreSQL creato con successo.\n"
                                      "Vuoi connetterti ora al nuovo database?"):
                    try:
                        # Reconnect to the new database
                        self.db_conn.close()
                        self.db_conn = DatabaseConnection.from_url(connection_string)
                        self.db_conn.create_tables()
                        self.db_manager = DatabaseManager(self.db_conn)
                        
                        # Reinitialize services
                        self.site_service = SiteService(self.db_manager)
                        self.us_service = USService(self.db_manager)
                        self.inventario_service = InventarioService(self.db_manager)
                        self.periodizzazione_service = PeriodizzazioneService(self.db_manager)
                        self.media_service = MediaService(self.db_manager)
                        self.thesaurus_service = ThesaurusService(self.db_manager)
                        self.matrix_generator = HarrisMatrixGenerator(self.db_manager, self.us_service)
                        
                        # Initialize default thesaurus
                        self.thesaurus_service.initialize_default_vocabularies()
                        
                        # Refresh interface
                        self.refresh_data()
                        self.status_text.set("Connesso a PostgreSQL")
                        
                        messagebox.showinfo("Successo", "Connessione al database PostgreSQL completata!")
                        
                    except Exception as e:
                        messagebox.showerror("Errore", f"Errore connessione database: {str(e)}")
            
            PostgreSQLInstallerDialog(self.root, self.postgres_installer, callback=on_postgres_installed)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura installer PostgreSQL: {str(e)}")
    
    
    def show_pdf_export_dialog(self):
        """Show PDF export dialog"""
        try:
            # Get sites list for the dialog
            sites = self.site_service.get_all_sites(size=200)
            PDFExportDialog(self.root, self.pdf_generator, self.site_service, self.us_service, 
                          self.inventario_service, sites)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura export PDF: {str(e)}")
    
    def show_statistics_dialog(self):
        """Show statistics dialog"""
        try:
            StatisticsDialog(self.root, self.site_service, self.us_service, self.inventario_service)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura statistiche: {str(e)}")

    def show_export_import_dialog(self):
        """Show export/import dialog"""
        try:
            show_export_import_dialog(self.root, self.db_manager)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura export/import: {str(e)}")

    def show_analytics_dashboard(self):
        """Show analytics dashboard dialog"""
        try:
            show_analytics_dialog(self.root, self.db_manager)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura analytics: {str(e)}")

    def refresh_current_tab(self):
        """Refresh the current tab (called by export/import dialog after import)"""
        self.refresh_data()

    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup when application closes"""
        try:
            if hasattr(self, 'db_conn'):
                self.db_conn.close()
        except:
            pass

if __name__ == "__main__":
    app = PyArchInitGUI()
    app.run()