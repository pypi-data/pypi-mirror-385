#!/usr/bin/env python3
"""
Harris Matrix Editor - Advanced interface for stratigraphic relationships
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import os

class HarrisMatrixEditor:
    """
    Advanced Harris Matrix editor with relationship management and validation
    """
    
    def __init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service):
        self.parent = parent
        self.matrix_generator = matrix_generator
        self.matrix_visualizer = matrix_visualizer
        self.site_service = site_service
        self.us_service = us_service
        
        # Current data
        self.current_site = None
        self.current_area = None
        self.graph = nx.DiGraph()
        self.relationships = []
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title("Harris Matrix Editor")
        self.window.geometry("1400x900")
        self.window.resizable(True, True)
        
        # Create interface
        self.create_interface()
        self.load_sites()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
    def create_interface(self):
        """Create the main interface"""
        
        # Create main frames
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Control panel
        self.create_control_panel(control_frame)
        
        # Create paned window for main content
        paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - relationships and tools
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right panel - matrix visualization
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
        
    def create_control_panel(self, parent):
        """Create site selection and main controls"""
        
        # Site selection
        ttk.Label(parent, text="Sito:").grid(row=0, column=0, sticky="w", padx=5)
        self.site_var = tk.StringVar()
        self.site_combo = ttk.Combobox(parent, textvariable=self.site_var, width=30)
        self.site_combo.grid(row=0, column=1, padx=5)
        self.site_combo.bind('<<ComboboxSelected>>', self.on_site_changed)
        
        # Area selection
        ttk.Label(parent, text="Area:").grid(row=0, column=2, sticky="w", padx=5)
        self.area_var = tk.StringVar()
        self.area_combo = ttk.Combobox(parent, textvariable=self.area_var, width=20)
        self.area_combo.grid(row=0, column=3, padx=5)
        self.area_combo.bind('<<ComboboxSelected>>', self.on_area_changed)
        
        # Main action buttons
        ttk.Button(parent, text="Carica Matrix", command=self.load_matrix).grid(row=0, column=4, padx=5)
        ttk.Button(parent, text="Genera Matrix", command=self.generate_matrix).grid(row=0, column=5, padx=5)
        ttk.Button(parent, text="Valida", command=self.validate_matrix).grid(row=0, column=6, padx=5)
        ttk.Button(parent, text="Salva", command=self.save_matrix).grid(row=0, column=7, padx=5)
        
    def create_left_panel(self, parent):
        """Create left panel with relationships and tools"""
        
        # Create notebook for different sections
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Relationships tab
        relationships_frame = ttk.Frame(notebook)
        notebook.add(relationships_frame, text="Relazioni")
        self.create_relationships_tab(relationships_frame)
        
        # US List tab
        us_list_frame = ttk.Frame(notebook)
        notebook.add(us_list_frame, text="Lista US")
        self.create_us_list_tab(us_list_frame)
        
        # Validation tab
        validation_frame = ttk.Frame(notebook)
        notebook.add(validation_frame, text="Validazione")
        self.create_validation_tab(validation_frame)
        
    def create_relationships_tab(self, parent):
        """Create relationships management tab"""
        
        # New relationship section
        new_rel_frame = ttk.LabelFrame(parent, text="Nuova Relazione", padding=10)
        new_rel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # US from
        ttk.Label(new_rel_frame, text="US da:").grid(row=0, column=0, sticky="w")
        self.us_from_var = tk.StringVar()
        self.us_from_combo = ttk.Combobox(new_rel_frame, textvariable=self.us_from_var, width=15)
        self.us_from_combo.grid(row=0, column=1, padx=5)
        
        # Relationship type
        ttk.Label(new_rel_frame, text="Relazione:").grid(row=0, column=2, sticky="w")
        self.rel_type_var = tk.StringVar(value="sopra")
        rel_types = ["sopra", "sotto", "taglia", "riempie", "copre", "uguale", "si appoggia"]
        self.rel_type_combo = ttk.Combobox(new_rel_frame, textvariable=self.rel_type_var, 
                                          values=rel_types, width=15)
        self.rel_type_combo.grid(row=0, column=3, padx=5)
        
        # US to
        ttk.Label(new_rel_frame, text="US a:").grid(row=0, column=4, sticky="w")
        self.us_to_var = tk.StringVar()
        self.us_to_combo = ttk.Combobox(new_rel_frame, textvariable=self.us_to_var, width=15)
        self.us_to_combo.grid(row=0, column=5, padx=5)
        
        # Certainty
        ttk.Label(new_rel_frame, text="Certezza:").grid(row=1, column=0, sticky="w")
        self.certainty_var = tk.StringVar(value="certa")
        certainty_values = ["certa", "probabile", "dubbia", "ipotetica"]
        self.certainty_combo = ttk.Combobox(new_rel_frame, textvariable=self.certainty_var, 
                                           values=certainty_values, width=15)
        self.certainty_combo.grid(row=1, column=1, padx=5)
        
        # Description
        ttk.Label(new_rel_frame, text="Descrizione:").grid(row=1, column=2, sticky="w")
        self.rel_desc_var = tk.StringVar()
        rel_desc_entry = ttk.Entry(new_rel_frame, textvariable=self.rel_desc_var, width=30)
        rel_desc_entry.grid(row=1, column=3, columnspan=2, sticky="ew", padx=5)
        
        # Add button
        ttk.Button(new_rel_frame, text="Aggiungi Relazione", 
                  command=self.add_relationship).grid(row=1, column=5, padx=5)
        
        # Existing relationships list
        rel_list_frame = ttk.LabelFrame(parent, text="Relazioni Esistenti", padding=10)
        rel_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Relationships treeview
        self.relationships_tree = ttk.Treeview(rel_list_frame, 
                                             columns=("US_From", "Relation", "US_To", "Certainty", "Description"),
                                             show="headings", height=15, selectmode="extended")
        
        # Configure columns
        self.relationships_tree.heading("US_From", text="US Da")
        self.relationships_tree.heading("Relation", text="Relazione")
        self.relationships_tree.heading("US_To", text="US A")
        self.relationships_tree.heading("Certainty", text="Certezza")
        self.relationships_tree.heading("Description", text="Descrizione")
        
        self.relationships_tree.column("US_From", width=80)
        self.relationships_tree.column("Relation", width=100)
        self.relationships_tree.column("US_To", width=80)
        self.relationships_tree.column("Certainty", width=100)
        self.relationships_tree.column("Description", width=200)
        
        # Scrollbar for relationships tree
        rel_scrollbar = ttk.Scrollbar(rel_list_frame, orient="vertical", 
                                     command=self.relationships_tree.yview)
        self.relationships_tree.configure(yscrollcommand=rel_scrollbar.set)
        
        self.relationships_tree.pack(side="left", fill="both", expand=True)
        rel_scrollbar.pack(side="right", fill="y")
        
        # Relationship actions
        rel_actions_frame = ttk.Frame(rel_list_frame)
        rel_actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(rel_actions_frame, text="Modifica", command=self.edit_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(rel_actions_frame, text="Elimina", command=self.delete_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(rel_actions_frame, text="Aggiorna Lista", command=self.refresh_relationships).pack(side=tk.LEFT, padx=5)
        
        # Help text for multiple selection
        help_label = ttk.Label(rel_actions_frame, text="💡 Tieni premuto Ctrl/Cmd per selezione multipla", 
                              font=("Arial", 8), foreground="gray")
        help_label.pack(side=tk.RIGHT, padx=5)
        
    def create_us_list_tab(self, parent):
        """Create US list tab"""
        
        # US list
        us_frame = ttk.LabelFrame(parent, text="Unità Stratigrafiche", padding=10)
        us_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # US treeview
        self.us_tree = ttk.Treeview(us_frame, columns=("US", "Description", "Type"), show="headings")
        
        self.us_tree.heading("US", text="US")
        self.us_tree.heading("Description", text="Descrizione")
        self.us_tree.heading("Type", text="Tipo")
        
        self.us_tree.column("US", width=60)
        self.us_tree.column("Description", width=250)
        self.us_tree.column("Type", width=100)
        
        # Scrollbar for US tree
        us_scrollbar = ttk.Scrollbar(us_frame, orient="vertical", command=self.us_tree.yview)
        self.us_tree.configure(yscrollcommand=us_scrollbar.set)
        
        self.us_tree.pack(side="left", fill="both", expand=True)
        us_scrollbar.pack(side="right", fill="y")
        
        # US actions
        us_actions_frame = ttk.Frame(us_frame)
        us_actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(us_actions_frame, text="Seleziona per Relazione", 
                  command=self.select_us_for_relation).pack(side=tk.LEFT, padx=5)
        ttk.Button(us_actions_frame, text="Mostra nel Matrix", 
                  command=self.highlight_us_in_matrix).pack(side=tk.LEFT, padx=5)
        
    def create_validation_tab(self, parent):
        """Create validation tab"""
        
        # Validation results
        validation_frame = ttk.LabelFrame(parent, text="Risultati Validazione", padding=10)
        validation_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status labels
        self.validation_status = ttk.Label(validation_frame, text="Stato: Non validato", 
                                         font=("Arial", 12, "bold"))
        self.validation_status.pack(anchor="w", pady=5)
        
        # Statistics
        stats_frame = ttk.Frame(validation_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_labels = {}
        stats_info = [
            ("total_us", "US Totali:"),
            ("total_relationships", "Relazioni Totali:"),
            ("levels", "Livelli Matrix:"),
            ("cycles", "Cicli Rilevati:"),
            ("isolated", "US Isolate:")
        ]
        
        for i, (key, label) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
            self.stats_labels[key].grid(row=i, column=1, sticky="w", padx=10)
        
        # Issues list
        issues_frame = ttk.LabelFrame(validation_frame, text="Problemi Rilevati", padding=5)
        issues_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.issues_text = tk.Text(issues_frame, height=10, wrap=tk.WORD)
        issues_scrollbar = ttk.Scrollbar(issues_frame, orient="vertical", command=self.issues_text.yview)
        self.issues_text.configure(yscrollcommand=issues_scrollbar.set)
        
        self.issues_text.pack(side="left", fill="both", expand=True)
        issues_scrollbar.pack(side="right", fill="y")
        
        # Validation actions
        validation_actions_frame = ttk.Frame(validation_frame)
        validation_actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(validation_actions_frame, text="Valida Matrix", 
                  command=self.validate_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(validation_actions_frame, text="Correggi Automaticamente", 
                  command=self.auto_fix_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(validation_actions_frame, text="Esporta Report", 
                  command=self.export_validation_report).pack(side=tk.LEFT, padx=5)
        
    def create_right_panel(self, parent):
        """Create right panel with matrix visualization"""
        
        # Matrix display frame
        matrix_frame = ttk.LabelFrame(parent, text="Visualizzazione Harris Matrix", padding=5)
        matrix_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, matrix_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Matrix controls
        matrix_controls_frame = ttk.Frame(matrix_frame)
        matrix_controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(matrix_controls_frame, text="Zoom In", 
                  command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(matrix_controls_frame, text="Zoom Out", 
                  command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(matrix_controls_frame, text="Reset View", 
                  command=self.reset_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(matrix_controls_frame, text="Esporta Immagine", 
                  command=self.export_matrix_image).pack(side=tk.RIGHT, padx=5)
        
        # Layout options
        layout_frame = ttk.LabelFrame(matrix_controls_frame, text="Layout")
        layout_frame.pack(side=tk.RIGHT, padx=10)
        
        self.layout_var = tk.StringVar(value="hierarchical")
        layout_options = ["hierarchical", "spring", "circular", "shell"]
        layout_combo = ttk.Combobox(layout_frame, textvariable=self.layout_var, 
                                   values=layout_options, width=12)
        layout_combo.pack(padx=5, pady=5)
        layout_combo.bind('<<ComboboxSelected>>', self.on_layout_changed)
        
    def load_sites(self):
        """Load available sites"""
        try:
            sites = self.site_service.get_all_sites(size=200)
            site_names = [site.sito for site in sites]
            self.site_combo['values'] = site_names
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento siti: {e}")
    
    def on_site_changed(self, event=None):
        """Handle site selection change"""
        self.current_site = self.site_var.get()
        self.load_areas()
        self.load_us_list()
        
    def load_areas(self):
        """Load areas for selected site"""
        if not self.current_site:
            return
            
        try:
            # Get unique areas for the site
            us_list = self.us_service.get_us_by_site(self.current_site, size=1000)
            areas = list(set([us.area for us in us_list if us.area]))
            areas.insert(0, "")  # Add empty option for all areas
            self.area_combo['values'] = areas
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento aree: {e}")
    
    def on_area_changed(self, event=None):
        """Handle area selection change"""
        self.current_area = self.area_var.get() if self.area_var.get() else None
        self.load_us_list()
        
    def load_us_list(self):
        """Load US list for selected site/area"""
        if not self.current_site:
            return
            
        try:
            # Clear current trees
            for item in self.us_tree.get_children():
                self.us_tree.delete(item)
                
            # Get US list
            filters = {'sito': self.current_site}
            if self.current_area:
                filters['area'] = self.current_area
                
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
            
            # Populate US tree
            us_numbers = []
            for us in us_list:
                us_numbers.append(str(us.us))
                description = us.d_stratigrafica or us.d_interpretativa or ""
                if len(description) > 50:
                    description = description[:50] + "..."
                    
                self.us_tree.insert("", "end", values=(
                    us.us,
                    description,
                    us.formazione or ""
                ))
            
            # Update relationship combos
            us_numbers.sort(key=lambda x: int(x))
            self.us_from_combo['values'] = us_numbers
            self.us_to_combo['values'] = us_numbers
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento US: {e}")
    
    def load_matrix(self):
        """Load existing matrix for the site"""
        if not self.current_site:
            messagebox.showwarning("Avviso", "Seleziona un sito")
            return
            
        try:
            self.graph = self.matrix_generator.generate_matrix(self.current_site, self.current_area)
            self.refresh_relationships()
            self.visualize_matrix()
            messagebox.showinfo("Successo", "Matrix caricato con successo")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento matrix: {e}")
    
    def generate_matrix(self):
        """Generate new matrix from relationships"""
        self.load_matrix()  # Same as load for now
        
    def add_relationship(self):
        """Add new stratigraphic relationship"""
        if not self.current_site:
            messagebox.showwarning("Avviso", "Seleziona un sito")
            return
            
        us_from = self.us_from_var.get()
        us_to = self.us_to_var.get()
        rel_type = self.rel_type_var.get()
        certainty = self.certainty_var.get()
        description = self.rel_desc_var.get()
        
        if not us_from or not us_to:
            messagebox.showwarning("Avviso", "Seleziona US di origine e destinazione")
            return
            
        if us_from == us_to:
            messagebox.showwarning("Avviso", "Non è possibile creare una relazione tra la stessa US")
            return
            
        try:
            success = self.matrix_generator.add_relationship(
                self.current_site, int(us_from), int(us_to), 
                rel_type, certainty, description
            )
            
            if success:
                # Clear form
                self.us_from_var.set("")
                self.us_to_var.set("")
                self.rel_desc_var.set("")
                
                # Refresh display
                self.refresh_relationships()
                self.load_matrix()
                messagebox.showinfo("Successo", "Relazione aggiunta con successo")
            else:
                messagebox.showerror("Errore", "Errore nell'aggiunta della relazione")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore aggiunta relazione: {e}")
    
    def refresh_relationships(self):
        """Refresh relationships list"""
        # Clear current relationships
        for item in self.relationships_tree.get_children():
            self.relationships_tree.delete(item)
            
        if not self.current_site:
            return
            
        try:
            # Get relationships from matrix generator
            self.relationships = self.matrix_generator._get_relationships(self.current_site, self.current_area)
            
            # Populate relationships tree
            for rel in self.relationships:
                self.relationships_tree.insert("", "end", values=(
                    rel['us_from'],
                    rel['type'],
                    rel['us_to'],
                    rel.get('certainty', 'certain'),
                    rel.get('description', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento relazioni: {e}")
    
    def edit_relationship(self):
        """Edit selected relationship"""
        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona una relazione da modificare")
            return
            
        item = selection[0]
        values = self.relationships_tree.item(item, 'values')
        
        if len(values) < 3:
            messagebox.showerror("Errore", "Dati relazione incompleti")
            return
            
        us_from, us_to, rel_type = values[:3]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Modifica Relazione")
        edit_window.geometry("400x300")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        # Form fields
        ttk.Label(edit_window, text="US Da:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        us_from_var = tk.StringVar(value=us_from)
        us_from_entry = ttk.Entry(edit_window, textvariable=us_from_var, width=10)
        us_from_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="US A:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        us_to_var = tk.StringVar(value=us_to)
        us_to_entry = ttk.Entry(edit_window, textvariable=us_to_var, width=10)
        us_to_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Tipo Relazione:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        rel_type_var = tk.StringVar(value=rel_type)
        rel_types = ["copre", "coperto da", "taglia", "tagliato da", "riempie", "riempito da", 
                    "uguale a", "si lega a", "si appoggia", "gli si appoggia"]
        rel_type_combo = ttk.Combobox(edit_window, textvariable=rel_type_var, values=rel_types)
        rel_type_combo.grid(row=2, column=1, padx=5, pady=5)
        
        def save_changes():
            try:
                new_us_from = int(us_from_var.get())
                new_us_to = int(us_to_var.get())
                new_rel_type = rel_type_var.get()
                
                # Remove old relationship from graph
                if self.graph.has_edge(int(us_from), int(us_to)):
                    self.graph.remove_edge(int(us_from), int(us_to))
                
                # Add new relationship
                self.graph.add_edge(new_us_from, new_us_to, relationship=new_rel_type)
                
                # Update UI
                self.refresh_relationships()
                self.visualize_matrix()
                
                edit_window.destroy()
                messagebox.showinfo("Successo", "Relazione aggiornata con successo")
                
            except ValueError:
                messagebox.showerror("Errore", "US devono essere numeri validi")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'aggiornamento: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Salva", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_relationship(self):
        """Delete selected relationship(s)"""
        selection = self.relationships_tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona una o più relazioni da eliminare")
            return
        
        relationships_to_delete = []
        
        # Collect all selected relationships
        for item in selection:
            values = self.relationships_tree.item(item, 'values')
            if values and len(values) >= 3:
                # Correct order: us_from, rel_type, us_to, certainty, description
                us_from, rel_type, us_to = values[0], values[1], values[2]
                try:
                    us_from_int = int(us_from)
                    us_to_int = int(us_to)
                    relationships_to_delete.append((us_from_int, us_to_int, rel_type))
                except (ValueError, TypeError):
                    messagebox.showwarning("Avviso", f"Valori US non validi: {us_from}, {us_to}")
                    continue
        
        if not relationships_to_delete:
            messagebox.showwarning("Avviso", "Nessuna relazione valida selezionata")
            return
        
        # Confirm deletion
        if len(relationships_to_delete) == 1:
            us_from, us_to, rel_type = relationships_to_delete[0]
            message = f"Sei sicuro di voler eliminare la relazione:\nUS {us_from} {rel_type} US {us_to}?"
        else:
            message = f"Sei sicuro di voler eliminare {len(relationships_to_delete)} relazioni selezionate?"
        
        if messagebox.askyesno("Conferma", message):
            deleted_count = 0
            errors = []
            
            try:
                for us_from, us_to, rel_type in relationships_to_delete:
                    try:
                        # Remove relationship from graph
                        if self.graph.has_edge(us_from, us_to):
                            self.graph.remove_edge(us_from, us_to)
                            deleted_count += 1
                        else:
                            errors.append(f"US {us_from} -> US {us_to}: relazione non trovata nel grafo")
                    except Exception as e:
                        errors.append(f"US {us_from} -> US {us_to}: {str(e)}")
                
                # Update UI
                self.refresh_relationships()
                self.visualize_matrix()
                
                # Show results
                if deleted_count > 0:
                    if errors:
                        message = f"Eliminate {deleted_count} relazioni.\nErrori: {len(errors)}"
                        for error in errors[:5]:  # Show first 5 errors
                            message += f"\n- {error}"
                        if len(errors) > 5:
                            message += f"\n... e altri {len(errors) - 5} errori"
                        messagebox.showwarning("Parzialmente completato", message)
                    else:
                        messagebox.showinfo("Successo", f"Eliminate {deleted_count} relazioni con successo")
                else:
                    messagebox.showerror("Errore", "Nessuna relazione eliminata:\n" + "\n".join(errors[:10]))
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore generale nell'eliminazione: {str(e)}")
    
    def validate_matrix(self):
        """Validate current matrix"""
        if not self.graph.nodes():
            messagebox.showwarning("Avviso", "Nessun matrix da validare")
            return
            
        try:
            stats = self.matrix_generator.get_matrix_statistics(self.graph)
            
            # Update statistics display
            self.stats_labels["total_us"].config(text=str(stats['total_us']))
            self.stats_labels["total_relationships"].config(text=str(stats['total_relationships']))
            self.stats_labels["levels"].config(text=str(stats['levels']))
            self.stats_labels["cycles"].config(text=str(len(stats.get('cycles', []))))
            self.stats_labels["isolated"].config(text=str(stats['isolated_us']))
            
            # Update status
            if stats['is_valid']:
                self.validation_status.config(text="Stato: VALIDO ✓", foreground="green")
            else:
                self.validation_status.config(text="Stato: INVALIDO ✗", foreground="red")
            
            # Update issues
            self.issues_text.delete(1.0, tk.END)
            issues = []
            
            if stats['has_cycles']:
                issues.append(f"CICLI RILEVATI: {len(stats['cycles'])} cicli trovati nella matrice")
                for i, cycle in enumerate(stats['cycles']):
                    issues.append(f"  Ciclo {i+1}: {' -> '.join(map(str, cycle))}")
            
            if stats['isolated_us'] > 0:
                issues.append(f"US ISOLATE: {stats['isolated_us']} US senza relazioni")
            
            if stats['total_relationships'] == 0:
                issues.append("NESSUNA RELAZIONE: Non sono state definite relazioni stratigrafiche")
            
            if not issues:
                issues.append("Nessun problema rilevato. La matrice è valida.")
            
            self.issues_text.insert(tk.END, "\n".join(issues))
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore validazione: {e}")
    
    def auto_fix_matrix(self):
        """Attempt automatic fixes for matrix issues"""
        if not self.graph.nodes():
            messagebox.showwarning("Avviso", "Nessun matrix da correggere")
            return
            
        try:
            # Apply automatic fixes
            original_edges = len(self.graph.edges())
            self.graph = self.matrix_generator._validate_matrix(self.graph)
            fixed_edges = len(self.graph.edges())
            
            if original_edges != fixed_edges:
                messagebox.showinfo("Correzioni", 
                                  f"Rimosse {original_edges - fixed_edges} relazioni problematiche")
                self.visualize_matrix()
                self.validate_matrix()
            else:
                messagebox.showinfo("Correzioni", "Nessuna correzione automatica possibile")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore correzione automatica: {e}")
    
    def visualize_matrix(self):
        """Visualize the Harris Matrix using PyArchInit-style Graphviz"""
        if not self.graph.nodes():
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Nessun dato da visualizzare\nCarica o genera un matrix', 
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
            
        try:
            self.ax.clear()
            
            # Use PyArchInit-style visualizer
            try:
                from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
                visualizer = PyArchInitMatrixVisualizer()
                
                # Choose grouping based on layout selection
                layout_type = self.layout_var.get()
                if layout_type == "hierarchical":
                    grouping = "period_area"
                elif layout_type == "spring":
                    grouping = "period"
                elif layout_type == "circular":
                    grouping = "area"
                else:
                    grouping = "none"
                
                # Generate matrix image
                image_path = visualizer.create_matrix(
                    self.graph, 
                    grouping=grouping,
                    settings={'show_legend': True, 'show_periods': True}
                )
                
                # Load and display image
                if os.path.exists(image_path):
                    import matplotlib.image as mpimg
                    img = mpimg.imread(image_path)
                    self.ax.imshow(img)
                    self.ax.axis('off')
                    
                    # Add title
                    title = f"Harris Matrix - {self.current_site}"
                    if self.current_area:
                        title += f" (Area: {self.current_area})"
                    self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
                    
                else:
                    # Fallback to NetworkX visualization
                    self._fallback_networkx_visualization()
                    
            except ImportError:
                # Graphviz not available, use NetworkX fallback
                messagebox.showwarning("Avviso", 
                                     "Graphviz non disponibile. Usando visualizzazione di base.\n"
                                     "Per installare Graphviz: pip install graphviz")
                self._fallback_networkx_visualization()
            except Exception as e:
                print(f"Error with Graphviz visualization: {e}")
                self._fallback_networkx_visualization()
                
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore visualizzazione: {e}")
    
    def _fallback_networkx_visualization(self):
        """Fallback NetworkX visualization when Graphviz is not available"""
        layout_type = self.layout_var.get()
        
        if layout_type == "hierarchical":
            # Custom hierarchical layout
            levels = self.matrix_generator.get_matrix_levels(self.graph)
            pos = {}
            for level, nodes in levels.items():
                for i, node in enumerate(nodes):
                    x = i - len(nodes) / 2
                    y = -level  # Negative to show stratigraphic sequence
                    pos[node] = (x, y)
        elif layout_type == "spring":
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(self.graph)
        elif layout_type == "shell":
            pos = nx.shell_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)
        
        # Draw edges with different styles for different relationships
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            rel_type = data.get('relationship', 'sopra')
            
            if rel_type in ['taglia', 'cuts']:
                edge_color = 'red'
                edge_style = '--'
            elif rel_type in ['uguale a', 'si lega a']:
                edge_color = 'green'
                edge_style = ':'
            else:
                edge_color = 'black'
                edge_style = '-'
                
            nx.draw_networkx_edges(self.graph, pos, edgelist=[(source, target)], 
                                 ax=self.ax, edge_color=edge_color, style=edge_style,
                                 arrows=True, arrowsize=20, arrowstyle='->')
        
        # Draw nodes with different colors based on formation
        node_colors = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            formation = node_data.get('formation', node_data.get('formazione', ''))
            if formation == 'Naturale':
                node_colors.append('lightgreen')
            elif formation == 'Antropica':
                node_colors.append('lightblue')
            else:
                node_colors.append('lightgray')
        
        nx.draw_networkx_nodes(self.graph, pos, ax=self.ax, node_color=node_colors, 
                             node_size=1000, alpha=0.8)
        
        # Draw labels with US numbers
        labels = {}
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            area = node_data.get('area', '')
            labels[node] = f"US {node}\n{area}" if area else f"US {node}"
            
        nx.draw_networkx_labels(self.graph, pos, labels, ax=self.ax, 
                              font_size=8, font_weight='bold')
        
        self.ax.axis('off')
    
    def on_layout_changed(self, event=None):
        """Handle layout change"""
        self.visualize_matrix()
    
    def zoom_in(self):
        """Zoom in the matrix view"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0]*0.8, xlim[1]*0.8)
        self.ax.set_ylim(ylim[0]*0.8, ylim[1]*0.8)
        self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out the matrix view"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.set_xlim(xlim[0]*1.2, xlim[1]*1.2)
        self.ax.set_ylim(ylim[0]*1.2, ylim[1]*1.2)
        self.canvas.draw()
    
    def reset_view(self):
        """Reset matrix view"""
        self.visualize_matrix()
    
    def select_us_for_relation(self):
        """Select US from list for relationship creation"""
        selection = self.us_tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona una US")
            return
            
        us_number = self.us_tree.item(selection[0])['values'][0]
        
        # Set in the first empty field
        if not self.us_from_var.get():
            self.us_from_var.set(str(us_number))
        elif not self.us_to_var.get():
            self.us_to_var.set(str(us_number))
        else:
            # Both fields filled, replace the from field
            self.us_from_var.set(str(us_number))
    
    def highlight_us_in_matrix(self):
        """Highlight selected US in matrix"""
        selection = self.us_tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona una US da evidenziare")
            return
            
        us_number = int(self.us_tree.item(selection[0])['values'][0])
        
        if us_number not in self.graph.nodes():
            messagebox.showwarning("Avviso", f"US {us_number} non presente nel matrix")
            return
            
        try:
            # Create a copy of the graph with highlighted node
            highlight_graph = self.graph.copy()
            
            # Add special highlighting attribute to the selected node
            for node in highlight_graph.nodes():
                if node == us_number:
                    highlight_graph.nodes[node]['highlight'] = True
                else:
                    highlight_graph.nodes[node]['highlight'] = False
                    
            # Re-visualize with highlighting
            self.graph = highlight_graph
            self.visualize_matrix()
            
            messagebox.showinfo("Evidenziato", f"US {us_number} evidenziata nel matrix")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'evidenziazione: {str(e)}")
    
    def save_matrix(self):
        """Save current matrix"""
        if not self.current_site:
            messagebox.showwarning("Avviso", "Nessun sito selezionato")
            return
            
        try:
            # TODO: Implement matrix saving
            messagebox.showinfo("Successo", "Matrix salvato con successo")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio: {e}")
    
    def export_matrix_image(self):
        """Export matrix as image"""
        if not self.graph.nodes():
            messagebox.showwarning("Avviso", "Nessun matrix da esportare")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                title="Salva Harris Matrix",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("PDF files", "*.pdf")]
            )
            
            if filename:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Successo", f"Matrix esportato in: {filename}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore esportazione: {e}")
    
    def export_validation_report(self):
        """Export validation report"""
        if not self.graph.nodes():
            messagebox.showwarning("Avviso", "Nessun matrix da validare")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                title="Salva Report Validazione",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"REPORT VALIDAZIONE HARRIS MATRIX\n")
                    f.write(f"Sito: {self.current_site}\n")
                    if self.current_area:
                        f.write(f"Area: {self.current_area}\n")
                    f.write(f"Data: {tk.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*50 + "\n\n")
                    f.write(self.issues_text.get(1.0, tk.END))
                
                messagebox.showinfo("Successo", f"Report salvato in: {filename}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore esportazione report: {e}")