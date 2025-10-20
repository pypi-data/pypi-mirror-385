#!/usr/bin/env python3
"""
Thesaurus Management Dialog for PyArchInit-Mini
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ThesaurusDialog:
    """
    Dialog for managing thesaurus and controlled vocabularies
    """
    
    def __init__(self, parent, thesaurus_service, callback=None):
        self.parent = parent
        self.thesaurus_service = thesaurus_service
        self.callback = callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestione Thesaurus")
        self.dialog.geometry("900x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_window()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create interface
        self.create_interface()
        
        # Load initial data
        self.load_tables()
    
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
        # Control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Table selection
        ttk.Label(control_frame, text="Tabella:").pack(side=tk.LEFT, padx=(0, 5))
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(control_frame, textvariable=self.table_var, 
                                       values=[], width=25, state="readonly")
        self.table_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_change)
        
        # Field selection
        ttk.Label(control_frame, text="Campo:").pack(side=tk.LEFT, padx=(10, 5))
        self.field_var = tk.StringVar()
        self.field_combo = ttk.Combobox(control_frame, textvariable=self.field_var,
                                       values=[], width=25, state="readonly")
        self.field_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.field_combo.bind('<<ComboboxSelected>>', self.on_field_change)
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Aggiungi Valore", command=self.add_value).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Modifica", command=self.edit_value).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Elimina", command=self.delete_value).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Inizializza Default", command=self.initialize_defaults).pack(side=tk.LEFT, padx=2)
        
        # Main content frame with panels
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Values list
        left_frame = ttk.LabelFrame(content_frame, text="Valori Vocabolario")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Values treeview
        columns = ('ID', 'Valore', 'Etichetta', 'Ordine')
        self.values_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.values_tree.heading('ID', text='ID')
        self.values_tree.heading('Valore', text='Valore')
        self.values_tree.heading('Etichetta', text='Etichetta')
        self.values_tree.heading('Ordine', text='Ordine')
        
        self.values_tree.column('ID', width=50, minwidth=50)
        self.values_tree.column('Valore', width=150, minwidth=100)
        self.values_tree.column('Etichetta', width=200, minwidth=150)
        self.values_tree.column('Ordine', width=80, minwidth=50)
        
        # Scrollbars for values tree
        values_scrollbar_y = ttk.Scrollbar(left_frame, orient="vertical", command=self.values_tree.yview)
        values_scrollbar_x = ttk.Scrollbar(left_frame, orient="horizontal", command=self.values_tree.xview)
        self.values_tree.configure(yscrollcommand=values_scrollbar_y.set, xscrollcommand=values_scrollbar_x.set)
        
        self.values_tree.pack(side="left", fill="both", expand=True)
        values_scrollbar_y.pack(side="right", fill="y")
        values_scrollbar_x.pack(side="bottom", fill="x")
        
        # Bind selection event
        self.values_tree.bind('<<TreeviewSelect>>', self.on_value_select)
        
        # Right panel - Value details
        right_frame = ttk.LabelFrame(content_frame, text="Dettagli Valore")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), ipadx=10)
        
        # Value details form
        self.create_details_form(right_frame)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(bottom_frame, text="Chiudi", command=self.close).pack(side=tk.RIGHT)
    
    def create_details_form(self, parent):
        """Create the details form for value editing"""
        # Value
        ttk.Label(parent, text="Valore:").pack(anchor="w", pady=(10, 2))
        self.value_entry = ttk.Entry(parent, width=30)
        self.value_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Label
        ttk.Label(parent, text="Etichetta:").pack(anchor="w", pady=(5, 2))
        self.label_entry = ttk.Entry(parent, width=30)
        self.label_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Description
        ttk.Label(parent, text="Descrizione:").pack(anchor="w", pady=(5, 2))
        self.description_text = tk.Text(parent, width=30, height=4)
        self.description_text.pack(fill=tk.X, pady=(0, 5))
        
        # Sort order
        ttk.Label(parent, text="Ordine:").pack(anchor="w", pady=(5, 2))
        self.order_entry = ttk.Entry(parent, width=30)
        self.order_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Active status
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Attivo", variable=self.active_var).pack(anchor="w", pady=(5, 5))
        
        # Save button
        ttk.Button(parent, text="Salva Modifiche", command=self.save_value_changes).pack(fill=tk.X, pady=(10, 5))
    
    def load_tables(self):
        """Load available tables"""
        try:
            # Standard archaeological tables
            tables = [
                'site_table',
                'us_table', 
                'inventario_materiali_table'
            ]
            
            self.table_combo['values'] = tables
            if tables:
                self.table_combo.set(tables[0])
                self.on_table_change()
                
        except Exception as e:
            logger.error(f"Error loading tables: {e}")
            messagebox.showerror("Errore", f"Errore nel caricamento delle tabelle: {str(e)}")
    
    def on_table_change(self, event=None):
        """Handle table selection change"""
        table_name = self.table_var.get()
        if not table_name:
            return
        
        try:
            # Get fields for the selected table
            fields = self.thesaurus_service.get_table_fields(table_name)
            
            self.field_combo['values'] = fields
            if fields:
                self.field_combo.set(fields[0])
                self.on_field_change()
            else:
                self.field_combo.set('')
                self.clear_values()
                
        except Exception as e:
            logger.error(f"Error loading fields for table {table_name}: {e}")
            messagebox.showerror("Errore", f"Errore nel caricamento dei campi: {str(e)}")
    
    def on_field_change(self, event=None):
        """Handle field selection change"""
        self.load_values()
    
    def load_values(self):
        """Load values for the selected table and field"""
        table_name = self.table_var.get()
        field_name = self.field_var.get()
        
        if not table_name or not field_name:
            self.clear_values()
            return
        
        try:
            # Clear existing items
            self.clear_values()
            
            # Get values from thesaurus service
            values = self.thesaurus_service.get_field_values(table_name, field_name)
            
            # Add values to tree
            for value in values:
                self.values_tree.insert('', 'end', values=(
                    value.get('id', ''),
                    value.get('value', ''),
                    value.get('label', ''),
                    value.get('sort_order', '')
                ))
                
        except Exception as e:
            logger.error(f"Error loading values: {e}")
            messagebox.showerror("Errore", f"Errore nel caricamento dei valori: {str(e)}")
    
    def clear_values(self):
        """Clear the values tree"""
        for item in self.values_tree.get_children():
            self.values_tree.delete(item)
        
        # Clear details form
        self.clear_details_form()
    
    def clear_details_form(self):
        """Clear the details form"""
        self.value_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)
        self.description_text.delete('1.0', tk.END)
        self.order_entry.delete(0, tk.END)
        self.active_var.set(True)
    
    def on_value_select(self, event):
        """Handle value selection"""
        selection = self.values_tree.selection()
        if not selection:
            self.clear_details_form()
            return
        
        item = selection[0]
        values = self.values_tree.item(item, 'values')
        
        if values:
            # Populate details form
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, values[1])  # Value
            
            self.label_entry.delete(0, tk.END)
            self.label_entry.insert(0, values[2])  # Label
            
            self.order_entry.delete(0, tk.END)
            self.order_entry.insert(0, values[3])  # Order
            
            # Note: Description and active status would need to be loaded from the service
            # For now, we'll clear these fields
            self.description_text.delete('1.0', tk.END)
            self.active_var.set(True)
    
    def add_value(self):
        """Add new value"""
        table_name = self.table_var.get()
        field_name = self.field_var.get()
        
        if not table_name or not field_name:
            messagebox.showwarning("Attenzione", "Seleziona una tabella e un campo")
            return
        
        # Get value from user
        value = simpledialog.askstring("Nuovo Valore", "Inserisci il nuovo valore:")
        if not value:
            return
        
        # Get optional label
        label = simpledialog.askstring("Etichetta", f"Etichetta per '{value}' (opzionale):")
        
        try:
            # Add value through service
            result = self.thesaurus_service.add_field_value(
                table_name=table_name,
                field_name=field_name,
                value=value,
                label=label
            )
            
            # Refresh values list
            self.load_values()
            
            messagebox.showinfo("Successo", f"Valore '{value}' aggiunto con successo")
            
        except Exception as e:
            logger.error(f"Error adding value: {e}")
            messagebox.showerror("Errore", f"Errore nell'aggiunta del valore: {str(e)}")
    
    def edit_value(self):
        """Edit selected value"""
        selection = self.values_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un valore da modificare")
            return
        
        item = selection[0]
        values = self.values_tree.item(item, 'values')
        
        if not values or not values[0]:  # No ID
            messagebox.showwarning("Attenzione", "Impossibile modificare questo valore")
            return
        
        value_id = values[0]
        current_value = values[1]
        current_label = values[2]
        
        # Get new value from user
        new_value = simpledialog.askstring("Modifica Valore", 
                                          "Modifica il valore:", 
                                          initialvalue=current_value)
        if new_value is None:  # User cancelled
            return
        
        # Get new label
        new_label = simpledialog.askstring("Modifica Etichetta", 
                                          "Modifica l'etichetta:", 
                                          initialvalue=current_label)
        
        try:
            # Update value through service
            result = self.thesaurus_service.update_field_value(
                field_id=int(value_id),
                value=new_value if new_value != current_value else None,
                label=new_label if new_label != current_label else None
            )
            
            # Refresh values list
            self.load_values()
            
            messagebox.showinfo("Successo", "Valore aggiornato con successo")
            
        except Exception as e:
            logger.error(f"Error updating value: {e}")
            messagebox.showerror("Errore", f"Errore nell'aggiornamento del valore: {str(e)}")
    
    def delete_value(self):
        """Delete selected value"""
        selection = self.values_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un valore da eliminare")
            return
        
        item = selection[0]
        values = self.values_tree.item(item, 'values')
        
        if not values or not values[0]:  # No ID
            messagebox.showwarning("Attenzione", "Impossibile eliminare questo valore")
            return
        
        value_id = values[0]
        value_text = values[1]
        
        # Confirm deletion
        if not messagebox.askyesno("Conferma", f"Eliminare il valore '{value_text}'?"):
            return
        
        try:
            # Delete value through service
            success = self.thesaurus_service.delete_field_value(int(value_id))
            
            if success:
                # Refresh values list
                self.load_values()
                messagebox.showinfo("Successo", "Valore eliminato con successo")
            else:
                messagebox.showerror("Errore", "Errore nell'eliminazione del valore")
                
        except Exception as e:
            logger.error(f"Error deleting value: {e}")
            messagebox.showerror("Errore", f"Errore nell'eliminazione del valore: {str(e)}")
    
    def save_value_changes(self):
        """Save changes to the selected value"""
        selection = self.values_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un valore da modificare")
            return
        
        item = selection[0]
        values = self.values_tree.item(item, 'values')
        
        if not values or not values[0]:  # No ID
            messagebox.showwarning("Attenzione", "Impossibile modificare questo valore")
            return
        
        value_id = values[0]
        
        # Get values from form
        new_value = self.value_entry.get().strip()
        new_label = self.label_entry.get().strip()
        new_description = self.description_text.get('1.0', tk.END).strip()
        
        if not new_value:
            messagebox.showerror("Errore", "Il valore non può essere vuoto")
            return
        
        try:
            # Update value through service
            result = self.thesaurus_service.update_field_value(
                field_id=int(value_id),
                value=new_value,
                label=new_label if new_label else None,
                description=new_description if new_description else None
            )
            
            # Refresh values list
            self.load_values()
            
            messagebox.showinfo("Successo", "Valore aggiornato con successo")
            
        except Exception as e:
            logger.error(f"Error updating value: {e}")
            messagebox.showerror("Errore", f"Errore nell'aggiornamento del valore: {str(e)}")
    
    def initialize_defaults(self):
        """Initialize default vocabularies"""
        if not messagebox.askyesno("Conferma", 
                                  "Inizializzare i vocabolari predefiniti? "
                                  "Questo aggiungerà i valori standard per i campi archeologici."):
            return
        
        try:
            success = self.thesaurus_service.initialize_default_vocabularies()
            
            if success:
                # Refresh current view
                self.load_values()
                messagebox.showinfo("Successo", "Vocabolari predefiniti inizializzati con successo")
            else:
                messagebox.showerror("Errore", "Errore nell'inizializzazione dei vocabolari")
                
        except Exception as e:
            logger.error(f"Error initializing vocabularies: {e}")
            messagebox.showerror("Errore", f"Errore nell'inizializzazione: {str(e)}")
    
    def close(self):
        """Close dialog"""
        if self.callback:
            self.callback()
        self.dialog.destroy()