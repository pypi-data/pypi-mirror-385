#!/usr/bin/env python3
"""
Extended Inventory Dialog for PyArchInit-Mini
Complete implementation with all fields from original PyArchInit plugin
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tempfile
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExtendedInventarioDialog:
    """
    Extended Inventory Dialog with all fields from PyArchInit plugin
    Includes media management and thesaurus integration
    """
    
    def __init__(self, parent, inventario_service, site_service, thesaurus_service=None, 
                 media_service=None, inventario=None, callback=None):
        self.parent = parent
        self.inventario_service = inventario_service
        self.site_service = site_service
        self.thesaurus_service = thesaurus_service
        self.media_service = media_service
        self.inventario = inventario
        self.callback = callback
        self.media_list = []
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuovo Reperto" if inventario is None else "Modifica Reperto")
        self.dialog.geometry("1000x700")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_window()
        
        # Create media directory
        self.media_dir = self.create_media_directory()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_identification_tab()
        self.create_classification_tab()
        self.create_context_tab()
        self.create_physical_tab()
        self.create_conservation_tab()
        self.create_ceramic_tab()
        self.create_measurements_tab()
        self.create_documentation_tab()
        self.create_media_tab()
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(self.button_frame, text="Annulla", command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(self.button_frame, text="Salva", command=self.save).pack(side=tk.RIGHT)
        ttk.Button(self.button_frame, text="Esporta PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
        # Load existing data
        if inventario:
            self.populate_form()
            self.load_media()
    
    def center_window(self):
        """Center dialog window on parent"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_media_directory(self):
        """Create media directory for the inventory item"""
        if self.inventario:
            inv_id = str(getattr(self.inventario, 'id_invmat', 'unknown'))
        else:
            inv_id = 'new_item'
        
        media_dir = os.path.join(tempfile.gettempdir(), 'pyarchinit_media', 'inventario', inv_id)
        os.makedirs(media_dir, exist_ok=True)
        return media_dir
    
    def get_thesaurus_values(self, field_name: str) -> List[str]:
        """Get thesaurus values for a field"""
        if not self.thesaurus_service:
            # Return default values if no thesaurus service
            defaults = {
                'tipo_reperto': ['Ceramica', 'Metallo', 'Vetro', 'Osso', 'Pietra', 'Legno', 'Tessuto', 'Laterizio', 'Moneta'],
                'stato_conservazione': ['Ottimo', 'Buono', 'Discreto', 'Cattivo', 'Pessimo', 'Frammentario', 'Lacunoso', 'Integro'],
                'corpo_ceramico': ['Depurato', 'Semi-depurato', 'Grezzo', 'Fine', 'Medio-fine', 'Grossolano'],
                'rivestimento': ['Verniciato', 'Ingobbato', 'Dipinto', 'Graffito', 'Inciso', 'Impresso', 'Nudo']
            }
            return [''] + defaults.get(field_name, [])
        
        try:
            values = self.thesaurus_service.get_field_values('inventario_materiali_table', field_name)
            return [''] + [v['value'] for v in values]
        except Exception as e:
            logger.error(f"Error getting thesaurus values for {field_name}: {e}")
            return ['']
    
    def create_identification_tab(self):
        """Create identification and basic info tab"""
        id_frame = ttk.Frame(self.notebook)
        self.notebook.add(id_frame, text="Identificazione")
        
        # Create scrollable frame
        canvas = tk.Canvas(id_frame)
        scrollbar = ttk.Scrollbar(id_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.fields = {}
        row = 0
        
        # Get site names
        try:
            sites = self.site_service.get_all_sites()
            site_names = [site['sito'] for site in sites]
        except Exception:
            site_names = []
        
        # Sito (required)
        ttk.Label(scrollable_frame, text="Sito *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['sito'] = ttk.Combobox(scrollable_frame, values=site_names, width=35)
        self.fields['sito'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Numero inventario (required)
        ttk.Label(scrollable_frame, text="Numero Inventario *:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['numero_inventario'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['numero_inventario'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # N. Reperto
        ttk.Label(scrollable_frame, text="N. Reperto:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['n_reperto'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['n_reperto'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Schedatore
        ttk.Label(scrollable_frame, text="Schedatore:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['schedatore'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['schedatore'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Data scheda
        ttk.Label(scrollable_frame, text="Data Scheda:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['date_scheda'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['date_scheda'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        # Set current date as default
        self.fields['date_scheda'].insert(0, datetime.now().strftime("%Y-%m-%d"))
        row += 1
        
        # Years
        ttk.Label(scrollable_frame, text="Anno:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['years'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['years'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Focus on first field
        self.fields['sito'].focus()
    
    def create_classification_tab(self):
        """Create classification tab"""
        class_frame = ttk.Frame(self.notebook)
        self.notebook.add(class_frame, text="Classificazione")
        
        # Create scrollable frame
        canvas = tk.Canvas(class_frame)
        scrollbar = ttk.Scrollbar(class_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Tipo reperto
        ttk.Label(scrollable_frame, text="Tipo Reperto:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        tipo_values = self.get_thesaurus_values('tipo_reperto')
        self.fields['tipo_reperto'] = ttk.Combobox(scrollable_frame, values=tipo_values, width=35)
        self.fields['tipo_reperto'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Criterio schedatura
        ttk.Label(scrollable_frame, text="Criterio Schedatura:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['criterio_schedatura'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['criterio_schedatura'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Definizione
        ttk.Label(scrollable_frame, text="Definizione:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['definizione'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['definizione'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Tipo
        ttk.Label(scrollable_frame, text="Tipo:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['tipo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['tipo'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Tipo contenitore
        ttk.Label(scrollable_frame, text="Tipo Contenitore:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['tipo_contenitore'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['tipo_contenitore'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Struttura
        ttk.Label(scrollable_frame, text="Struttura:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['struttura'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['struttura'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Descrizione
        ttk.Label(scrollable_frame, text="Descrizione:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['descrizione'] = tk.Text(scrollable_frame, width=40, height=5)
        self.fields['descrizione'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_context_tab(self):
        """Create context tab"""
        context_frame = ttk.Frame(self.notebook)
        self.notebook.add(context_frame, text="Contesto")
        
        # Create scrollable frame
        canvas = tk.Canvas(context_frame)
        scrollbar = ttk.Scrollbar(context_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Area
        ttk.Label(scrollable_frame, text="Area:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['area'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['area'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # US
        ttk.Label(scrollable_frame, text="US:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['us'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['us'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Punto rinvenimento
        ttk.Label(scrollable_frame, text="Punto Rinvenimento:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['punto_rinv'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['punto_rinv'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Elementi reperto
        ttk.Label(scrollable_frame, text="Elementi Reperto:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['elementi_reperto'] = tk.Text(scrollable_frame, width=40, height=4)
        self.fields['elementi_reperto'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_physical_tab(self):
        """Create physical characteristics tab"""
        phys_frame = ttk.Frame(self.notebook)
        self.notebook.add(phys_frame, text="Caratteristiche Fisiche")
        
        # Create scrollable frame
        canvas = tk.Canvas(phys_frame)
        scrollbar = ttk.Scrollbar(phys_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Peso
        ttk.Label(scrollable_frame, text="Peso (g):").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['peso'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['peso'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Forme minime
        ttk.Label(scrollable_frame, text="Forme Minime:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['forme_minime'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['forme_minime'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Forme massime
        ttk.Label(scrollable_frame, text="Forme Massime:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['forme_massime'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['forme_massime'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Totale frammenti
        ttk.Label(scrollable_frame, text="Totale Frammenti:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['totale_frammenti'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['totale_frammenti'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Misurazioni
        ttk.Label(scrollable_frame, text="Misurazioni:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['misurazioni'] = tk.Text(scrollable_frame, width=40, height=4)
        self.fields['misurazioni'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Tecnologie
        ttk.Label(scrollable_frame, text="Tecnologie:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['tecnologie'] = tk.Text(scrollable_frame, width=40, height=4)
        self.fields['tecnologie'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_conservation_tab(self):
        """Create conservation tab"""
        cons_frame = ttk.Frame(self.notebook)
        self.notebook.add(cons_frame, text="Conservazione")
        
        # Create scrollable frame
        canvas = tk.Canvas(cons_frame)
        scrollbar = ttk.Scrollbar(cons_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Stato conservazione
        ttk.Label(scrollable_frame, text="Stato Conservazione:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        stato_values = self.get_thesaurus_values('stato_conservazione')
        self.fields['stato_conservazione'] = ttk.Combobox(scrollable_frame, values=stato_values, width=35)
        self.fields['stato_conservazione'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Lavato
        ttk.Label(scrollable_frame, text="Lavato:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['lavato'] = ttk.Combobox(scrollable_frame, values=["", "Sì", "No"], width=35)
        self.fields['lavato'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Nr cassa
        ttk.Label(scrollable_frame, text="Nr. Cassa:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['nr_cassa'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['nr_cassa'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Luogo conservazione
        ttk.Label(scrollable_frame, text="Luogo Conservazione:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['luogo_conservazione'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['luogo_conservazione'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Repertato
        ttk.Label(scrollable_frame, text="Repertato:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['repertato'] = ttk.Combobox(scrollable_frame, values=["", "Sì", "No"], width=35)
        self.fields['repertato'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Diagnostico
        ttk.Label(scrollable_frame, text="Diagnostico:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['diagnostico'] = ttk.Combobox(scrollable_frame, values=["", "Sì", "No"], width=35)
        self.fields['diagnostico'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_ceramic_tab(self):
        """Create ceramic-specific fields tab"""
        ceramic_frame = ttk.Frame(self.notebook)
        self.notebook.add(ceramic_frame, text="Ceramica")
        
        # Create scrollable frame
        canvas = tk.Canvas(ceramic_frame)
        scrollbar = ttk.Scrollbar(ceramic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Corpo ceramico
        ttk.Label(scrollable_frame, text="Corpo Ceramico:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        corpo_values = self.get_thesaurus_values('corpo_ceramico')
        self.fields['corpo_ceramico'] = ttk.Combobox(scrollable_frame, values=corpo_values, width=35)
        self.fields['corpo_ceramico'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Rivestimento
        ttk.Label(scrollable_frame, text="Rivestimento:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        riv_values = self.get_thesaurus_values('rivestimento')
        self.fields['rivestimento'] = ttk.Combobox(scrollable_frame, values=riv_values, width=35)
        self.fields['rivestimento'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Diametro orlo
        ttk.Label(scrollable_frame, text="Diametro Orlo (cm):").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['diametro_orlo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['diametro_orlo'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # EVE orlo
        ttk.Label(scrollable_frame, text="EVE Orlo:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['eve_orlo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['eve_orlo'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_measurements_tab(self):
        """Create measurements and dating tab"""
        meas_frame = ttk.Frame(self.notebook)
        self.notebook.add(meas_frame, text="Misurazioni e Datazione")
        
        # Create scrollable frame
        canvas = tk.Canvas(meas_frame)
        scrollbar = ttk.Scrollbar(meas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Datazione reperto
        ttk.Label(scrollable_frame, text="Datazione Reperto:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['datazione_reperto'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['datazione_reperto'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_documentation_tab(self):
        """Create documentation tab"""
        doc_frame = ttk.Frame(self.notebook)
        self.notebook.add(doc_frame, text="Documentazione")
        
        # Create scrollable frame
        canvas = tk.Canvas(doc_frame)
        scrollbar = ttk.Scrollbar(doc_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # Riferimenti bibliografici
        ttk.Label(scrollable_frame, text="Riferimenti Bibliografici:").grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.fields['rif_biblio'] = tk.Text(scrollable_frame, width=40, height=4)
        self.fields['rif_biblio'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Negativo photo
        ttk.Label(scrollable_frame, text="Negativo Photo:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['negativo_photo'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['negativo_photo'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        # Diapositiva
        ttk.Label(scrollable_frame, text="Diapositiva:").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.fields['diapositiva'] = ttk.Entry(scrollable_frame, width=40)
        self.fields['diapositiva'].grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_media_tab(self):
        """Create media management tab"""
        media_frame = ttk.Frame(self.notebook)
        self.notebook.add(media_frame, text="Media")
        
        # Control buttons frame
        control_frame = ttk.Frame(media_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Aggiungi Media", command=self.add_media_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Rimuovi Selezionato", command=self.remove_media_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Anteprima", command=self.preview_media).pack(side=tk.LEFT, padx=5)
        
        # Drag and drop area
        drop_frame = ttk.LabelFrame(media_frame, text="Trascina qui i file multimediali")
        drop_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.drop_area = tk.Label(drop_frame, 
                                text="Trascina qui i file multimediali\\n(Immagini, PDF, Video, Audio)",
                                relief="sunken", bd=2, height=3)
        self.drop_area.pack(fill=tk.X, padx=5, pady=5)
        
        # Enable drag and drop
        self.drop_area.bind("<Button-1>", self.add_media_file)
        
        # Media list with thumbnails
        list_frame = ttk.LabelFrame(media_frame, text="File Media")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for media list
        columns = ('Nome', 'Tipo', 'Dimensione', 'Descrizione')
        self.media_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=8)
        
        # Configure columns
        self.media_tree.heading('#0', text='Thumbnail')
        self.media_tree.column('#0', width=100, minwidth=100)
        
        for col in columns:
            self.media_tree.heading(col, text=col)
            self.media_tree.column(col, width=120)
        
        # Scrollbars
        media_scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=self.media_tree.yview)
        media_scrollbar_x = ttk.Scrollbar(list_frame, orient="horizontal", command=self.media_tree.xview)
        self.media_tree.configure(yscrollcommand=media_scrollbar_y.set, xscrollcommand=media_scrollbar_x.set)
        
        self.media_tree.pack(side="left", fill="both", expand=True)
        media_scrollbar_y.pack(side="right", fill="y")
        media_scrollbar_x.pack(side="bottom", fill="x")
        
        # Description frame for selected media
        desc_frame = ttk.LabelFrame(media_frame, text="Descrizione Media")
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.media_description = tk.Text(desc_frame, height=3)
        self.media_description.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind selection event
        self.media_tree.bind('<<TreeviewSelect>>', self.on_media_select)
    
    def add_media_file(self, event=None):
        """Add media file with file dialog"""
        filetypes = [
            ('Tutti i file supportati', '*.jpg *.jpeg *.png *.gif *.bmp *.pdf *.mp4 *.avi *.mov *.mp3 *.wav'),
            ('Immagini', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('Documenti', '*.pdf *.doc *.docx'),
            ('Video', '*.mp4 *.avi *.mov *.wmv'),
            ('Audio', '*.mp3 *.wav *.ogg'),
            ('Tutti i file', '*.*')
        ]
        
        file_paths = filedialog.askopenfilenames(
            title="Seleziona file media",
            filetypes=filetypes
        )
        
        for file_path in file_paths:
            self.process_media_file(file_path)
    
    def process_media_file(self, file_path):
        """Process and add media file to the list"""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Errore", f"File non trovato: {file_path}")
                return
            
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Determine media type
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                media_type = 'image'
            elif file_ext in ['.pdf', '.doc', '.docx']:
                media_type = 'document'
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
                media_type = 'video'
            elif file_ext in ['.mp3', '.wav', '.ogg']:
                media_type = 'audio'
            else:
                media_type = 'other'
            
            # Copy file to media directory
            dest_path = os.path.join(self.media_dir, file_name)
            if file_path != dest_path:
                import shutil
                shutil.copy2(file_path, dest_path)
            
            # Add to media list
            media_info = {
                'file_path': dest_path,
                'file_name': file_name,
                'media_type': media_type,
                'file_size': file_size,
                'description': ''
            }
            
            self.media_list.append(media_info)
            self.refresh_media_list()
            
            messagebox.showinfo("Successo", f"File '{file_name}' aggiunto con successo")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'aggiunta del file: {str(e)}")
    
    def refresh_media_list(self):
        """Refresh the media list display"""
        # Clear existing items
        for item in self.media_tree.get_children():
            self.media_tree.delete(item)
        
        # Add media items
        for i, media in enumerate(self.media_list):
            # Format file size
            size_str = self.format_file_size(media['file_size'])
            
            # Insert item
            item_id = self.media_tree.insert('', 'end', 
                                            text=f"Media {i+1}",
                                            values=(media['file_name'], 
                                                   media['media_type'], 
                                                   size_str,
                                                   media['description'][:50] + '...' if len(media['description']) > 50 else media['description']))
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def on_media_select(self, event):
        """Handle media selection"""
        selection = self.media_tree.selection()
        if selection:
            item = selection[0]
            index = self.media_tree.index(item)
            if 0 <= index < len(self.media_list):
                media = self.media_list[index]
                self.media_description.delete('1.0', tk.END)
                self.media_description.insert('1.0', media['description'])
    
    def remove_media_file(self):
        """Remove selected media file"""
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un file media da rimuovere")
            return
        
        item = selection[0]
        index = self.media_tree.index(item)
        
        if 0 <= index < len(self.media_list):
            media = self.media_list[index]
            
            # Confirm deletion
            if messagebox.askyesno("Conferma", f"Rimuovere il file '{media['file_name']}'?"):
                # Remove file from filesystem
                try:
                    if os.path.exists(media['file_path']):
                        os.remove(media['file_path'])
                except Exception as e:
                    messagebox.showerror("Errore", f"Errore durante la rimozione del file: {str(e)}")
                
                # Remove from list
                self.media_list.pop(index)
                self.refresh_media_list()
                
                # Clear description
                self.media_description.delete('1.0', tk.END)
    
    def preview_media(self):
        """Preview selected media file"""
        selection = self.media_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un file media da visualizzare")
            return
        
        item = selection[0]
        index = self.media_tree.index(item)
        
        if 0 <= index < len(self.media_list):
            media = self.media_list[index]
            try:
                # Open file with default application
                if os.path.exists(media['file_path']):
                    import subprocess
                    if sys.platform.startswith('darwin'):  # macOS
                        subprocess.call(['open', media['file_path']])
                    elif sys.platform.startswith('win'):  # Windows
                        os.startfile(media['file_path'])
                    else:  # Linux
                        subprocess.call(['xdg-open', media['file_path']])
                else:
                    messagebox.showerror("Errore", "File non trovato")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'apertura del file: {str(e)}")
    
    def load_media(self):
        """Load existing media files for the inventory item"""
        if not self.inventario or not self.media_service:
            return
        
        try:
            # Load media from service
            media_files = self.media_service.get_media_by_entity('inventario', self.inventario.get('id_invmat'))
            
            for media in media_files:
                media_info = {
                    'file_path': media.get('file_path', ''),
                    'file_name': media.get('media_name', ''),
                    'media_type': media.get('media_type', 'other'),
                    'file_size': media.get('file_size', 0),
                    'description': media.get('description', '')
                }
                self.media_list.append(media_info)
            
            self.refresh_media_list()
            
        except Exception as e:
            logger.error(f"Error loading media: {e}")
    
    def get_text_field_value(self, field_name):
        """Get value from Text widget"""
        if field_name in self.fields and isinstance(self.fields[field_name], tk.Text):
            return self.fields[field_name].get("1.0", tk.END).strip() or None
        return None
    
    def get_entry_field_value(self, field_name):
        """Get value from Entry or Combobox widget"""
        if field_name in self.fields:
            value = self.fields[field_name].get().strip()
            return value if value else None
        return None
    
    def populate_form(self):
        """Populate form with existing inventory data"""
        if not self.inventario:
            return
        
        # Basic fields
        entry_fields = [
            'sito', 'numero_inventario', 'n_reperto', 'schedatore', 'date_scheda', 'years',
            'tipo_reperto', 'criterio_schedatura', 'definizione', 'tipo', 'tipo_contenitore',
            'struttura', 'area', 'us', 'punto_rinv', 'peso', 'forme_minime', 'forme_massime',
            'totale_frammenti', 'stato_conservazione', 'lavato', 'nr_cassa', 'luogo_conservazione',
            'repertato', 'diagnostico', 'corpo_ceramico', 'rivestimento', 'diametro_orlo',
            'eve_orlo', 'datazione_reperto', 'negativo_photo', 'diapositiva'
        ]
        
        for field in entry_fields:
            if field in self.fields and hasattr(self.inventario, field):
                value = getattr(self.inventario, field)
                if value is not None:
                    if hasattr(self.fields[field], 'set'):  # Combobox
                        self.fields[field].set(str(value))
                    else:  # Entry
                        self.fields[field].insert(0, str(value))
        
        # Text fields
        text_fields = ['descrizione', 'elementi_reperto', 'misurazioni', 'tecnologie', 'rif_biblio']
        
        for field in text_fields:
            if field in self.fields and hasattr(self.inventario, field):
                value = getattr(self.inventario, field)
                if value is not None:
                    self.fields[field].insert("1.0", str(value))
    
    def save(self):
        """Save inventory data"""
        try:
            # Validate required fields
            sito = self.get_entry_field_value('sito')
            numero_inventario = self.get_entry_field_value('numero_inventario')
            
            if not sito:
                messagebox.showerror("Errore", "Il sito è obbligatorio")
                return
            
            if not numero_inventario:
                messagebox.showerror("Errore", "Il numero inventario è obbligatorio")
                return
            
            # Prepare data
            inventario_data = {
                'sito': sito,
                'numero_inventario': int(numero_inventario) if numero_inventario.isdigit() else None,
                'n_reperto': int(self.get_entry_field_value('n_reperto')) if self.get_entry_field_value('n_reperto') and self.get_entry_field_value('n_reperto').isdigit() else None,
                'schedatore': self.get_entry_field_value('schedatore'),
                'date_scheda': self.get_entry_field_value('date_scheda'),
                'years': int(self.get_entry_field_value('years')) if self.get_entry_field_value('years') and self.get_entry_field_value('years').isdigit() else None,
                'tipo_reperto': self.get_entry_field_value('tipo_reperto'),
                'criterio_schedatura': self.get_entry_field_value('criterio_schedatura'),
                'definizione': self.get_entry_field_value('definizione'),
                'descrizione': self.get_text_field_value('descrizione'),
                'tipo': self.get_entry_field_value('tipo'),
                'tipo_contenitore': self.get_entry_field_value('tipo_contenitore'),
                'struttura': self.get_entry_field_value('struttura'),
                'area': self.get_entry_field_value('area'),
                'us': self.get_entry_field_value('us'),
                'punto_rinv': self.get_entry_field_value('punto_rinv'),
                'elementi_reperto': self.get_text_field_value('elementi_reperto'),
                'peso': float(self.get_entry_field_value('peso')) if self.get_entry_field_value('peso') else None,
                'forme_minime': int(self.get_entry_field_value('forme_minime')) if self.get_entry_field_value('forme_minime') and self.get_entry_field_value('forme_minime').isdigit() else None,
                'forme_massime': int(self.get_entry_field_value('forme_massime')) if self.get_entry_field_value('forme_massime') and self.get_entry_field_value('forme_massime').isdigit() else None,
                'totale_frammenti': int(self.get_entry_field_value('totale_frammenti')) if self.get_entry_field_value('totale_frammenti') and self.get_entry_field_value('totale_frammenti').isdigit() else None,
                'misurazioni': self.get_text_field_value('misurazioni'),
                'tecnologie': self.get_text_field_value('tecnologie'),
                'stato_conservazione': self.get_entry_field_value('stato_conservazione'),
                'lavato': self.get_entry_field_value('lavato'),
                'nr_cassa': self.get_entry_field_value('nr_cassa'),
                'luogo_conservazione': self.get_entry_field_value('luogo_conservazione'),
                'repertato': self.get_entry_field_value('repertato'),
                'diagnostico': self.get_entry_field_value('diagnostico'),
                'corpo_ceramico': self.get_entry_field_value('corpo_ceramico'),
                'rivestimento': self.get_entry_field_value('rivestimento'),
                'diametro_orlo': float(self.get_entry_field_value('diametro_orlo')) if self.get_entry_field_value('diametro_orlo') else None,
                'eve_orlo': float(self.get_entry_field_value('eve_orlo')) if self.get_entry_field_value('eve_orlo') else None,
                'datazione_reperto': self.get_entry_field_value('datazione_reperto'),
                'rif_biblio': self.get_text_field_value('rif_biblio'),
                'negativo_photo': self.get_entry_field_value('negativo_photo'),
                'diapositiva': self.get_entry_field_value('diapositiva')
            }
            
            # Save inventory
            if self.inventario:
                # Update existing inventory
                updated_inventario = self.inventario_service.update_inventario(self.inventario['id_invmat'], inventario_data)
                messagebox.showinfo("Successo", "Reperto aggiornato con successo")
            else:
                # Create new inventory
                new_inventario = self.inventario_service.create_inventario(inventario_data)
                messagebox.showinfo("Successo", "Reperto creato con successo")
            
            # Call callback to refresh data
            if self.callback:
                self.callback()
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()
    
    def export_pdf(self):
        """Export current inventory record as PDF"""
        try:
            # Check if we have an inventory record
            if not self.inventario:
                messagebox.showwarning("Avviso", "Nessun reperto da esportare")
                return
            
            # Ask user for output file
            from tkinter import filedialog
            output_path = filedialog.asksaveasfilename(
                title="Salva PDF come",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"inventario_{self.inventario.get('numero_inventario', 'nuovo')}.pdf"
            )
            
            if not output_path:
                return
            
            # Import PDF generator
            from ..pdf_export.pdf_generator import PDFGenerator
            
            # Create PDF generator instance
            generator = PDFGenerator()
            
            # Prepare inventory data as list
            inv_data = self.inventario.copy() if isinstance(self.inventario, dict) else self.inventario.__dict__.copy()
            
            # Generate PDF
            pdf_path = generator.generate_inventory_pdf(
                site_name=inv_data.get('sito', 'Unknown'),
                inventory_list=[inv_data],
                output_path=os.path.dirname(output_path)
            )
            
            # Rename to user's chosen name if different
            if pdf_path != output_path:
                import shutil
                shutil.move(pdf_path, output_path)
                pdf_path = output_path
            
            messagebox.showinfo("Successo", f"PDF esportato con successo:\n{pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione PDF: {str(e)}")