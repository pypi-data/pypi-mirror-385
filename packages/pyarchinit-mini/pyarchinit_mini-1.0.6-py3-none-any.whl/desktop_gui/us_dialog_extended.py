#!/usr/bin/env python3
"""
Extended US Dialog with tabs for relationships and periodization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.dnd import DndHandler
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from PIL import Image, ImageTk
import shutil

class ExtendedUSDialog:
    """
    Extended US dialog with multiple tabs for complete archaeological recording
    """
    
    def __init__(self, parent, us_service, site_service, matrix_generator, periodizzazione_service, 
                 site_names, db_manager, us=None, callback=None):
        self.parent = parent
        self.us_service = us_service
        self.site_service = site_service
        self.matrix_generator = matrix_generator
        self.periodizzazione_service = periodizzazione_service
        self.site_names = site_names
        self.db_manager = db_manager
        self.us = us
        self.callback = callback

        # Store US ID and number separately to avoid session issues
        self.us_id = us.id_us if us else None
        self.us_number = us.us if us else None

        # Data storage
        self.fields = {}
        self.relationships_data = []
        self.periodizzazione_data = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Nuova US" if us is None else f"Modifica US {self.us_number}")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create interface
        self.create_interface()
        
        # Populate if editing
        if us:
            self.populate_form()
    
    def create_interface(self):
        """Create the main interface with tabs"""
        
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_basic_tab()
        self.create_description_tab()
        self.create_physical_tab()
        self.create_chronology_tab()
        self.create_relationships_tab()
        self.create_media_tab()
        self.create_documentation_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Salva", command=self.save_us).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        
        if self.us:
            ttk.Button(button_frame, text="Elimina", command=self.delete_us).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Esporta PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
    
    def create_basic_tab(self):
        """Create basic information tab"""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Informazioni Base")
        
        # Create scrollable frame
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        row = 0
        
        # Identification section
        id_frame = ttk.LabelFrame(scrollable_frame, text="Identificazione", padding=10)
        id_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1
        
        # Sito (required)
        ttk.Label(id_frame, text="Sito *:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['sito'] = ttk.Combobox(id_frame, values=self.site_names, width=30)
        self.fields['sito'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Area
        ttk.Label(id_frame, text="Area:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['area'] = ttk.Entry(id_frame, width=20)
        self.fields['area'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # US number (required)
        ttk.Label(id_frame, text="Numero US *:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['us'] = ttk.Entry(id_frame, width=30)
        self.fields['us'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Unità tipo
        ttk.Label(id_frame, text="Tipo Unità:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['unita_tipo'] = ttk.Combobox(id_frame, 
                                               values=["US", "USM", "USV", "USR"], width=20)
        self.fields['unita_tipo'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Configure grid weights
        id_frame.columnconfigure(1, weight=1)
        id_frame.columnconfigure(3, weight=1)
        
        # Excavation section
        exc_frame = ttk.LabelFrame(scrollable_frame, text="Dati di Scavo", padding=10)
        exc_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1
        
        # Anno scavo
        ttk.Label(exc_frame, text="Anno Scavo:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['anno_scavo'] = ttk.Entry(exc_frame, width=30)
        self.fields['anno_scavo'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Scavato
        ttk.Label(exc_frame, text="Scavato:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['scavato'] = ttk.Combobox(exc_frame, values=["Sì", "No", "Parzialmente"], width=20)
        self.fields['scavato'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Schedatore
        ttk.Label(exc_frame, text="Schedatore:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['schedatore'] = ttk.Entry(exc_frame, width=30)
        self.fields['schedatore'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Metodo di scavo
        ttk.Label(exc_frame, text="Metodo Scavo:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['metodo_di_scavo'] = ttk.Combobox(exc_frame, 
                                                    values=["Manuale", "Meccanico", "Misto"], width=20)
        self.fields['metodo_di_scavo'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Data schedatura
        ttk.Label(exc_frame, text="Data Schedatura:").grid(row=2, column=0, sticky="w", pady=5)
        self.fields['data_schedatura'] = ttk.Entry(exc_frame, width=30)
        self.fields['data_schedatura'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Attività
        ttk.Label(exc_frame, text="Attività:").grid(row=2, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['attivita'] = ttk.Entry(exc_frame, width=20)
        self.fields['attivita'].grid(row=2, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Configure grid weights
        exc_frame.columnconfigure(1, weight=1)
        exc_frame.columnconfigure(3, weight=1)
        
        # Configure main grid
        scrollable_frame.columnconfigure(0, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_description_tab(self):
        """Create descriptions tab"""
        desc_frame = ttk.Frame(self.notebook)
        self.notebook.add(desc_frame, text="Descrizioni")
        
        # Descrizione stratigrafica
        ttk.Label(desc_frame, text="Descrizione Stratigrafica:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.fields['d_stratigrafica'] = tk.Text(desc_frame, height=6, wrap=tk.WORD)
        self.fields['d_stratigrafica'].pack(fill=tk.X, padx=10, pady=5)
        
        # Descrizione interpretativa
        ttk.Label(desc_frame, text="Descrizione Interpretativa:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.fields['d_interpretativa'] = tk.Text(desc_frame, height=6, wrap=tk.WORD)
        self.fields['d_interpretativa'].pack(fill=tk.X, padx=10, pady=5)
        
        # Interpretazione
        ttk.Label(desc_frame, text="Interpretazione:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.fields['interpretazione'] = tk.Text(desc_frame, height=4, wrap=tk.WORD)
        self.fields['interpretazione'].pack(fill=tk.X, padx=10, pady=5)
        
        # Osservazioni
        ttk.Label(desc_frame, text="Osservazioni:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        self.fields['osservazioni'] = tk.Text(desc_frame, height=4, wrap=tk.WORD)
        self.fields['osservazioni'].pack(fill=tk.X, padx=10, pady=5)
    
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
        
        # Formation and characteristics
        char_frame = ttk.LabelFrame(scrollable_frame, text="Caratteristiche", padding=10)
        char_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1
        
        # Formazione
        ttk.Label(char_frame, text="Formazione:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['formazione'] = ttk.Combobox(char_frame, 
                                               values=["Naturale", "Artificiale", "Mista"], width=25)
        self.fields['formazione'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Stato di conservazione
        ttk.Label(char_frame, text="Stato Conservazione:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['stato_di_conservazione'] = ttk.Combobox(char_frame, 
                                                           values=["Ottimo", "Buono", "Discreto", "Cattivo"], width=25)
        self.fields['stato_di_conservazione'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Colore
        ttk.Label(char_frame, text="Colore:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['colore'] = ttk.Entry(char_frame, width=25)
        self.fields['colore'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Consistenza
        ttk.Label(char_frame, text="Consistenza:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['consistenza'] = ttk.Combobox(char_frame, 
                                                values=["Compatta", "Semicompatta", "Sciolta"], width=25)
        self.fields['consistenza'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Struttura
        ttk.Label(char_frame, text="Struttura:").grid(row=2, column=0, sticky="w", pady=5)
        self.fields['struttura'] = ttk.Entry(char_frame, width=25)
        self.fields['struttura'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        char_frame.columnconfigure(1, weight=1)
        char_frame.columnconfigure(3, weight=1)
        
        # Measurements
        meas_frame = ttk.LabelFrame(scrollable_frame, text="Misure", padding=10)
        meas_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1
        
        # Quote
        ttk.Label(meas_frame, text="Quota Relativa:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['quota_relativa'] = ttk.Entry(meas_frame, width=15)
        self.fields['quota_relativa'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(meas_frame, text="Quota Assoluta:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['quota_abs'] = ttk.Entry(meas_frame, width=15)
        self.fields['quota_abs'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Dimensioni
        ttk.Label(meas_frame, text="Lunghezza Max:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['lunghezza_max'] = ttk.Entry(meas_frame, width=15)
        self.fields['lunghezza_max'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(meas_frame, text="Larghezza Media:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['larghezza_media'] = ttk.Entry(meas_frame, width=15)
        self.fields['larghezza_media'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(meas_frame, text="Altezza Max:").grid(row=2, column=0, sticky="w", pady=5)
        self.fields['altezza_max'] = ttk.Entry(meas_frame, width=15)
        self.fields['altezza_max'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(meas_frame, text="Altezza Min:").grid(row=2, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['altezza_min'] = ttk.Entry(meas_frame, width=15)
        self.fields['altezza_min'].grid(row=2, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        meas_frame.columnconfigure(1, weight=1)
        meas_frame.columnconfigure(3, weight=1)
        
        scrollable_frame.columnconfigure(0, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_chronology_tab(self):
        """Create chronology/periodization tab"""
        chron_frame = ttk.Frame(self.notebook)
        self.notebook.add(chron_frame, text="Cronologia")
        
        # Current periodization display
        current_frame = ttk.LabelFrame(chron_frame, text="Periodizzazione Attuale", padding=10)
        current_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Define period values
        period_values = ["", "Paleolitico", "Mesolitico", "Neolitico", "Eneolitico", 
                        "Bronzo Antico", "Bronzo Medio", "Bronzo Finale", "Ferro I", "Ferro II", 
                        "Orientalizzante", "Arcaico", "Classico", "Ellenistico", "Romano Repubblicano",
                        "Romano Imperiale", "Tardo Antico", "Altomedievale", "Medievale", 
                        "Postmedievale", "Moderno", "Contemporaneo"]
        
        # Periodo iniziale
        ttk.Label(current_frame, text="Periodo Iniziale:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['periodo_iniziale'] = ttk.Combobox(current_frame, width=30, values=period_values)
        self.fields['periodo_iniziale'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Fase iniziale
        ttk.Label(current_frame, text="Fase Iniziale:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['fase_iniziale'] = ttk.Entry(current_frame, width=30)
        self.fields['fase_iniziale'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Periodo finale
        ttk.Label(current_frame, text="Periodo Finale:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['periodo_finale'] = ttk.Combobox(current_frame, width=30, values=period_values)
        self.fields['periodo_finale'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Fase finale
        ttk.Label(current_frame, text="Fase Finale:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['fase_finale'] = ttk.Entry(current_frame, width=30)
        self.fields['fase_finale'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Datazione
        ttk.Label(current_frame, text="Datazione:").grid(row=2, column=0, sticky="w", pady=5)
        self.fields['datazione'] = ttk.Entry(current_frame, width=30)
        self.fields['datazione'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Affidabilità
        ttk.Label(current_frame, text="Affidabilità:").grid(row=2, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['affidabilita'] = ttk.Combobox(current_frame, 
                                                 values=["Alta", "Media", "Bassa"], width=30)
        self.fields['affidabilita'].grid(row=2, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        current_frame.columnconfigure(1, weight=1)
        current_frame.columnconfigure(3, weight=1)
        
        # Advanced periodization section
        advanced_frame = ttk.LabelFrame(chron_frame, text="Periodizzazione Avanzata", padding=10)
        advanced_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons for advanced features
        button_frame = ttk.Frame(advanced_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Gestisci Periodizzazione Dettagliata", 
                  command=self.open_periodization_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Visualizza Sequenza Cronologica", 
                  command=self.show_chronological_sequence).pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = tk.Text(advanced_frame, height=8, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, pady=5)
        info_text.insert("1.0", "La periodizzazione avanzata permette di:\\n\\n"
                                "• Collegare periodi formali dal database\\n"
                                "• Specificare culture materiali\\n"
                                "• Aggiungere datazioni radiocarboniche\\n"
                                "• Definire livelli di affidabilità\\n"
                                "• Motivare le scelte cronologiche\\n\\n"
                                "Usa i pulsanti sopra per accedere alle funzionalità avanzate.")
        info_text.config(state=tk.DISABLED)
    
    def create_relationships_tab(self):
        """Create stratigraphic relationships tab"""
        rel_frame = ttk.Frame(self.notebook)
        self.notebook.add(rel_frame, text="Relazioni Stratigrafiche")
        
        # Controls
        controls_frame = ttk.Frame(rel_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Aggiungi Relazione", 
                  command=self.add_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Modifica Relazione", 
                  command=self.edit_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Elimina Relazione", 
                  command=self.delete_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Editor Harris Matrix", 
                  command=self.open_harris_editor).pack(side=tk.RIGHT, padx=5)
        
        # Relationships list
        list_frame = ttk.LabelFrame(rel_frame, text="Relazioni Esistenti", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for relationships
        self.relationships_tree = ttk.Treeview(list_frame, 
                                             columns=("Type", "Target_US", "Certainty", "Description"),
                                             show="headings", height=12)
        
        self.relationships_tree.heading("Type", text="Tipo Relazione")
        self.relationships_tree.heading("Target_US", text="US Correlata")
        self.relationships_tree.heading("Certainty", text="Certezza")
        self.relationships_tree.heading("Description", text="Descrizione")
        
        self.relationships_tree.column("Type", width=120)
        self.relationships_tree.column("Target_US", width=100)
        self.relationships_tree.column("Certainty", width=100)
        self.relationships_tree.column("Description", width=300)
        
        # Scrollbar
        rel_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                     command=self.relationships_tree.yview)
        self.relationships_tree.configure(yscrollcommand=rel_scrollbar.set)
        
        self.relationships_tree.pack(side="left", fill="both", expand=True)
        rel_scrollbar.pack(side="right", fill="y")
        
        # Load relationships if editing
        if self.us:
            self.load_relationships()
    
    def create_media_tab(self):
        """Create media management tab with thumbnails and drag & drop"""
        media_frame = ttk.Frame(self.notebook)
        self.notebook.add(media_frame, text="Media")
        
        # Create media storage directory
        self.media_dir = self.create_media_directory()
        
        # Media management section
        if self.us:
            # Top frame with drop zone
            drop_frame = ttk.LabelFrame(media_frame, text="Drag & Drop Files", padding=10)
            drop_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            # Drag and drop area
            self.drop_area = tk.Label(drop_frame, 
                                    text="Trascina qui i file multimediali\n(Immagini, PDF, Video, Audio)",
                                    relief="sunken", bd=2, height=3,
                                    bg="#f0f0f0", fg="#666666")
            self.drop_area.pack(fill=tk.X, pady=5)
            
            # Enable drag and drop
            self.setup_drag_drop()
            
            # Media grid with thumbnails
            media_list_frame = ttk.LabelFrame(media_frame, text="File Multimediali Associati", padding=10)
            media_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Create scrollable frame for media grid
            self.media_canvas = tk.Canvas(media_list_frame, height=200)
            media_scrollbar = ttk.Scrollbar(media_list_frame, orient="vertical", command=self.media_canvas.yview)
            self.media_scrollable_frame = ttk.Frame(self.media_canvas)
            
            self.media_scrollable_frame.bind(
                "<Configure>",
                lambda e: self.media_canvas.configure(scrollregion=self.media_canvas.bbox("all"))
            )
            
            self.media_canvas.create_window((0, 0), window=self.media_scrollable_frame, anchor="nw")
            self.media_canvas.configure(yscrollcommand=media_scrollbar.set)
            
            self.media_canvas.pack(side="left", fill="both", expand=True)
            media_scrollbar.pack(side="right", fill="y")
            
            # Media buttons
            media_button_frame = ttk.Frame(media_frame)
            media_button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(media_button_frame, text="Aggiungi File", 
                      command=self.add_media_file).pack(side=tk.LEFT, padx=5)
            ttk.Button(media_button_frame, text="Elimina Selezionati", 
                      command=self.delete_selected_media).pack(side=tk.LEFT, padx=5)
            ttk.Button(media_button_frame, text="Esporta Tutto", 
                      command=self.export_all_media).pack(side=tk.RIGHT, padx=5)
            
            # Store media items for selection
            self.media_items = []
            self.selected_media = []
            
            # Load existing media
            self.load_media_grid()
        else:
            # Info for new US
            info_frame = ttk.LabelFrame(media_frame, text="Gestione Media", padding=20)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            info_label = ttk.Label(info_frame, 
                                 text="La gestione dei file multimediali sarà disponibile\n"
                                      "dopo aver salvato la US.\n\n"
                                      "Potrai associare:\n"
                                      "• Fotografie dello scavo\n"
                                      "• Documenti tecnici\n"
                                      "• Disegni e planimetrie\n"
                                      "• Video documentari\n"
                                      "• File audio",
                                 justify="center")
            info_label.pack(pady=20)
    
    def create_documentation_tab(self):
        """Create documentation tab"""
        doc_frame = ttk.Frame(self.notebook)
        self.notebook.add(doc_frame, text="Documentazione")
        
        # Documentation fields
        doc_fields_frame = ttk.LabelFrame(doc_frame, text="Documentazione", padding=10)
        doc_fields_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Inclusi
        ttk.Label(doc_fields_frame, text="Inclusi:").grid(row=0, column=0, sticky="nw", pady=5)
        self.fields['inclusi'] = tk.Text(doc_fields_frame, height=3, width=50)
        self.fields['inclusi'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Campioni
        ttk.Label(doc_fields_frame, text="Campioni:").grid(row=1, column=0, sticky="nw", pady=5)
        self.fields['campioni'] = tk.Text(doc_fields_frame, height=3, width=50)
        self.fields['campioni'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Documentazione
        ttk.Label(doc_fields_frame, text="Documentazione:").grid(row=2, column=0, sticky="nw", pady=5)
        self.fields['documentazione'] = tk.Text(doc_fields_frame, height=3, width=50)
        self.fields['documentazione'].grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        doc_fields_frame.columnconfigure(1, weight=1)
        
        # Additional fields
        additional_frame = ttk.LabelFrame(doc_frame, text="Informazioni Aggiuntive", padding=10)
        additional_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Direttore US
        ttk.Label(additional_frame, text="Direttore US:").grid(row=0, column=0, sticky="w", pady=5)
        self.fields['direttore_us'] = ttk.Entry(additional_frame, width=30)
        self.fields['direttore_us'].grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Responsabile US
        ttk.Label(additional_frame, text="Responsabile US:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['responsabile_us'] = ttk.Entry(additional_frame, width=30)
        self.fields['responsabile_us'].grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Flottazione
        ttk.Label(additional_frame, text="Flottazione:").grid(row=1, column=0, sticky="w", pady=5)
        self.fields['flottazione'] = ttk.Combobox(additional_frame, values=["Sì", "No"], width=30)
        self.fields['flottazione'].grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Setacciatura
        ttk.Label(additional_frame, text="Setacciatura:").grid(row=1, column=2, sticky="w", pady=5, padx=(20, 0))
        self.fields['setacciatura'] = ttk.Combobox(additional_frame, values=["Sì", "No"], width=30)
        self.fields['setacciatura'].grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        additional_frame.columnconfigure(1, weight=1)
        additional_frame.columnconfigure(3, weight=1)
    
    def populate_form(self):
        """Populate form with existing US data"""
        if not self.us:
            return
        
        # Basic fields
        self.fields['sito'].set(self.us.sito or "")
        
        # Text fields
        text_fields = ['area', 'us', 'schedatore', 'anno_scavo', 'unita_tipo', 'scavato', 
                      'metodo_di_scavo', 'data_schedatura', 'attivita', 'formazione',
                      'stato_di_conservazione', 'colore', 'consistenza', 'struttura',
                      'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
                      'datazione', 'affidabilita', 'direttore_us', 'responsabile_us',
                      'flottazione', 'setacciatura']
        
        for field in text_fields:
            if field in self.fields and hasattr(self.us, field):
                value = getattr(self.us, field)
                if value is not None:
                    if isinstance(self.fields[field], ttk.Entry):
                        self.fields[field].insert(0, str(value))
                    elif isinstance(self.fields[field], ttk.Combobox):
                        self.fields[field].set(str(value))
        
        # Numeric fields
        numeric_fields = ['quota_relativa', 'quota_abs', 'lunghezza_max', 'altezza_max',
                         'altezza_min', 'profondita_max', 'profondita_min', 'larghezza_media']
        
        for field in numeric_fields:
            if field in self.fields and hasattr(self.us, field):
                value = getattr(self.us, field)
                if value is not None:
                    self.fields[field].insert(0, str(value))
        
        # Text areas
        text_areas = ['d_stratigrafica', 'd_interpretativa', 'interpretazione', 'osservazioni',
                     'inclusi', 'campioni', 'documentazione']
        
        for field in text_areas:
            if field in self.fields and hasattr(self.us, field):
                value = getattr(self.us, field)
                if value is not None:
                    self.fields[field].insert("1.0", str(value))
    
    def load_relationships(self):
        """Load stratigraphic relationships for current US"""
        if not self.us:
            return

        # Clear existing relationships
        for item in self.relationships_tree.get_children():
            self.relationships_tree.delete(item)

        try:
            # Load from US rapporti field (format: "copre 1002, taglia 1005")
            if hasattr(self.us, 'rapporti') and self.us.rapporti:
                rapporti_str = self.us.rapporti

                # Parse relationships
                if rapporti_str.strip():
                    parts = rapporti_str.split(',')
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue

                        # Split "copre 1002" into ["copre", "1002"]
                        tokens = part.split()
                        if len(tokens) >= 2:
                            rel_type = ' '.join(tokens[:-1])  # Everything except last token
                            target_us = tokens[-1]  # Last token is US number

                            # Add to TreeView: (Type, Target_US, Certainty, Description)
                            self.relationships_tree.insert("", "end", values=(
                                rel_type,      # Type: "copre", "taglia", etc
                                target_us,     # Target US number
                                "certa",       # Certainty (default)
                                ""             # Description (empty)
                            ))

        except Exception as e:
            print(f"Error loading relationships: {e}")
            # Don't show error to user, just log it
    
    def add_relationship(self):
        """Add new stratigraphic relationship"""
        if not self.us:
            messagebox.showwarning("Avviso", "Salva prima la US")
            return

        # Create simple relationship dialog
        RelationshipDialog(self.window, self.us, self.matrix_generator,
                         callback=self.load_relationships, parent_dialog=self)
    
    def edit_relationship(self):
        """Edit selected relationship"""
        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona una relazione da modificare")
            return
        
        # Get selected relationship data
        item = selection[0]
        values = self.relationships_tree.item(item, 'values')
        if not values or len(values) < 2:
            messagebox.showerror("Errore", "Dati relazione non validi")
            return

        # TreeView columns: ("Type", "Target_US", "Certainty", "Description")
        old_rel_type, old_us_correlata = values[0], values[1]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Modifica Relazione")
        edit_window.geometry("400x300")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Modifica relazione per US {self.us.us}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Relationship type
        ttk.Label(main_frame, text="Tipo Relazione:").pack(anchor="w")
        rel_type_var = ttk.Combobox(main_frame, 
                                   values=["copre", "coperto da", "taglia", "tagliato da", 
                                          "riempie", "riempito da", "si appoggia", "gli si appoggia",
                                          "si lega a", "uguale a"],
                                   width=30)
        rel_type_var.pack(fill=tk.X, pady=5)
        rel_type_var.set(old_rel_type)
        
        # Target US
        ttk.Label(main_frame, text="US Correlata:").pack(anchor="w", pady=(10, 0))
        target_us_var = ttk.Entry(main_frame, width=30)
        target_us_var.pack(fill=tk.X, pady=5)
        target_us_var.insert(0, old_us_correlata)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def save_changes():
            new_rel_type = rel_type_var.get().strip()
            new_us_correlata = target_us_var.get().strip()
            
            if not new_rel_type or not new_us_correlata:
                messagebox.showerror("Errore", "Compila tutti i campi")
                return
            
            try:
                # Validate target US is numeric
                int(new_us_correlata)
            except ValueError:
                messagebox.showerror("Errore", "US correlata deve essere numerica")
                return
            
            try:
                # Remove old relationship and add new one
                current_rapporti = getattr(self.us, 'rapporti', [])
                if isinstance(current_rapporti, str):
                    try:
                        current_rapporti = eval(current_rapporti)
                    except:
                        current_rapporti = []
                elif not isinstance(current_rapporti, list):
                    current_rapporti = []
                
                # Remove old relationship
                updated_rapporti = []
                for rel in current_rapporti:
                    try:
                        if isinstance(rel, str):
                            parsed_rel = eval(rel)
                        else:
                            parsed_rel = rel
                        
                        if (isinstance(parsed_rel, (list, tuple)) and len(parsed_rel) >= 2 and
                            parsed_rel[0] == old_rel_type and str(parsed_rel[1]).replace('US_', '') == str(old_us_correlata)):
                            continue  # Skip old relationship
                        else:
                            updated_rapporti.append(rel)
                    except:
                        updated_rapporti.append(rel)
                
                # Add new relationship
                new_relationship = [new_rel_type, f"US_{new_us_correlata}"]
                updated_rapporti.append(str(new_relationship))
                
                # Update US
                self.us.rapporti = updated_rapporti

                # Update tree - columns: ("Type", "Target_US", "Certainty", "Description")
                self.relationships_tree.item(item, values=(new_rel_type, new_us_correlata, "certa", ""))
                
                edit_window.destroy()
                messagebox.showinfo("Successo", "Relazione modificata con successo")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore modifica relazione: {str(e)}")
        
        ttk.Button(button_frame, text="Salva", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_relationship(self):
        """Delete selected relationship"""
        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Selezione", "Seleziona una relazione da eliminare")
            return
        
        # Get selected relationship data
        item = selection[0]
        values = self.relationships_tree.item(item, 'values')
        if not values or len(values) < 2:
            messagebox.showerror("Errore", "Dati relazione non validi")
            return

        # TreeView columns: ("Type", "Target_US", "Certainty", "Description")
        rel_type, us_correlata = values[0], values[1]
        
        if messagebox.askyesno("Conferma", f"Eliminare la relazione:\n{self.us.us} {rel_type} {us_correlata}?"):
            try:
                # Remove from rapporti field
                current_rapporti = getattr(self.us, 'rapporti', [])
                if isinstance(current_rapporti, str):
                    try:
                        current_rapporti = eval(current_rapporti)
                    except:
                        current_rapporti = []
                elif not isinstance(current_rapporti, list):
                    current_rapporti = []
                
                # Find and remove the relationship
                updated_rapporti = []
                for rel in current_rapporti:
                    try:
                        if isinstance(rel, str):
                            parsed_rel = eval(rel)
                        else:
                            parsed_rel = rel
                        
                        if (isinstance(parsed_rel, (list, tuple)) and len(parsed_rel) >= 2 and
                            parsed_rel[0] == rel_type and str(parsed_rel[1]).replace('US_', '') == str(us_correlata)):
                            continue  # Skip this relationship (delete it)
                        else:
                            updated_rapporti.append(rel)
                    except:
                        updated_rapporti.append(rel)  # Keep if can't parse
                
                # Update the US rapporti field
                self.us.rapporti = updated_rapporti
                
                # Remove from tree
                self.relationships_tree.delete(item)
                
                messagebox.showinfo("Successo", "Relazione eliminata con successo")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore eliminazione relazione: {str(e)}")
    
    def open_harris_editor(self):
        """Open Harris Matrix editor"""
        if not self.us or not hasattr(self.us, 'sito'):
            messagebox.showwarning("Avviso", "Salva prima la US")
            return
        
        try:
            from desktop_gui.harris_matrix_editor import HarrisMatrixEditor
            from pyarchinit_mini.services.site_service import SiteService
            from pyarchinit_mini.services.us_service import USService
            from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
            from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
            
            # Create necessary services
            site_service = SiteService(self.db_manager)
            us_service = USService(self.db_manager)
            matrix_generator = HarrisMatrixGenerator(self.db_manager, us_service)
            matrix_visualizer = PyArchInitMatrixVisualizer()
            
            # Create and show the Harris Matrix editor
            editor = HarrisMatrixEditor(
                self.window, 
                matrix_generator, 
                matrix_visualizer, 
                site_service, 
                us_service
            )
            
            # Set current site from US
            if hasattr(self.us, 'sito') and self.us.sito:
                editor.current_site = self.us.sito
                # Set the site combo box if it exists
                if hasattr(editor, 'site_var'):
                    editor.site_var.set(self.us.sito)
                # Trigger site change to load data
                editor.on_site_changed()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore apertura Harris Matrix Editor: {str(e)}")
    
    def open_periodization_dialog(self):
        """Open detailed periodization dialog"""
        if not self.us:
            messagebox.showwarning("Avviso", "Salva prima la US")
            return
        
        # Create detailed periodization dialog
        PeriodizationDialog(self.window, self.us, self.periodizzazione_service, 
                          callback=self.refresh_periodization_data)
    
    def refresh_periodization_data(self):
        """Refresh periodization data in form"""
        if not self.us:
            return
        
        try:
            # Get updated periodization data
            # TODO: Implement when periodization service is properly integrated
            messagebox.showinfo("Aggiornamento", "Dati di periodizzazione aggiornati")
            
        except Exception as e:
            print(f"Error refreshing periodization data: {e}")
    
    def show_chronological_sequence(self):
        """Show chronological sequence for site"""
        if not self.fields['sito'].get():
            messagebox.showwarning("Avviso", "Seleziona un sito")
            return
        
        # Create chronological sequence dialog
        ChronologicalSequenceDialog(self.window, self.fields['sito'].get(), 
                                   self.us_service, self.periodizzazione_service)
    
    def create_media_directory(self):
        """Create media directory structure"""
        try:
            base_dir = os.path.join(os.getcwd(), "media")
            if self.us:
                site_dir = os.path.join(base_dir, self.us.sito.replace(" ", "_"))
                us_dir = os.path.join(site_dir, f"US_{self.us.us}")
                thumb_dir = os.path.join(us_dir, "thumbnails")
            else:
                us_dir = os.path.join(base_dir, "temp")
                thumb_dir = os.path.join(us_dir, "thumbnails")
            
            os.makedirs(us_dir, exist_ok=True)
            os.makedirs(thumb_dir, exist_ok=True)
            
            return us_dir
            
        except Exception as e:
            print(f"Error creating media directory: {e}")
            return os.path.join(os.getcwd(), "media")
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Bind drag and drop events
        self.drop_area.bind("<Button-1>", self.on_drop_click)
        
        # Enable file drop (platform specific)
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            # If tkinterdnd2 is available, use it
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self.on_file_drop)
        except ImportError:
            # Fallback to basic implementation
            self.drop_area.bind("<Button-1>", self.add_media_file)
    
    def on_drop_click(self, event):
        """Handle click on drop area"""
        self.add_media_file()
    
    def on_file_drop(self, event):
        """Handle file drop"""
        files = event.data.split()
        for file_path in files:
            if os.path.isfile(file_path):
                self.process_dropped_file(file_path)
    
    def process_dropped_file(self, file_path):
        """Process a dropped file"""
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.media_dir, filename)
            
            # Copy file to media directory
            shutil.copy2(file_path, dest_path)
            
            # Create thumbnail if it's an image
            self.create_thumbnail(dest_path)
            
            # Refresh media grid
            self.load_media_grid()
            
            messagebox.showinfo("Successo", f"File {filename} aggiunto con successo")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiunta del file: {str(e)}")
    
    def create_thumbnail(self, file_path):
        """Create thumbnail for image files"""
        try:
            # Check if it's an image
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                return None
            
            # Open and resize image
            with Image.open(file_path) as img:
                # Calculate size maintaining aspect ratio
                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_dir = os.path.join(self.media_dir, "thumbnails")
                thumb_name = f"thumb_{os.path.basename(file_path)}"
                thumb_path = os.path.join(thumb_dir, thumb_name)
                
                img.save(thumb_path, "JPEG", quality=85)
                return thumb_path
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def load_media_grid(self):
        """Load media files in grid with thumbnails"""
        try:
            # Clear existing media items
            for widget in self.media_scrollable_frame.winfo_children():
                widget.destroy()
            
            self.media_items = []
            
            if not os.path.exists(self.media_dir):
                return
            
            # Get all files in media directory
            files = [f for f in os.listdir(self.media_dir) 
                    if os.path.isfile(os.path.join(self.media_dir, f)) and f != ".DS_Store"]
            
            # Create grid layout
            cols = 4
            for i, filename in enumerate(files):
                row = i // cols
                col = i % cols
                
                self.create_media_item(filename, row, col)
                
        except Exception as e:
            print(f"Error loading media grid: {e}")
    
    def create_media_item(self, filename, row, col):
        """Create a media item widget"""
        try:
            file_path = os.path.join(self.media_dir, filename)
            
            # Create frame for media item
            item_frame = ttk.Frame(self.media_scrollable_frame, relief="raised", borderwidth=1)
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Try to load thumbnail or create generic icon
            thumb_path = os.path.join(self.media_dir, "thumbnails", f"thumb_{filename}")
            
            if os.path.exists(thumb_path):
                # Load thumbnail
                img = Image.open(thumb_path)
                photo = ImageTk.PhotoImage(img)
            else:
                # Create generic icon based on file type
                photo = self.create_file_icon(filename)
            
            # Thumbnail label
            thumb_label = tk.Label(item_frame, image=photo, cursor="hand2")
            thumb_label.image = photo  # Keep a reference
            thumb_label.pack(pady=2)
            
            # Filename label
            name_label = tk.Label(item_frame, text=filename[:15] + ("..." if len(filename) > 15 else ""),
                                font=("Arial", 8), wraplength=100)
            name_label.pack()
            
            # File size
            file_size = os.path.getsize(file_path)
            size_text = self.format_file_size(file_size)
            size_label = tk.Label(item_frame, text=size_text, font=("Arial", 7), fg="gray")
            size_label.pack()
            
            # Bind click events
            for widget in [thumb_label, name_label, size_label, item_frame]:
                widget.bind("<Button-1>", lambda e, f=filename: self.on_media_select(f))
                widget.bind("<Double-Button-1>", lambda e, f=filename: self.view_media_file(f))
            
            self.media_items.append({
                'filename': filename,
                'frame': item_frame,
                'selected': False
            })
            
        except Exception as e:
            print(f"Error creating media item for {filename}: {e}")
    
    def create_file_icon(self, filename):
        """Create a generic file icon"""
        try:
            # Create a simple colored rectangle as icon
            img = Image.new('RGB', (100, 100), color='lightgray')
            
            # Determine color based on file type
            ext = filename.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                color = 'lightblue'
            elif ext in ['pdf']:
                color = 'lightcoral'
            elif ext in ['doc', 'docx', 'txt']:
                color = 'lightgreen'
            elif ext in ['mp4', 'avi', 'mov']:
                color = 'lightyellow'
            else:
                color = 'lightgray'
            
            img = Image.new('RGB', (100, 100), color=color)
            return ImageTk.PhotoImage(img)
            
        except Exception:
            # Fallback to empty image
            img = Image.new('RGB', (100, 100), color='white')
            return ImageTk.PhotoImage(img)
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    def on_media_select(self, filename):
        """Handle media item selection"""
        for item in self.media_items:
            if item['filename'] == filename:
                item['selected'] = not item['selected']
                # Update visual selection
                if item['selected']:
                    item['frame'].configure(relief="solid", borderwidth=2)
                    if filename not in self.selected_media:
                        self.selected_media.append(filename)
                else:
                    item['frame'].configure(relief="raised", borderwidth=1)
                    if filename in self.selected_media:
                        self.selected_media.remove(filename)
                break
    
    def add_media_file(self, event=None):
        """Add new media file"""
        file_paths = filedialog.askopenfilenames(
            title="Seleziona file multimediali",
            filetypes=[
                ("Tutti i file supportati", "*.jpg *.jpeg *.png *.gif *.pdf *.doc *.docx *.mp4 *.avi"),
                ("Immagini", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("Documenti", "*.pdf *.doc *.docx *.txt"),
                ("Video", "*.mp4 *.avi *.mov *.mkv"),
                ("Audio", "*.mp3 *.wav *.m4a"),
                ("Tutti i file", "*.*")
            ]
        )
        
        if file_paths:
            for file_path in file_paths:
                self.process_dropped_file(file_path)
    
    def view_media_file(self, filename=None):
        """View selected media file"""
        if filename is None:
            if not self.selected_media:
                messagebox.showwarning("Selezione", "Seleziona un file da visualizzare")
                return
            filename = self.selected_media[0]
        
        file_path = os.path.join(self.media_dir, filename)
        
        if os.path.exists(file_path):
            try:
                # Try to open with default system application
                import subprocess
                import platform
                
                if platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', file_path])
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(file_path)
                else:  # Linux
                    subprocess.call(['xdg-open', file_path])
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire il file: {str(e)}")
        else:
            messagebox.showerror("Errore", "File non trovato")
    
    def delete_selected_media(self):
        """Delete selected media files"""
        if not self.selected_media:
            messagebox.showwarning("Selezione", "Seleziona uno o più file da eliminare")
            return
        
        files_text = "\n".join(self.selected_media)
        if messagebox.askyesno("Conferma", f"Eliminare i seguenti file?\n\n{files_text}"):
            try:
                for filename in self.selected_media:
                    file_path = os.path.join(self.media_dir, filename)
                    thumb_path = os.path.join(self.media_dir, "thumbnails", f"thumb_{filename}")
                    
                    # Delete main file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # Delete thumbnail
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                
                self.selected_media.clear()
                self.load_media_grid()
                messagebox.showinfo("Successo", "File eliminati con successo")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione: {str(e)}")
    
    def export_all_media(self):
        """Export all media files"""
        export_dir = filedialog.askdirectory(title="Seleziona cartella di esportazione")
        if export_dir:
            try:
                if not os.path.exists(self.media_dir):
                    messagebox.showwarning("Avviso", "Nessun file media da esportare")
                    return
                
                files = [f for f in os.listdir(self.media_dir) 
                        if os.path.isfile(os.path.join(self.media_dir, f)) and not f.startswith('.')]
                
                if not files:
                    messagebox.showwarning("Avviso", "Nessun file media da esportare")
                    return
                
                # Create destination directory
                dest_dir = os.path.join(export_dir, f"{self.us.sito}_US_{self.us.us}_media")
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy files
                for filename in files:
                    src_path = os.path.join(self.media_dir, filename)
                    dst_path = os.path.join(dest_dir, filename)
                    shutil.copy2(src_path, dst_path)
                
                messagebox.showinfo("Successo", 
                                  f"Esportati {len(files)} file in:\n{dest_dir}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'esportazione: {str(e)}")
    
    def save_us(self):
        """Save US data"""
        try:
            # Validate required fields
            if not self.fields['sito'].get().strip():
                messagebox.showerror("Errore", "Il sito è obbligatorio")
                return
            
            if not self.fields['us'].get().strip():
                messagebox.showerror("Errore", "Il numero US è obbligatorio")
                return
            
            # Prepare data
            us_data = {}
            
            # String fields
            string_fields = ['sito', 'area', 'schedatore', 'unita_tipo', 'scavato', 
                           'metodo_di_scavo', 'data_schedatura', 'attivita', 'formazione',
                           'stato_di_conservazione', 'colore', 'consistenza', 'struttura',
                           'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
                           'datazione', 'affidabilita', 'direttore_us', 'responsabile_us',
                           'flottazione', 'setacciatura']
            
            for field in string_fields:
                if field in self.fields:
                    if isinstance(self.fields[field], ttk.Entry) or isinstance(self.fields[field], ttk.Combobox):
                        value = self.fields[field].get().strip()
                        if value:
                            us_data[field] = value
            
            # Numeric fields
            try:
                us_number = int(self.fields['us'].get().strip())
                us_data['us'] = us_number
            except ValueError:
                messagebox.showerror("Errore", "Il numero US deve essere un numero")
                return
            
            # Year field
            if self.fields['anno_scavo'].get().strip():
                try:
                    us_data['anno_scavo'] = int(self.fields['anno_scavo'].get().strip())
                except ValueError:
                    messagebox.showerror("Errore", "L'anno di scavo deve essere un numero")
                    return
            
            # Float fields
            float_fields = ['quota_relativa', 'quota_abs', 'lunghezza_max', 'altezza_max',
                           'altezza_min', 'profondita_max', 'profondita_min', 'larghezza_media']
            
            for field in float_fields:
                if field in self.fields and self.fields[field].get().strip():
                    try:
                        us_data[field] = float(self.fields[field].get().strip())
                    except ValueError:
                        messagebox.showerror("Errore", f"Il campo {field} deve essere un numero")
                        return
            
            # Text areas
            text_areas = ['d_stratigrafica', 'd_interpretativa', 'interpretazione', 'osservazioni',
                         'inclusi', 'campioni', 'documentazione']
            
            for field in text_areas:
                if field in self.fields:
                    value = self.fields[field].get("1.0", tk.END).strip()
                    if value:
                        us_data[field] = value

            # Collect stratigraphic relationships from TreeView
            relationships_list = []
            for item in self.relationships_tree.get_children():
                values = self.relationships_tree.item(item, 'values')
                if values and len(values) >= 2:
                    rel_type = values[0]  # Type of relationship
                    target_us = values[1]  # Target US number
                    # Format as "Type TargetUS"
                    relationships_list.append(f"{rel_type} {target_us}")

            # Save relationships to rapporti field
            if relationships_list:
                us_data['rapporti'] = ", ".join(relationships_list)
            elif 'rapporti' in us_data:
                # Clear rapporti if no relationships
                us_data['rapporti'] = ""

            # Save US
            if self.us_id:
                # Update existing - use DTO method to avoid session issues
                updated_us = self.us_service.update_us_dto(self.us_id, us_data)
                messagebox.showinfo("Successo", "US aggiornata con successo")
            else:
                # Create new
                new_us = self.us_service.create_us(us_data)
                messagebox.showinfo("Successo", "US creata con successo")
            
            # Call callback
            if self.callback:
                self.callback()
            
            # Close dialog
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")
    
    def delete_us(self):
        """Delete current US"""
        if not self.us_id:
            return

        if messagebox.askyesno("Conferma", f"Eliminare la US {self.us_number}?"):
            try:
                self.us_service.delete_us(self.us_id)
                messagebox.showinfo("Successo", "US eliminata con successo")
                
                if self.callback:
                    self.callback()
                
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione: {str(e)}")

    def export_pdf(self):
        """Export current US record as PDF"""
        try:
            if not self.us:
                messagebox.showwarning("Avviso", "Nessuna US da esportare")
                return

            from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator

            # Convert DTO to dict manually
            us_data = {}
            for attr in dir(self.us):
                if not attr.startswith('_') and not callable(getattr(self.us, attr)):
                    value = getattr(self.us, attr)
                    # Convert datetime to string
                    if hasattr(value, 'isoformat'):
                        us_data[attr] = str(value)
                    else:
                        us_data[attr] = value

            # Get save location
            export_path = filedialog.asksaveasfilename(
                title="Esporta US come PDF",
                defaultextension=".pdf",
                filetypes=[("File PDF", "*.pdf"), ("Tutti i file", "*.*")],
                initialfile=f"US_{self.us.us}_{self.us.sito.replace(' ', '_')}.pdf"
            )

            if export_path:
                # Generate PDF
                generator = PDFGenerator()
                pdf_path = generator.generate_us_pdf(
                    site_name=self.us.sito,
                    us_list=[us_data],
                    output_path=export_path,
                    logo_path=None
                )
                messagebox.showinfo("Successo", f"PDF esportato in:\n{pdf_path}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione PDF: {str(e)}")
            print(f"Export PDF error: {e}")
            import traceback
            traceback.print_exc()

    def cancel(self):
        """Cancel and close dialog"""
        self.window.destroy()

class RelationshipDialog:
    """Simple dialog for adding stratigraphic relationships"""

    def __init__(self, parent, us, matrix_generator, callback=None, parent_dialog=None):
        self.parent = parent
        self.us = us
        self.matrix_generator = matrix_generator
        self.callback = callback
        self.parent_dialog = parent_dialog  # Reference to ExtendedUSDialog for TreeView access
        
        # Create dialog
        self.window = tk.Toplevel(parent)
        self.window.title("Nuova Relazione Stratigrafica")
        self.window.geometry("500x450")
        self.window.resizable(True, True)
        self.window.minsize(450, 400)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
    
    def create_interface(self):
        """Create relationship dialog interface"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Current US
        ttk.Label(main_frame, text=f"US Corrente: {self.us.us}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Relationship type
        ttk.Label(main_frame, text="Tipo Relazione:").pack(anchor="w")
        self.rel_type = ttk.Combobox(main_frame, 
                                   values=["copre", "coperto da", "taglia", "tagliato da", 
                                          "riempie", "riempito da", "si appoggia", "gli si appoggia",
                                          "si lega a", "uguale a"],
                                   width=30)
        self.rel_type.pack(fill=tk.X, pady=5)
        self.rel_type.set("copre")
        
        # Target US
        ttk.Label(main_frame, text="US Correlata:").pack(anchor="w", pady=(10, 0))
        self.target_us = ttk.Entry(main_frame, width=30)
        self.target_us.pack(fill=tk.X, pady=5)
        
        # Certainty
        ttk.Label(main_frame, text="Certezza:").pack(anchor="w", pady=(10, 0))
        self.certainty = ttk.Combobox(main_frame, 
                                    values=["certa", "probabile", "dubbia", "ipotetica"],
                                    width=30)
        self.certainty.pack(fill=tk.X, pady=5)
        self.certainty.set("certa")
        
        # Description
        ttk.Label(main_frame, text="Descrizione:").pack(anchor="w", pady=(10, 0))
        self.description = tk.Text(main_frame, height=4, width=30)
        self.description.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Salva", command=self.save_relationship).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def save_relationship(self):
        """Save the relationship"""
        try:
            target_us_str = self.target_us.get().strip()
            if not target_us_str:
                messagebox.showerror("Errore", "Inserisci il numero della US correlata")
                return

            try:
                target_us_num = int(target_us_str)
            except ValueError:
                messagebox.showerror("Errore", "Il numero US deve essere un numero")
                return

            rel_type = self.rel_type.get()
            certainty = self.certainty.get()
            description = self.description.get("1.0", tk.END).strip()

            # Add relationship directly to parent dialog's TreeView
            if self.parent_dialog and hasattr(self.parent_dialog, 'relationships_tree'):
                # Format: Type, Target_US, Certainty, Description
                self.parent_dialog.relationships_tree.insert("", "end", values=(
                    rel_type,           # Type
                    target_us_num,      # Target US
                    certainty,          # Certainty
                    description         # Description
                ))
                messagebox.showinfo("Successo", "Relazione aggiunta alla lista.\nRicorda di salvare la US per confermare.")
                # DON'T call callback - it would reload from DB and clear the new relationship!
                # The relationship will be saved when the US is saved
                self.window.destroy()
            else:
                messagebox.showerror("Errore", "Errore nell'aggiunta della relazione")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore: {str(e)}")
    
    def cancel(self):
        """Cancel dialog"""
        self.window.destroy()


class PeriodizationDialog:
    """Dialog for detailed periodization management"""
    
    def __init__(self, parent, us, periodizzazione_service, callback=None):
        self.parent = parent
        self.us = us
        self.periodizzazione_service = periodizzazione_service
        self.callback = callback
        
        # Create dialog
        self.window = tk.Toplevel(parent)
        self.window.title(f"Periodizzazione Dettagliata - US {us.us}")
        self.window.geometry("700x500")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
        self.load_periodization_data()
    
    def create_interface(self):
        """Create periodization interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=f"Gestione Periodizzazione", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"US {self.us.us} - {self.us.sito}", 
                 font=("Arial", 10)).pack(side=tk.RIGHT)
        
        # Create notebook for different periodization aspects
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_chronology_tab()
        self.create_phases_tab()
        self.create_dating_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Salva", command=self.save_periodization).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def create_chronology_tab(self):
        """Create chronology tab"""
        chron_frame = ttk.Frame(self.notebook)
        self.notebook.add(chron_frame, text="Cronologia")
        
        # Periods section
        periods_frame = ttk.LabelFrame(chron_frame, text="Periodi Cronologici", padding=10)
        periods_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Initial period
        ttk.Label(periods_frame, text="Periodo Iniziale:").grid(row=0, column=0, sticky="w", pady=5)
        self.periodo_iniziale = ttk.Combobox(periods_frame, width=30,
                                           values=["Neolitico", "Bronzo Antico", "Bronzo Medio", 
                                                 "Bronzo Finale", "Ferro I", "Ferro II", "Romano",
                                                 "Medievale", "Post-medievale", "Moderno"])
        self.periodo_iniziale.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Final period
        ttk.Label(periods_frame, text="Periodo Finale:").grid(row=1, column=0, sticky="w", pady=5)
        self.periodo_finale = ttk.Combobox(periods_frame, width=30,
                                         values=["Neolitico", "Bronzo Antico", "Bronzo Medio", 
                                               "Bronzo Finale", "Ferro I", "Ferro II", "Romano",
                                               "Medievale", "Post-medievale", "Moderno"])
        self.periodo_finale.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        periods_frame.columnconfigure(1, weight=1)
    
    def create_phases_tab(self):
        """Create phases tab"""
        phases_frame = ttk.Frame(self.notebook)
        self.notebook.add(phases_frame, text="Fasi")
        
        # Phases section
        phases_section = ttk.LabelFrame(phases_frame, text="Fasi Cronologiche", padding=10)
        phases_section.pack(fill=tk.X, padx=10, pady=10)
        
        # Initial phase
        ttk.Label(phases_section, text="Fase Iniziale:").grid(row=0, column=0, sticky="w", pady=5)
        self.fase_iniziale = ttk.Entry(phases_section, width=40)
        self.fase_iniziale.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Final phase
        ttk.Label(phases_section, text="Fase Finale:").grid(row=1, column=0, sticky="w", pady=5)
        self.fase_finale = ttk.Entry(phases_section, width=40)
        self.fase_finale.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        phases_section.columnconfigure(1, weight=1)
        
        # Phase details
        details_frame = ttk.LabelFrame(phases_frame, text="Dettagli Fase", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(details_frame, text="Descrizione Fase:").pack(anchor="w")
        self.phase_description = tk.Text(details_frame, height=8, wrap=tk.WORD)
        self.phase_description.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def create_dating_tab(self):
        """Create dating tab"""
        dating_frame = ttk.Frame(self.notebook)
        self.notebook.add(dating_frame, text="Datazione")
        
        # Dating methods
        methods_frame = ttk.LabelFrame(dating_frame, text="Metodi di Datazione", padding=10)
        methods_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Dating method
        ttk.Label(methods_frame, text="Metodo:").grid(row=0, column=0, sticky="w", pady=5)
        self.dating_method = ttk.Combobox(methods_frame, width=30,
                                        values=["Stratigrafico", "Radiocarbonio", "Tipologico",
                                              "Ceramico", "Numismatico", "Archeomagnetico"])
        self.dating_method.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Dating certainty
        ttk.Label(methods_frame, text="Certezza:").grid(row=1, column=0, sticky="w", pady=5)
        self.dating_certainty = ttk.Combobox(methods_frame, width=30,
                                           values=["Alta", "Media", "Bassa", "Ipotetica"])
        self.dating_certainty.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        methods_frame.columnconfigure(1, weight=1)
        
        # Date ranges
        ranges_frame = ttk.LabelFrame(dating_frame, text="Intervalli Cronologici", padding=10)
        ranges_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start date
        ttk.Label(ranges_frame, text="Data Iniziale:").grid(row=0, column=0, sticky="w", pady=5)
        self.start_date = ttk.Entry(ranges_frame, width=20)
        self.start_date.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        ttk.Label(ranges_frame, text="(formato: -500 per 500 a.C.)").grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        # End date
        ttk.Label(ranges_frame, text="Data Finale:").grid(row=1, column=0, sticky="w", pady=5)
        self.end_date = ttk.Entry(ranges_frame, width=20)
        self.end_date.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        ttk.Label(ranges_frame, text="(formato: 100 per 100 d.C.)").grid(row=1, column=2, sticky="w", padx=(10, 0))
        
        ranges_frame.columnconfigure(1, weight=1)
        
        # Bibliography
        biblio_frame = ttk.LabelFrame(dating_frame, text="Bibliografia", padding=10)
        biblio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(biblio_frame, text="Riferimenti Bibliografici:").pack(anchor="w")
        self.bibliography = tk.Text(biblio_frame, height=6, wrap=tk.WORD)
        self.bibliography.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def load_periodization_data(self):
        """Load existing periodization data"""
        try:
            # Load from US data if available
            if hasattr(self.us, 'periodo_iniziale') and self.us.periodo_iniziale:
                self.periodo_iniziale.set(self.us.periodo_iniziale)
            if hasattr(self.us, 'periodo_finale') and self.us.periodo_finale:
                self.periodo_finale.set(self.us.periodo_finale)
            if hasattr(self.us, 'fase_iniziale') and self.us.fase_iniziale:
                self.fase_iniziale.insert(0, self.us.fase_iniziale)
            if hasattr(self.us, 'fase_finale') and self.us.fase_finale:
                self.fase_finale.insert(0, self.us.fase_finale)
            
            # TODO: Load additional periodization data from service
            
        except Exception as e:
            print(f"Error loading periodization data: {e}")
    
    def save_periodization(self):
        """Save periodization data"""
        try:
            # Collect data
            period_data = {
                'sito': self.us.sito,
                'us': self.us.us,
                'periodo_iniziale': self.periodo_iniziale.get(),
                'periodo_finale': self.periodo_finale.get(),
                'fase_iniziale': self.fase_iniziale.get(),
                'fase_finale': self.fase_finale.get(),
                'metodo_datazione': self.dating_method.get(),
                'certezza_datazione': self.dating_certainty.get(),
                'data_iniziale': self.start_date.get(),
                'data_finale': self.end_date.get(),
                'descrizione_fase': self.phase_description.get("1.0", tk.END).strip(),
                'bibliografia': self.bibliography.get("1.0", tk.END).strip()
            }
            
            # TODO: Save using periodization service
            # self.periodizzazione_service.create_or_update_periodization(period_data)
            
            messagebox.showinfo("Successo", "Periodizzazione salvata con successo")
            
            if self.callback:
                self.callback()
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.window.destroy()


class ChronologicalSequenceDialog:
    """Dialog for displaying chronological sequence"""
    
    def __init__(self, parent, site_name, us_service, periodizzazione_service):
        self.parent = parent
        self.site_name = site_name
        self.us_service = us_service
        self.periodizzazione_service = periodizzazione_service
        
        # Create dialog
        self.window = tk.Toplevel(parent)
        self.window.title(f"Sequenza Cronologica - {site_name}")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
        self.load_chronological_data()
    
    def create_interface(self):
        """Create chronological sequence interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=f"Sequenza Cronologica", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"Sito: {self.site_name}", 
                 font=("Arial", 10)).pack(side=tk.RIGHT)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_timeline_tab()
        self.create_periods_tab()
        self.create_matrix_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Esporta", command=self.export_sequence).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Chiudi", command=self.close).pack(side=tk.RIGHT, padx=5)
    
    def create_timeline_tab(self):
        """Create timeline view tab"""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="Timeline")
        
        # Timeline tree
        self.timeline_tree = ttk.Treeview(timeline_frame, 
                                        columns=("US", "Periodo", "Fase", "Datazione", "Relazioni"), 
                                        show="headings")
        
        self.timeline_tree.heading("US", text="US")
        self.timeline_tree.heading("Periodo", text="Periodo")
        self.timeline_tree.heading("Fase", text="Fase")
        self.timeline_tree.heading("Datazione", text="Datazione")
        self.timeline_tree.heading("Relazioni", text="Relazioni Stratigrafiche")
        
        self.timeline_tree.column("US", width=80)
        self.timeline_tree.column("Periodo", width=150)
        self.timeline_tree.column("Fase", width=150)
        self.timeline_tree.column("Datazione", width=120)
        self.timeline_tree.column("Relazioni", width=200)
        
        # Scrollbar
        timeline_scrollbar = ttk.Scrollbar(timeline_frame, orient="vertical", command=self.timeline_tree.yview)
        self.timeline_tree.configure(yscrollcommand=timeline_scrollbar.set)
        
        self.timeline_tree.pack(side="left", fill="both", expand=True)
        timeline_scrollbar.pack(side="right", fill="y")
    
    def create_periods_tab(self):
        """Create periods summary tab"""
        periods_frame = ttk.Frame(self.notebook)
        self.notebook.add(periods_frame, text="Periodi")
        
        # Periods summary
        summary_frame = ttk.LabelFrame(periods_frame, text="Riepilogo Periodi", padding=10)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.periods_text = tk.Text(summary_frame, wrap=tk.WORD, height=20)
        periods_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=self.periods_text.yview)
        self.periods_text.configure(yscrollcommand=periods_scrollbar.set)
        
        self.periods_text.pack(side="left", fill="both", expand=True)
        periods_scrollbar.pack(side="right", fill="y")
    
    def create_matrix_tab(self):
        """Create stratigraphic matrix tab"""
        matrix_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrix_frame, text="Matrice")
        
        # Matrix info
        info_frame = ttk.LabelFrame(matrix_frame, text="Matrice Stratigrafica", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = tk.Text(info_frame, wrap=tk.WORD, height=15)
        matrix_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_text.yview)
        info_text.configure(yscrollcommand=matrix_scrollbar.set)
        
        info_text.pack(side="left", fill="both", expand=True)
        matrix_scrollbar.pack(side="right", fill="y")
        
        # Matrix generation button
        button_frame = ttk.Frame(matrix_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Genera Harris Matrix", 
                  command=self.generate_harris_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Visualizza Grafico", 
                  command=self.show_matrix_graph).pack(side=tk.LEFT, padx=5)
        
        self.matrix_text = info_text
    
    def load_chronological_data(self):
        """Load chronological data for the site"""
        try:
            # Get all US for the site
            us_filters = {'sito': self.site_name}
            us_list = self.us_service.get_all_us(size=1000, filters=us_filters)
            
            # Clear timeline
            for item in self.timeline_tree.get_children():
                self.timeline_tree.delete(item)
            
            # Populate timeline
            periods_summary = {}
            
            for us in us_list:
                # Extract chronological data
                periodo = f"{us.periodo_iniziale or ''} - {us.periodo_finale or ''}".strip(' -')
                fase = f"{us.fase_iniziale or ''} - {us.fase_finale or ''}".strip(' -')
                datazione = us.datazione or ""
                
                # Add to timeline
                self.timeline_tree.insert("", "end", values=(
                    f"US {us.us}",
                    periodo,
                    fase,
                    datazione,
                    "Anteriore/Posteriore"  # Placeholder for relationships
                ))
                
                # Count periods
                if us.periodo_iniziale:
                    periods_summary[us.periodo_iniziale] = periods_summary.get(us.periodo_iniziale, 0) + 1
            
            # Update periods summary
            self.update_periods_summary(periods_summary)
            
            # Update matrix info
            self.update_matrix_info(us_list)
            
        except Exception as e:
            print(f"Error loading chronological data: {e}")
            messagebox.showerror("Errore", f"Errore nel caricamento dei dati: {str(e)}")
    
    def update_periods_summary(self, periods_summary):
        """Update periods summary text"""
        self.periods_text.delete("1.0", tk.END)
        
        summary_text = f"RIEPILOGO CRONOLOGICO - SITO {self.site_name}\n"
        summary_text += "=" * 50 + "\n\n"
        
        if periods_summary:
            summary_text += "PERIODI RAPPRESENTATI:\n\n"
            for period, count in sorted(periods_summary.items()):
                summary_text += f"• {period}: {count} US\n"
        else:
            summary_text += "Nessuna periodizzazione inserita per questo sito.\n"
        
        summary_text += "\n" + "=" * 50 + "\n\n"
        summary_text += "SEQUENZA CRONOLOGICA:\n\n"
        summary_text += "La sequenza cronologica verrà generata automaticamente\n"
        summary_text += "basandosi sui dati stratigrafici e di periodizzazione\n"
        summary_text += "inseriti per ogni unità stratigrafica.\n\n"
        summary_text += "Per una sequenza più accurata, assicurarsi di aver inserito:\n"
        summary_text += "• Relazioni stratigrafiche tra le US\n"
        summary_text += "• Periodizzazioni dettagliate\n"
        summary_text += "• Datazioni assolute quando disponibili\n"
        
        self.periods_text.insert("1.0", summary_text)
    
    def update_matrix_info(self, us_list):
        """Update matrix information"""
        matrix_info = f"INFORMAZIONI MATRICE STRATIGRAFICA\n"
        matrix_info += "=" * 40 + "\n\n"
        matrix_info += f"Sito: {self.site_name}\n"
        matrix_info += f"Numero totale US: {len(us_list)}\n\n"
        
        if us_list:
            matrix_info += "US PRESENTI:\n"
            for us in sorted(us_list, key=lambda x: x.us):
                matrix_info += f"• US {us.us}"
                if us.d_stratigrafica:
                    matrix_info += f" - {us.d_stratigrafica[:50]}..."
                matrix_info += "\n"
        
        matrix_info += "\n" + "=" * 40 + "\n\n"
        matrix_info += "Per generare la Harris Matrix completa,\n"
        matrix_info += "utilizzare i pulsanti sottostanti.\n"
        
        self.matrix_text.delete("1.0", tk.END)
        self.matrix_text.insert("1.0", matrix_info)
    
    def generate_harris_matrix(self):
        """Generate Harris Matrix"""
        messagebox.showinfo("Harris Matrix", 
                           f"Generazione Harris Matrix per {self.site_name}\n\n"
                           "Questa funzionalità integrerà il generatore\n"
                           "di matrici stratigrafiche esistente.")
    
    def show_matrix_graph(self):
        """Show matrix as graph"""
        messagebox.showinfo("Grafico Matrix", 
                           f"Visualizzazione grafica della matrice\n"
                           "per il sito {self.site_name}\n\n"
                           "Integrazione con NetworkX e Matplotlib.")
    
    def export_sequence(self):
        """Export chronological sequence"""
        try:
            export_path = filedialog.asksaveasfilename(
                title="Esporta Sequenza Cronologica",
                defaultextension=".txt",
                filetypes=[
                    ("File di testo", "*.txt"),
                    ("File CSV", "*.csv"),
                    ("Tutti i file", "*.*")
                ]
            )
            
            if export_path:
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(f"SEQUENZA CRONOLOGICA - {self.site_name}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Export timeline data
                    for item in self.timeline_tree.get_children():
                        values = self.timeline_tree.item(item)['values']
                        f.write(f"{values[0]}: {values[1]} - {values[2]} ({values[3]})\n")
                
                messagebox.showinfo("Successo", f"Sequenza esportata in:\n{export_path}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'esportazione: {str(e)}")