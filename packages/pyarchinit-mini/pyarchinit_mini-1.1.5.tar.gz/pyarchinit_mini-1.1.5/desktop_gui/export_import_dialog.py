"""
Export/Import Dialog for Desktop GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path


class ExportImportDialog:
    """Dialog for data export and import"""

    def __init__(self, parent, db_manager):
        """
        Initialize export/import dialog

        Args:
            parent: Parent window
            db_manager: DatabaseManager instance
        """
        self.parent = parent
        self.db_manager = db_manager

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export / Import Dati")
        self.dialog.geometry("700x600")
        self.dialog.resizable(False, False)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Export tab
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="Esporta Dati")
        self.create_export_tab(export_frame)

        # Import tab
        import_frame = ttk.Frame(notebook)
        notebook.add(import_frame, text="Importa Dati")
        self.create_import_tab(import_frame)

        # Close button
        close_btn = ttk.Button(self.dialog, text="Chiudi", command=self.dialog.destroy)
        close_btn.pack(pady=10)

    def create_export_tab(self, parent):
        """Create export tab widgets"""
        # Header
        header = ttk.Label(parent, text="Esporta Dati", font=('Arial', 14, 'bold'))
        header.pack(pady=10)

        desc = ttk.Label(parent, text="Esporta i tuoi dati archeologici in formato Excel o CSV",
                        wraplength=650)
        desc.pack(pady=5)

        # Export Sites Section
        sites_frame = ttk.LabelFrame(parent, text="Siti Archeologici", padding=10)
        sites_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(sites_frame, text="Esporta tutti i siti nel database").pack(anchor=tk.W)

        sites_btn_frame = ttk.Frame(sites_frame)
        sites_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(sites_btn_frame, text="Esporta Excel",
                  command=lambda: self.export_data('sites', 'excel')).pack(side=tk.LEFT, padx=5)
        ttk.Button(sites_btn_frame, text="Esporta CSV",
                  command=lambda: self.export_data('sites', 'csv')).pack(side=tk.LEFT, padx=5)

        # Export US Section
        us_frame = ttk.LabelFrame(parent, text="Unità Stratigrafiche (US)", padding=10)
        us_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(us_frame, text="Filtra per sito (opzionale):").pack(anchor=tk.W)

        us_filter_frame = ttk.Frame(us_frame)
        us_filter_frame.pack(fill=tk.X, pady=5)

        self.us_site_var = tk.StringVar()
        us_entry = ttk.Entry(us_filter_frame, textvariable=self.us_site_var, width=30)
        us_entry.pack(side=tk.LEFT, padx=5)

        us_btn_frame = ttk.Frame(us_frame)
        us_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(us_btn_frame, text="Esporta Excel",
                  command=lambda: self.export_data('us', 'excel')).pack(side=tk.LEFT, padx=5)
        ttk.Button(us_btn_frame, text="Esporta CSV",
                  command=lambda: self.export_data('us', 'csv')).pack(side=tk.LEFT, padx=5)

        # Export Inventario Section
        inv_frame = ttk.LabelFrame(parent, text="Inventario Materiali", padding=10)
        inv_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(inv_frame, text="Filtra per sito (opzionale):").pack(anchor=tk.W)

        inv_filter_frame = ttk.Frame(inv_frame)
        inv_filter_frame.pack(fill=tk.X, pady=5)

        self.inv_site_var = tk.StringVar()
        inv_entry = ttk.Entry(inv_filter_frame, textvariable=self.inv_site_var, width=30)
        inv_entry.pack(side=tk.LEFT, padx=5)

        inv_btn_frame = ttk.Frame(inv_frame)
        inv_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(inv_btn_frame, text="Esporta Excel",
                  command=lambda: self.export_data('inventario', 'excel')).pack(side=tk.LEFT, padx=5)
        ttk.Button(inv_btn_frame, text="Esporta CSV",
                  command=lambda: self.export_data('inventario', 'csv')).pack(side=tk.LEFT, padx=5)

    def create_import_tab(self, parent):
        """Create import tab widgets"""
        # Header
        header = ttk.Label(parent, text="Importa Dati da CSV", font=('Arial', 14, 'bold'))
        header.pack(pady=10)

        desc = ttk.Label(parent, text="Importa dati da file CSV. I file devono seguire la struttura delle tabelle.",
                        wraplength=650)
        desc.pack(pady=5)

        # Warning
        warning_frame = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=2)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(warning_frame, text="⚠ Attenzione!", font=('Arial', 10, 'bold'),
                 foreground='red').pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(warning_frame,
                 text="L'import può sovrascrivere dati esistenti. Backup consigliato!",
                 wraplength=650).pack(anchor=tk.W, padx=10, pady=5)

        # Skip duplicates checkbox
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Salta record duplicati (mantieni dati esistenti)",
                       variable=self.skip_duplicates_var).pack(anchor=tk.W, padx=20, pady=10)

        # Import Sites
        sites_frame = ttk.LabelFrame(parent, text="Importa Siti", padding=10)
        sites_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(sites_frame, text="Seleziona file CSV e Importa Siti",
                  command=lambda: self.import_data('sites')).pack(pady=5)

        # Import US
        us_frame = ttk.LabelFrame(parent, text="Importa Unità Stratigrafiche", padding=10)
        us_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(us_frame, text="Seleziona file CSV e Importa US",
                  command=lambda: self.import_data('us')).pack(pady=5)

        # Import Inventario
        inv_frame = ttk.LabelFrame(parent, text="Importa Inventario Materiali", padding=10)
        inv_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(inv_frame, text="Seleziona file CSV e Importa Inventario",
                  command=lambda: self.import_data('inventario')).pack(pady=5)

    def export_data(self, entity_type, format):
        """
        Export data to file

        Args:
            entity_type: Type of entity (sites, us, inventario)
            format: Export format (excel, csv)
        """
        try:
            from pyarchinit_mini.services.export_import_service import ExportImportService
        except ImportError:
            messagebox.showerror(
                "Errore",
                "Modulo export non disponibile.\n\n"
                "Installa con: pip install 'pyarchinit-mini[export]'"
            )
            return

        # Get file save location
        if format == 'excel':
            file_ext = '.xlsx'
            file_types = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        else:
            file_ext = '.csv'
            file_types = [("CSV files", "*.csv"), ("All files", "*.*")]

        default_name = f"{entity_type}_export{file_ext}"
        filename = filedialog.asksaveasfilename(
            parent=self.dialog,
            title=f"Salva {entity_type.capitalize()} come {format.upper()}",
            defaultextension=file_ext,
            filetypes=file_types,
            initialfile=default_name
        )

        if not filename:
            return

        try:
            service = ExportImportService(self.db_manager)

            # Get site filter if applicable
            site_filter = None
            if entity_type == 'us':
                site_filter = self.us_site_var.get().strip() or None
            elif entity_type == 'inventario':
                site_filter = self.inv_site_var.get().strip() or None

            # Export data
            if entity_type == 'sites':
                if format == 'excel':
                    service.export_sites_to_excel(filename)
                else:
                    service.export_sites_to_csv(filename)
            elif entity_type == 'us':
                if format == 'excel':
                    service.export_us_to_excel(filename, site_filter)
                else:
                    service.export_us_to_csv(filename, site_filter)
            elif entity_type == 'inventario':
                if format == 'excel':
                    service.export_inventario_to_excel(filename, site_filter)
                else:
                    service.export_inventario_to_csv(filename, site_filter)

            messagebox.showinfo(
                "Successo",
                f"Export completato con successo!\n\nFile salvato: {filename}"
            )

        except Exception as e:
            messagebox.showerror("Errore Export", f"Errore durante l'export:\n\n{str(e)}")

    def import_data(self, entity_type):
        """
        Import data from CSV file

        Args:
            entity_type: Type of entity (sites, us, inventario)
        """
        try:
            from pyarchinit_mini.services.export_import_service import ExportImportService
        except ImportError:
            messagebox.showerror(
                "Errore",
                "Modulo export non disponibile.\n\n"
                "Installa con: pip install 'pyarchinit-mini[export]'"
            )
            return

        # Get file to import
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title=f"Seleziona CSV da importare ({entity_type.capitalize()})",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            service = ExportImportService(self.db_manager)
            skip_duplicates = self.skip_duplicates_var.get()

            # Import data
            if entity_type == 'sites':
                result = service.batch_import_sites_from_csv(filename, skip_duplicates)
            elif entity_type == 'us':
                result = service.batch_import_us_from_csv(filename, skip_duplicates)
            elif entity_type == 'inventario':
                result = service.batch_import_inventario_from_csv(filename, skip_duplicates)

            # Show results
            msg = f"Import completato!\n\n"
            msg += f"Totale record: {result['total']}\n"
            msg += f"Importati: {result['imported']}\n"
            msg += f"Saltati (duplicati): {result['skipped']}\n"
            msg += f"Errori: {len(result['errors'])}"

            if result['errors']:
                msg += f"\n\nPrimi errori:\n"
                for i, err in enumerate(result['errors'][:3], 1):
                    msg += f"{i}. {err['error']}\n"

            if result['imported'] > 0:
                messagebox.showinfo("Import Completato", msg)
                # Refresh the parent window if method exists
                if hasattr(self.parent, 'refresh_current_tab'):
                    self.parent.refresh_current_tab()
            else:
                messagebox.showwarning("Import", msg)

        except Exception as e:
            messagebox.showerror("Errore Import", f"Errore durante l'import:\n\n{str(e)}")


def show_export_import_dialog(parent, db_manager):
    """
    Show export/import dialog

    Args:
        parent: Parent window
        db_manager: DatabaseManager instance
    """
    ExportImportDialog(parent, db_manager)
