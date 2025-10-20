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

            # Generate Harris Matrix graph (with transitive reduction already applied)
            graph = self.matrix_generator.generate_matrix(site_name)

            # Generate DOT manually with GraphML-compatible node ID format
            # GraphML converter requires: US_number_description_epoch
            # This allows it to extract epoch and create y:Row elements for period grouping

            # Get all relevant US
            us_rilevanti = set()
            for source, target in graph.edges():
                us_rilevanti.add(source)
                us_rilevanti.add(target)

            # Start DOT
            dot_lines = []
            dot_lines.append('digraph {')
            dot_lines.append('\trankdir=BT')

            # Extract unique periods for y:Row generation
            periodi_unici = set()
            for node in us_rilevanti:
                if node in graph.nodes:
                    periodo = graph.nodes[node].get('period_initial', graph.nodes[node].get('periodo_iniziale', 'Sconosciuto'))
                    periodi_unici.add(periodo.replace(' ', '-'))  # Use dash

            # EM_palette node styles mapping based on unita_tipo
            US_STYLES = {
                'US': {  # Stratigraphic Unit (strato, riempimento, etc.)
                    'shape': 'box',
                    'fillcolor': '#FFFFFF',
                    'color': '#9B3333',  # red border
                    'penwidth': '4.0',
                    'style': 'filled'
                },
                'USM': {  # Unità Stratigrafica Muraria (masonry)
                    'shape': 'box',
                    'fillcolor': '#FFFFFF',
                    'color': '#9B3333',  # red border
                    'penwidth': '4.0',
                    'style': 'filled'
                },
                'USD': {  # Documentary US
                    'shape': 'box',
                    'fillcolor': '#FFFFFF',
                    'color': '#D86400',  # orange border
                    'penwidth': '4.0',
                    'style': 'rounded,filled'
                },
                'USV': {  # Virtual US negative
                    'shape': 'hexagon',
                    'fillcolor': '#000000',
                    'color': '#31792D',  # green border
                    'penwidth': '4.0',
                    'style': 'filled'
                },
                'USV/s': {  # Virtual US structural
                    'shape': 'trapezium',  # closest to parallelogram
                    'fillcolor': '#000000',
                    'color': '#248FE7',  # blue border
                    'penwidth': '4.0',
                    'style': 'filled'
                },
                'default': {  # Fallback for unknown types
                    'shape': 'box',
                    'fillcolor': '#CCCCFF',
                    'color': '#000000',
                    'penwidth': '2.0',
                    'style': 'filled'
                }
            }

            # Add period label nodes (required by GraphML converter to create y:Row elements)
            for periodo in sorted(periodi_unici):
                dot_lines.append(f'\t"Periodo : {periodo}" [shape=plaintext]')

            # Create nodes with GraphML-compatible format + EM_palette styles
            # Node ID: US_1001_Description_Period
            # Node label: US1001_Period (period included for get_y() to work)
            for node in sorted(us_rilevanti):
                if node not in graph.nodes:
                    continue

                node_data = graph.nodes[node]
                periodo = node_data.get('period_initial', node_data.get('periodo_iniziale', 'Sconosciuto'))
                d_stratigrafica = node_data.get('d_stratigrafica', node_data.get('description', ''))
                d_interpretativa = node_data.get('d_interpretativa', node_data.get('interpretation', ''))
                unita_tipo = node_data.get('unita_tipo', 'US')  # Extract unit type

                # Build node tooltip/description: d_stratigrafica + d_interpretativa
                node_description_parts = []
                if d_stratigrafica:
                    node_description_parts.append(d_stratigrafica)
                if d_interpretativa:
                    node_description_parts.append(d_interpretativa)
                node_description = ' - '.join(node_description_parts) if node_description_parts else ''

                # Clean description and period (remove spaces and special chars)
                desc_clean = d_stratigrafica.replace(' ', '_').replace(',', '').replace('"', '')
                if len(desc_clean) > 30:
                    desc_clean = desc_clean[:30]

                # Clean period: replace spaces with dash (not underscore)
                # This allows rsplit('_', 1) to extract the full period name
                periodo_clean = periodo.replace(' ', '-')  # Romano Imperiale → Romano-Imperiale

                # Node ID format: US_numero_descrizione_periodo
                # rsplit('_', 1) will extract "Romano-Imperiale" correctly
                node_id = f"US_{node}_{desc_clean}_{periodo_clean}"

                # Label: Include period for get_y() to work
                # Format: US1001_Romano-Imperiale (so get_y can find the period in LabelText)
                label = f"US{node}_{periodo_clean}"

                # Get style for this node based on unita_tipo
                style_dict = US_STYLES.get(unita_tipo, US_STYLES['default'])

                # Build node attributes
                attrs = [
                    f'label="{label}"',
                    f'fillcolor="{style_dict["fillcolor"]}"',
                    f'color="{style_dict["color"]}"',
                    f'shape={style_dict["shape"]}',
                    f'penwidth={style_dict["penwidth"]}',
                    f'style={style_dict["style"]}'
                ]

                # Add tooltip with node description (d_stratigrafica + d_interpretativa)
                if node_description:
                    # Clean description for DOT format (escape quotes)
                    desc_escaped = node_description.replace('"', '\\"').replace('\n', '\\n')
                    attrs.append(f'tooltip="{desc_escaped}"')

                # Add node with EM_palette styling
                dot_lines.append(f'\t"{node_id}" [{", ".join(attrs)}]')

            # Add edges with EM_palette styling based on relationship type
            for source, target in graph.edges():
                if source not in graph.nodes or target not in graph.nodes:
                    continue

                edge_data = graph.get_edge_data(source, target)
                rel_type = edge_data.get('relationship', edge_data.get('type', 'sopra'))

                source_data = graph.nodes[source]
                target_data = graph.nodes[target]

                source_periodo = source_data.get('period_initial', source_data.get('periodo_iniziale', 'Sconosciuto'))
                target_periodo = target_data.get('period_initial', target_data.get('periodo_iniziale', 'Sconosciuto'))

                source_desc = source_data.get('d_stratigrafica', source_data.get('description', ''))
                target_desc = target_data.get('d_stratigrafica', target_data.get('description', ''))

                desc_source_clean = source_desc.replace(' ', '_').replace(',', '').replace('"', '')[:30]
                desc_target_clean = target_desc.replace(' ', '_').replace(',', '').replace('"', '')[:30]

                # Clean periods (use dash, not underscore)
                source_periodo_clean = source_periodo.replace(' ', '-')
                target_periodo_clean = target_periodo.replace(' ', '-')

                source_id = f"US_{source}_{desc_source_clean}_{source_periodo_clean}"
                target_id = f"US_{target}_{desc_target_clean}_{target_periodo_clean}"

                # Determine edge attributes based on relationship type
                # Following PyArchInit convention for EM_palette
                rel_lower = rel_type.lower()
                edge_attrs = []

                # Contemporary relationships (uguale a, si lega a): NO arrow (arrowhead=none)
                if 'uguale' in rel_lower or 'lega' in rel_lower or 'same' in rel_lower or 'connected' in rel_lower:
                    edge_attrs.append('dir=none')  # No arrowhead in either direction
                # Negative relationships (taglia): dashed line with arrow
                elif 'taglia' in rel_lower or 'tagli' in rel_lower or 'cut' in rel_lower:
                    edge_attrs.append('style=dashed')
                    edge_attrs.append('arrowhead=normal')
                # Virtual or uncertain relationships: dashed line
                elif 'virtuale' in rel_lower or 'dubbio' in rel_lower or 'virtual' in rel_lower or 'uncertain' in rel_lower:
                    edge_attrs.append('style=dashed')
                    edge_attrs.append('arrowhead=normal')
                # Normal stratigraphic relationships (copre, sotto, etc.): solid line with arrow
                else:
                    edge_attrs.append('arrowhead=normal')

                # Build edge with styling (NO label - as per user request)
                # Optionally add relationship type as tooltip
                if rel_type:
                    edge_attrs.append(f'tooltip="{rel_type}"')

                edge_attr_str = ', '.join(edge_attrs) if edge_attrs else ''
                if edge_attr_str:
                    dot_lines.append(f'\t"{source_id}" -> "{target_id}" [{edge_attr_str}]')
                else:
                    dot_lines.append(f'\t"{source_id}" -> "{target_id}"')

            dot_lines.append('}')
            dot_content = '\n'.join(dot_lines)

            # Convert to GraphML
            from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

            graphml_content = convert_dot_content_to_graphml(
                dot_content,
                title=title,
                reverse_epochs=reverse_epochs
            )

            # Post-process GraphML to clean node labels (remove period from label)
            # Change "US1001_Medievale" to "US1001"
            if graphml_content:
                import re
                # Pattern: <y:NodeLabel...>US1234_Period-Name</y:NodeLabel>
                # Replace with: <y:NodeLabel...>US1234</y:NodeLabel>
                graphml_content = re.sub(
                    r'(>US\d+)_[^<]+(<\/y:NodeLabel>)',
                    r'\1\2',
                    graphml_content
                )

                # Apply EM_palette colors to nodes based on unita_tipo
                # AND add node descriptions (d_stratigrafica + d_interpretativa)
                try:
                    import xml.dom.minidom as minidom

                    # Build unita_tipo map and description map from graph
                    unita_tipo_map = {}
                    description_map = {}
                    for node in us_rilevanti:
                        if node in graph.nodes:
                            node_data = graph.nodes[node]
                            unita_tipo_map[node] = node_data.get('unita_tipo', 'US')

                            # Build description: d_stratigrafica + d_interpretativa
                            d_strat = node_data.get('d_stratigrafica', node_data.get('description', ''))
                            d_interp = node_data.get('d_interpretativa', node_data.get('interpretation', ''))
                            desc_parts = []
                            if d_strat:
                                desc_parts.append(d_strat)
                            if d_interp:
                                desc_parts.append(d_interp)
                            if desc_parts:
                                description_map[node] = ' - '.join(desc_parts)

                    # Parse and modify GraphML
                    dom = minidom.parseString(graphml_content)
                    nodes_modified = 0
                    descriptions_added = 0

                    # Find all ShapeNode elements (US nodes)
                    for shape_node in dom.getElementsByTagName('y:ShapeNode'):
                        # Find the label
                        labels = shape_node.getElementsByTagName('y:NodeLabel')
                        if not labels or not labels[0].firstChild:
                            continue

                        label_text = labels[0].firstChild.nodeValue
                        match = re.match(r'US(\d+)', label_text)
                        if not match:
                            continue

                        us_number = int(match.group(1))
                        unita_tipo = unita_tipo_map.get(us_number, 'US')

                        # Get colors from US_STYLES
                        style = US_STYLES.get(unita_tipo, US_STYLES['default'])

                        # Update Fill color
                        fill_nodes = shape_node.getElementsByTagName('y:Fill')
                        if fill_nodes:
                            fill_nodes[0].setAttribute('color', style['fillcolor'])
                            nodes_modified += 1

                        # Update BorderStyle color and width
                        border_nodes = shape_node.getElementsByTagName('y:BorderStyle')
                        if border_nodes:
                            border_nodes[0].setAttribute('color', style['color'])
                            border_nodes[0].setAttribute('width', style['penwidth'])

                        # Add description (d_stratigrafica + d_interpretativa) to node
                        if us_number in description_map:
                            # Navigate to parent <node> element
                            # Structure: <node> -> <data key="d6"> -> <y:ShapeNode>
                            # Note: In the GraphML generated, d5 = description, d6 = nodegraphics
                            data_element = shape_node.parentNode
                            node_element = data_element.parentNode

                            # Check if <data key="d5"> already exists (description field)
                            existing_desc = None
                            for child in node_element.childNodes:
                                if child.nodeType == child.ELEMENT_NODE and child.tagName == 'data':
                                    if child.getAttribute('key') == 'd5':
                                        existing_desc = child
                                        break

                            # Create or update description element
                            description_text = description_map[us_number]
                            if existing_desc:
                                # Update existing (usually empty)
                                if existing_desc.firstChild:
                                    existing_desc.firstChild.nodeValue = description_text
                                else:
                                    # Create text node if missing
                                    text_node = dom.createTextNode(description_text)
                                    existing_desc.appendChild(text_node)
                                descriptions_added += 1
                            else:
                                # Create new <data key="d5"> element
                                desc_element = dom.createElement('data')
                                desc_element.setAttribute('key', 'd5')
                                desc_element.setAttribute('xml:space', 'preserve')
                                desc_text_node = dom.createTextNode(description_text)
                                desc_element.appendChild(desc_text_node)
                                # Insert before <data key="d6"> (graphics data)
                                node_element.insertBefore(desc_element, data_element)
                                descriptions_added += 1

                    graphml_content = dom.toxml()
                    print(f'✓ Stili EM_palette applicati a {nodes_modified} nodi, {descriptions_added} descrizioni aggiunte')
                except Exception as style_error:
                    # Non-fatal: continue even if styling fails
                    print(f'⚠ Avviso: impossibile applicare stili EM_palette: {str(style_error)}')

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
