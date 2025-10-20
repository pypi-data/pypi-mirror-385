"""
GraphML Converter - DOT to GraphML (yEd) Converter for Harris Matrix

This module provides a clean API for converting Graphviz DOT files to
yEd-compatible GraphML format, specifically designed for archaeological
Harris Matrix diagrams.

Usage:
    from pyarchinit_mini.graphml_converter import convert_dot_to_graphml

    # Convert from file paths
    convert_dot_to_graphml(
        'input.dot',
        'output.graphml',
        title="Pompei - Regio VI",
        reverse_epochs=False
    )

    # Convert from string content
    from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

    dot_content = "digraph { ... }"
    graphml_content = convert_dot_content_to_graphml(
        dot_content,
        title="My Site",
        reverse_epochs=True
    )
"""

import os
import locale
from io import StringIO
from . import dot_parser as dot
from . import graphml_exporter as exporter


class GraphMLConverterOptions:
    """Options for GraphML conversion"""

    def __init__(self):
        # Node and edge labels
        self.NodeLabels = True
        self.EdgeLabels = True
        self.NodeUml = True
        self.Arrows = True
        self.Colors = True

        # Attributes
        self.LumpAttributes = True
        self.SepChar = '_'
        self.EdgeLabelsAutoComplete = False

        # Arrow styles
        self.DefaultArrowHead = 'none'
        self.DefaultArrowTail = 'none'

        # Colors (RGB format)
        self.DefaultNodeColor = '#CCCCFF'
        self.DefaultEdgeColor = '#000000'
        self.DefaultNodeTextColor = '#000000'
        self.DefaultEdgeTextColor = '#000000'

        # Encoding
        preferredEncoding = locale.getpreferredencoding()
        self.InputEncoding = preferredEncoding
        self.OutputEncoding = preferredEncoding

        # Output format
        self.format = 'Graphml'
        self.verbose = False
        self.sweep = False


def parse_dot_file(input_dot_path, options=None):
    """
    Parse a DOT file and return nodes, edges, and options.

    Args:
        input_dot_path: Path to input .dot file
        options: GraphMLConverterOptions instance (optional)

    Returns:
        Tuple of (nodes_dict, edges_list, options)
    """
    if options is None:
        options = GraphMLConverterOptions()

    # Convert color names to RGB
    options.DefaultNodeColor = dot.colorNameToRgb(options.DefaultNodeColor, '#CCCCFF')
    options.DefaultEdgeColor = dot.colorNameToRgb(options.DefaultEdgeColor, '#000000')
    options.DefaultNodeTextColor = dot.colorNameToRgb(options.DefaultNodeTextColor, '#000000')
    options.DefaultEdgeTextColor = dot.colorNameToRgb(options.DefaultEdgeTextColor, '#000000')

    # Read DOT file
    with open(input_dot_path, 'r', encoding=options.InputEncoding) as f:
        content = f.read().splitlines()

    # Collect nodes and edges
    nodes = {}
    edges = []
    default_edge = None
    default_node = None
    nid = 1
    eid = 1

    idx = 0
    while idx < len(content):
        l = '{}'.format(content[idx])

        if '->' in l:
            # Check for multiline edge
            if '[' in l and ']' not in l:
                ml = ""
                while ']' not in ml:
                    idx += 1
                    ml = '{}'.format(content[idx])
                    l = ' '.join([l.rstrip(), ml.lstrip()])

            # Process edge
            e = dot.Edge()
            e.initFromString(l)
            e.id = eid
            eid += 1
            if default_edge:
                e.complementAttributes(default_edge)
            edges.append(e)

        elif '[' in l:
            # Check for multiline node
            if ']' not in l:
                ml = ""
                while ']' not in ml:
                    idx += 1
                    ml = '{}'.format(content[idx])
                    l = ' '.join([l.rstrip(), ml.lstrip()])

            # Process node
            n = dot.Node()
            n.initFromString(l)
            lowlabel = n.label.lower()

            if (lowlabel != 'graph' and
                lowlabel != 'subgraph' and
                lowlabel != 'edge' and
                lowlabel != 'node'):
                n.id = nid
                nid += 1
                if default_node:
                    n.complementAttributes(default_node)
                nodes[n.label] = n
            else:
                if lowlabel == 'edge':
                    default_edge = n
                elif lowlabel == 'node':
                    default_node = n

        elif 'charset=' in l:
            # Pick up input encoding from DOT file
            li = l.strip().split('=')
            if len(li) == 2:
                ienc = li[1].strip('"')
                if ienc != "":
                    options.InputEncoding = ienc
                    if options.verbose:
                        print(f"Info: Picked up input encoding '{ienc}' from the DOT file.")

        idx += 1

    # Add single nodes referenced by edges
    for e in edges:
        if e.src not in nodes:
            n = dot.Node()
            n.label = e.src
            n.id = nid
            nid += 1
            nodes[e.src] = n
        if e.dest not in nodes:
            n = dot.Node()
            n.label = e.dest
            n.id = nid
            nid += 1
            nodes[e.dest] = n
        nodes[e.src].referenced = True
        nodes[e.dest].referenced = True

    if options.verbose:
        print(f"\nNodes: {len(nodes)}")
        print(f"Edges: {len(edges)}")

    # Sweep unreferenced nodes if requested
    if options.sweep:
        rnodes = {}
        for key, n in nodes.items():
            if n.referenced:
                rnodes[key] = n
        nodes = rnodes
        if options.verbose:
            print(f"\nNodes after sweep: {len(nodes)}")

    return nodes, edges, options


def convert_dot_to_graphml(input_dot_path, output_graphml_path, title="", reverse_epochs=False, options=None):
    """
    Convert a DOT file to GraphML format (yEd compatible).

    Args:
        input_dot_path: Path to input .dot file
        output_graphml_path: Path to output .graphml file
        title: Diagram title/header (default: "")
        reverse_epochs: Whether to reverse epoch ordering (default: False)
        options: GraphMLConverterOptions instance (optional)

    Returns:
        True if conversion successful, False otherwise

    Example:
        convert_dot_to_graphml(
            'harris_matrix.dot',
            'harris_matrix.graphml',
            title="Pompei - Regio VI",
            reverse_epochs=False
        )
    """
    try:
        # Parse DOT file
        nodes, edges, options = parse_dot_file(input_dot_path, options)

        # Export to GraphML
        with open(output_graphml_path, 'w', encoding='utf-8') as output_file:
            exporter.exportGraphml(
                output_file,
                nodes,
                edges,
                options,
                title=title,
                reverse_epochs=reverse_epochs
            )

        return True

    except Exception as e:
        if options and options.verbose:
            print(f"Error converting DOT to GraphML: {e}")
            import traceback
            traceback.print_exc()
        return False


def convert_dot_content_to_graphml(dot_content, title="", reverse_epochs=False, options=None):
    """
    Convert DOT content (string) to GraphML content (string).

    Args:
        dot_content: DOT file content as string
        title: Diagram title/header (default: "")
        reverse_epochs: Whether to reverse epoch ordering (default: False)
        options: GraphMLConverterOptions instance (optional)

    Returns:
        GraphML content as string, or None if conversion fails

    Example:
        dot_content = '''
        digraph {
            "US 1001" [label="US 1001"];
            "US 1002" [label="US 1002"];
            "US 1001" -> "US 1002" [label="Covers"];
        }
        '''
        graphml_content = convert_dot_content_to_graphml(
            dot_content,
            title="Test Site"
        )
    """
    import tempfile

    try:
        # Write DOT content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as tmp_dot:
            tmp_dot.write(dot_content)
            tmp_dot_path = tmp_dot.name

        # Create temporary GraphML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as tmp_graphml:
            tmp_graphml_path = tmp_graphml.name

        # Convert
        success = convert_dot_to_graphml(
            tmp_dot_path,
            tmp_graphml_path,
            title=title,
            reverse_epochs=reverse_epochs,
            options=options
        )

        if not success:
            return None

        # Read GraphML content
        with open(tmp_graphml_path, 'r', encoding='utf-8') as f:
            graphml_content = f.read()

        return graphml_content

    except Exception as e:
        if options and options.verbose:
            print(f"Error converting DOT content to GraphML: {e}")
            import traceback
            traceback.print_exc()
        return None

    finally:
        # Clean up temporary files
        try:
            if 'tmp_dot_path' in locals():
                os.unlink(tmp_dot_path)
            if 'tmp_graphml_path' in locals():
                os.unlink(tmp_graphml_path)
        except:
            pass


def get_template_path():
    """
    Get the path to the yEd GraphML template file.

    Returns:
        Path to EM_palette.graphml template
    """
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    return os.path.join(template_dir, 'EM_palette.graphml')
