"""
GraphML Export Dialog for Desktop GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path


class GraphMLExportDialog:
    """Dialog for GraphML export of Harris Matrix"""

    def __init__(self, parent, matrix_generator, matrix_visualizer, site_service):
        """
        Initialize GraphML export dialog

        Args:
            parent: Parent window
            matrix_generator: HarrisMatrixGenerator instance
            matrix_visualizer: PyArchInitMatrixVisualizer instance
            site_service: SiteService instance
        """
        self.parent = parent
        self.matrix_generator = matrix_generator
        self.matrix_visualizer = matrix_visualizer
        self.site_service = site_service

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Harris Matrix to GraphML (yEd)")
        self.dialog.geometry("700x650")
        self.dialog.resizable(True, True)

        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Variables
        self.selected_site = tk.StringVar()
        self.title_var = tk.StringVar()
        self.grouping_var = tk.StringVar(value='period_area')
        self.reverse_epochs_var = tk.BooleanVar(value=False)

        self.create_widgets()
        self.load_sites()

    def create_widgets(self):
        """Create dialog widgets"""
        # Header
        header = ttk.Label(self.dialog, text="Export Harris Matrix to GraphML",
                          font=('Arial', 14, 'bold'))
        header.pack(pady=10)

        desc = ttk.Label(self.dialog,
                        text="Esporta la Harris Matrix in formato GraphML compatibile con yEd Graph Editor.\n"
                             "Questo formato preserva la struttura dei periodi archeologici.",
                        wraplength=600, justify=tk.CENTER)
        desc.pack(pady=5)

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Site selection
        site_frame = ttk.LabelFrame(main_frame, text="Sito Archeologico", padding=10)
        site_frame.pack(fill=tk.X, pady=10)

        ttk.Label(site_frame, text="Seleziona il sito:").pack(anchor=tk.W, pady=(0, 5))
        self.site_combo = ttk.Combobox(site_frame, textvariable=self.selected_site,
                                       state='readonly', width=40)
        self.site_combo.pack(fill=tk.X)

        # Title
        title_frame = ttk.LabelFrame(main_frame, text="Titolo Diagramma (opzionale)", padding=10)
        title_frame.pack(fill=tk.X, pady=10)

        ttk.Label(title_frame, text="Intestazione da visualizzare nel diagramma:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Entry(title_frame, textvariable=self.title_var, width=40).pack(fill=tk.X)
        ttk.Label(title_frame, text="Es: Pompei - Regio VI", font=('Arial', 9, 'italic')).pack(anchor=tk.W)

        # Grouping
        grouping_frame = ttk.LabelFrame(main_frame, text="Raggruppamento", padding=10)
        grouping_frame.pack(fill=tk.X, pady=10)

        ttk.Label(grouping_frame, text="Come raggruppare le unità stratigrafiche:").pack(anchor=tk.W, pady=(0, 5))

        grouping_options = [
            ('period_area', 'Periodo + Area'),
            ('period', 'Solo Periodo'),
            ('area', 'Solo Area'),
            ('none', 'Nessun Raggruppamento')
        ]

        for value, text in grouping_options:
            ttk.Radiobutton(grouping_frame, text=text, variable=self.grouping_var,
                           value=value).pack(anchor=tk.W, padx=10)

        # Reverse epochs
        reverse_frame = ttk.Frame(main_frame)
        reverse_frame.pack(fill=tk.X, pady=10)

        ttk.Checkbutton(reverse_frame, text="Inverti ordine periodi (Periodo 1 = ultima epoca scavata)",
                       variable=self.reverse_epochs_var).pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Export GraphML", command=self.export_graphml,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Chiudi", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Help
        help_frame = ttk.LabelFrame(self.dialog, text="Info", padding=10)
        help_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        help_text = ("Il file GraphML può essere aperto con yEd Graph Editor.\n"
                    "Download gratuito: https://www.yworks.com/products/yed")
        ttk.Label(help_frame, text=help_text, font=('Arial', 9), foreground='gray').pack()

    def load_sites(self):
        """Load available sites"""
        try:
            sites = self.site_service.get_all_sites()
            site_names = [s.sito for s in sites if s.sito]

            if site_names:
                self.site_combo['values'] = site_names
                self.site_combo.current(0)
                # Set default title to first site name
                self.title_var.set(site_names[0])
            else:
                messagebox.showwarning("Avviso", "Nessun sito disponibile nel database")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento siti: {str(e)}")

    def export_graphml(self):
        """Export Harris Matrix to GraphML file"""
        try:
            site_name = self.selected_site.get()
            if not site_name:
                messagebox.showwarning("Avviso", "Seleziona un sito")
                return

            title = self.title_var.get() or site_name
            grouping = self.grouping_var.get()
            reverse_epochs = self.reverse_epochs_var.get()

            # Ask for output file
            default_filename = f"{site_name}_harris_matrix.graphml"
            filepath = filedialog.asksaveasfilename(
                parent=self.dialog,
                title="Salva Harris Matrix GraphML",
                defaultextension=".graphml",
                initialfile=default_filename,
                filetypes=[
                    ("GraphML files", "*.graphml"),
                    ("All files", "*.*")
                ]
            )

            if not filepath:
                return

            # Generate Harris Matrix graph
            graph = self.matrix_generator.generate_matrix(site_name)

            # Create Graphviz DOT structure
            from graphviz import Digraph

            G = Digraph(engine='dot', strict=False)
            G.attr(
                rankdir='BT',
                compound='true',
                pad='0.5',
                nodesep='0.5',
                ranksep='1.0'
            )

            # Categorize relationships
            us_rilevanti = set()
            for source, target in graph.edges():
                us_rilevanti.add(source)
                us_rilevanti.add(target)

            # Create nodes based on grouping
            if grouping != 'none':
                if grouping == 'period_area':
                    # Nested structure: {periodo: {area: [nodes]}}
                    period_groups = {}
                    for node in us_rilevanti:
                        if node not in graph.nodes:
                            continue
                        node_data = graph.nodes[node]
                        periodo = node_data.get('period_initial', node_data.get('periodo_iniziale', 'Sconosciuto'))
                        area = node_data.get('area', 'A')

                        if periodo not in period_groups:
                            period_groups[periodo] = {}
                        if area not in period_groups[periodo]:
                            period_groups[periodo][area] = []
                        period_groups[periodo][area].append(node)

                    # Create period labels and nodes grouped by area
                    for periodo, areas in sorted(period_groups.items()):
                        G.node(f"Periodo : {periodo}", shape='plaintext')

                        # Add nodes grouped by area within this period
                        for area, nodes in sorted(areas.items()):
                            for node in sorted(nodes):
                                node_data = graph.nodes[node]
                                descrizione = node_data.get('d_stratigrafica', '')
                                node_id = f"US_{node}_{descrizione}_{periodo}"
                                display_label = f"US {node}\\n{descrizione}"

                                G.node(node_id,
                                      label=display_label,
                                      shape='box',
                                      style='filled',
                                      fillcolor='#CCCCFF')
                else:
                    # Flat grouping for 'period' or 'area' modes
                    groups = {}
                    for node in us_rilevanti:
                        if node not in graph.nodes:
                            continue
                        node_data = graph.nodes[node]

                        if grouping == 'period':
                            group_key = node_data.get('period_initial', node_data.get('periodo_iniziale', 'Sconosciuto'))
                        else:  # area
                            group_key = node_data.get('area', 'A')

                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(node)

                    # Create labeled groups
                    for group_key, nodes in sorted(groups.items()):
                        G.node(f"Periodo : {group_key}", shape='plaintext')

                        for node in sorted(nodes):
                            node_data = graph.nodes[node]
                            descrizione = node_data.get('d_stratigrafica', '')
                            node_id = f"US_{node}_{descrizione}_{group_key}"
                            display_label = f"US {node}\\n{descrizione}"

                            G.node(node_id,
                                  label=display_label,
                                  shape='box',
                                  style='filled',
                                  fillcolor='#CCCCFF')
            else:
                # Simple nodes without grouping
                for node in us_rilevanti:
                    if node not in graph.nodes:
                        continue
                    node_data = graph.nodes[node]
                    descrizione = node_data.get('d_stratigrafica', '')
                    display_label = f"US {node}\\n{descrizione}"

                    G.node(f"US {node}",
                          label=display_label,
                          shape='box',
                          style='filled',
                          fillcolor='#CCCCFF')

            # Add edges
            for source, target in graph.edges():
                edge_data = graph.get_edge_data(source, target)
                rel_type = edge_data.get('relationship', edge_data.get('type', 'sopra'))

                # Format node names to match those created above
                if grouping != 'none':
                    source_data = graph.nodes.get(source, {})
                    target_data = graph.nodes.get(target, {})

                    source_desc = source_data.get('d_stratigrafica', '')
                    target_desc = target_data.get('d_stratigrafica', '')

                    if grouping == 'period_area' or grouping == 'period':
                        # Use periodo for node ID (area is just visual grouping)
                        source_periodo = source_data.get('period_initial', source_data.get('periodo_iniziale', 'Sconosciuto'))
                        target_periodo = target_data.get('period_initial', target_data.get('periodo_iniziale', 'Sconosciuto'))
                        source_id = f"US_{source}_{source_desc}_{source_periodo}"
                        target_id = f"US_{target}_{target_desc}_{target_periodo}"
                    else:  # area
                        source_area = source_data.get('area', 'A')
                        target_area = target_data.get('area', 'A')
                        source_id = f"US_{source}_{source_desc}_{source_area}"
                        target_id = f"US_{target}_{target_desc}_{target_area}"
                else:
                    source_id = f"US {source}"
                    target_id = f"US {target}"

                G.edge(source_id, target_id, label=rel_type)

            # Get DOT source
            dot_content = G.source

            # Convert to GraphML
            from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

            graphml_content = convert_dot_content_to_graphml(
                dot_content,
                title=title,
                reverse_epochs=reverse_epochs
            )

            if graphml_content is None:
                messagebox.showerror("Errore", "Conversione a GraphML fallita")
                return

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(graphml_content)

            messagebox.showinfo("Successo",
                              f"Harris Matrix esportata con successo!\n\n"
                              f"File: {os.path.basename(filepath)}\n"
                              f"Dimensione: {len(graphml_content) / 1024:.1f} KB\n\n"
                              f"Apri il file con yEd Graph Editor per visualizzare e modificare la matrice.")

            self.dialog.destroy()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Errore", f"Errore durante l'export GraphML:\n\n{str(e)}")


def show_graphml_export_dialog(parent, matrix_generator, matrix_visualizer, site_service):
    """
    Show GraphML export dialog

    Args:
        parent: Parent window
        matrix_generator: HarrisMatrixGenerator instance
        matrix_visualizer: PyArchInitMatrixVisualizer instance
        site_service: SiteService instance
    """
    GraphMLExportDialog(parent, matrix_generator, matrix_visualizer, site_service)
