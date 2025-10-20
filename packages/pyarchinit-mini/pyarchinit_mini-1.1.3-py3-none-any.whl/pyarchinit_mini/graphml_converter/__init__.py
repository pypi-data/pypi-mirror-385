"""
GraphML Converter - DOT to GraphML (yEd) Converter for Harris Matrix

Convert Graphviz DOT files to yEd-compatible GraphML format,
specifically optimized for archaeological Harris Matrix diagrams.

Usage:
    # Basic conversion
    from pyarchinit_mini.graphml_converter import convert_dot_to_graphml

    convert_dot_to_graphml(
        'input.dot',
        'output.graphml',
        title="Site Name",
        reverse_epochs=False
    )

    # Convert from string content
    from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

    graphml_content = convert_dot_content_to_graphml(
        dot_content_string,
        title="My Site"
    )

    # Use in other projects
    import pyarchinit_mini.graphml_converter as gml

    gml.convert_dot_to_graphml('input.dot', 'output.graphml')
"""

from .converter import (
    convert_dot_to_graphml,
    convert_dot_content_to_graphml,
    GraphMLConverterOptions,
    get_template_path
)

__all__ = [
    'convert_dot_to_graphml',
    'convert_dot_content_to_graphml',
    'GraphMLConverterOptions',
    'get_template_path'
]

__version__ = '1.0.0'
__author__ = 'PyArchInit Team'
