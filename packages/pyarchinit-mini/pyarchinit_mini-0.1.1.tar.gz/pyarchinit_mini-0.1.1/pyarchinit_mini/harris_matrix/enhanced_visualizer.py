#!/usr/bin/env python3
"""
Enhanced Harris Matrix visualizer with Graphviz support
Based on PyArchInit plugin approach with hierarchical orthogonal layout
"""

import os
import tempfile
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set
import json

class EnhancedHarrisMatrixVisualizer:
    """
    Enhanced Harris Matrix visualizer using Graphviz for hierarchical orthogonal layout
    Supports area/period/phase grouping and all stratigraphic relationships
    """
    
    def __init__(self):
        self.relationship_styles = {
            # Relationships with their inverse and styles
            'copre': {'inverse': 'coperto da', 'color': 'blue', 'style': 'solid', 'arrowhead': 'normal'},
            'coperto da': {'inverse': 'copre', 'color': 'blue', 'style': 'solid', 'arrowhead': 'inv'},
            'taglia': {'inverse': 'tagliato da', 'color': 'red', 'style': 'dashed', 'arrowhead': 'normal'},
            'tagliato da': {'inverse': 'taglia', 'color': 'red', 'style': 'dashed', 'arrowhead': 'inv'},
            'riempie': {'inverse': 'riempito da', 'color': 'green', 'style': 'dotted', 'arrowhead': 'normal'},
            'riempito da': {'inverse': 'riempie', 'color': 'green', 'style': 'dotted', 'arrowhead': 'inv'},
            'uguale a': {'inverse': 'uguale a', 'color': 'purple', 'style': 'bold', 'arrowhead': 'none'},
            'si lega a': {'inverse': 'si lega a', 'color': 'orange', 'style': 'solid', 'arrowhead': 'both'},
            'si appoggia': {'inverse': 'gli si appoggia', 'color': 'brown', 'style': 'solid', 'arrowhead': 'normal'},
            'gli si appoggia': {'inverse': 'si appoggia', 'color': 'brown', 'style': 'solid', 'arrowhead': 'inv'},
            'sopra': {'inverse': 'sotto', 'color': 'black', 'style': 'solid', 'arrowhead': 'normal'},
            'sotto': {'inverse': 'sopra', 'color': 'black', 'style': 'solid', 'arrowhead': 'inv'}
        }
        
        self.area_colors = {
            'A': '#FFE5E5',  # Light red
            'B': '#E5F3FF',  # Light blue  
            'C': '#E5FFE5',  # Light green
            'D': '#FFF5E5',  # Light orange
            'E': '#F5E5FF',  # Light purple
            'F': '#FFFFE5',  # Light yellow
        }
        
        self.period_shapes = {
            'Paleolitico': 'ellipse',
            'Mesolitico': 'ellipse', 
            'Neolitico': 'box',
            'Eneolitico': 'box',
            'Età del Bronzo': 'hexagon',
            'Età del Ferro': 'diamond',
            'Età Romana': 'rect',
            'Tardoantico': 'rect',
            'Altomedioevo': 'trapezium',
            'Medioevo': 'trapezium',
            'Postmedioevo': 'invtrapezium'
        }
    
    def create_graphviz_matrix(self, graph: nx.DiGraph, grouping: str = 'none', 
                              output_format: str = 'png', output_path: Optional[str] = None) -> str:
        """
        Create Harris Matrix using Graphviz with hierarchical orthogonal layout
        
        Args:
            graph: NetworkX directed graph
            grouping: 'none', 'area', 'period', 'phase', or 'area_period'
            output_format: 'png', 'svg', 'pdf', 'dot'
            output_path: Optional output file path
            
        Returns:
            Path to generated file or DOT source
        """
        try:
            import pygraphviz as pgv
        except ImportError:
            raise ImportError("pygraphviz is required for enhanced Harris Matrix visualization. "
                            "Install with: pip install pygraphviz")
        
        # Create new Graphviz graph
        G = pgv.AGraph(directed=True, strict=False)
        
        # Set graph attributes for hierarchical orthogonal layout
        G.graph_attr.update({
            'rankdir': 'TB',  # Top to bottom
            'splines': 'ortho',  # Orthogonal edges
            'nodesep': '0.8',
            'ranksep': '1.2',
            'concentrate': 'true',
            'compound': 'true',
            'fontname': 'Arial',
            'fontsize': '12',
            'bgcolor': 'white'
        })
        
        # Default node and edge attributes
        G.node_attr.update({
            'shape': 'box',
            'style': 'filled,rounded',
            'fontname': 'Arial',
            'fontsize': '10',
            'width': '1.5',
            'height': '1.0',
            'margin': '0.1'
        })
        
        G.edge_attr.update({
            'fontname': 'Arial',
            'fontsize': '8'
        })
        
        # Group nodes by specified criteria
        groups = self._group_nodes(graph, grouping)
        
        # Add subgraphs for grouping
        if grouping != 'none' and len(groups) > 1:
            self._add_subgraphs(G, groups, grouping)
        
        # Add nodes
        self._add_nodes_to_graph(G, graph, grouping)
        
        # Add edges with proper styling
        self._add_edges_to_graph(G, graph)
        
        # Set layout algorithm
        G.layout(prog='dot')  # Hierarchical layout
        
        # Generate output
        if output_path is None:
            output_path = tempfile.mktemp(suffix=f'.{output_format}')
        
        if output_format == 'dot':
            with open(output_path, 'w') as f:
                f.write(G.string())
        else:
            G.draw(output_path, format=output_format)
        
        return output_path
    
    def _group_nodes(self, graph: nx.DiGraph, grouping: str) -> Dict[str, List[int]]:
        """Group nodes by specified criteria"""
        groups = {'default': []}
        
        for node in graph.nodes():
            node_data = graph.nodes[node]
            group_key = 'default'
            
            if grouping == 'area':
                area = node_data.get('area', 'N/A')
                group_key = f"Area {area}"
            elif grouping == 'period':
                period = node_data.get('period_initial', node_data.get('periodo_iniziale', 'N/A'))
                group_key = f"Periodo {period}"
            elif grouping == 'phase':
                phase = node_data.get('phase_initial', node_data.get('fase_iniziale', 'N/A'))
                group_key = f"Fase {phase}"
            elif grouping == 'area_period':
                area = node_data.get('area', 'N/A')
                period = node_data.get('period_initial', node_data.get('periodo_iniziale', 'N/A'))
                group_key = f"Area {area} - {period}"
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(node)
        
        return groups
    
    def _add_subgraphs(self, G, groups: Dict[str, List[int]], grouping: str):
        """Add subgraphs for visual grouping"""
        for group_name, nodes in groups.items():
            if len(nodes) > 0:
                subgraph_name = f"cluster_{group_name.replace(' ', '_').replace('-', '_')}"
                
                # Determine subgraph style based on grouping
                if 'Area' in group_name:
                    area = group_name.split()[1] if len(group_name.split()) > 1 else 'A'
                    color = self.area_colors.get(area, '#F0F0F0')
                    style = 'filled,rounded'
                elif 'Periodo' in group_name:
                    color = '#FFF8DC'  # Light yellow for periods
                    style = 'filled,dashed'
                elif 'Fase' in group_name:
                    color = '#F0F8FF'  # Light blue for phases
                    style = 'filled,dotted'
                else:
                    color = '#F5F5F5'
                    style = 'filled'
                
                # Create subgraph
                subgraph = G.add_subgraph(
                    nodes,
                    name=subgraph_name,
                    label=group_name,
                    style=style,
                    color='gray',
                    fillcolor=color,
                    fontsize='12',
                    fontname='Arial Bold'
                )
    
    def _add_nodes_to_graph(self, G, graph: nx.DiGraph, grouping: str):
        """Add nodes to Graphviz graph with appropriate styling"""
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            # Create node label
            label = f"US {node}"
            
            # Add additional info to label
            description = node_data.get('description', node_data.get('d_stratigrafica', ''))
            if description:
                # Truncate long descriptions
                desc_short = description[:30] + '...' if len(description) > 30 else description
                label += f"\\n{desc_short}"
            
            # Add area info
            area = node_data.get('area', '')
            if area:
                label += f"\\nArea: {area}"
            
            # Add dating info
            period = node_data.get('period_initial', node_data.get('periodo_iniziale', ''))
            if period:
                label += f"\\n{period}"
            
            # Determine node styling
            area = node_data.get('area', 'A')
            period = node_data.get('period_initial', node_data.get('periodo_iniziale', ''))
            
            # Node color based on area
            fillcolor = self.area_colors.get(area, '#E8F4FD')
            
            # Node shape based on period
            shape = self.period_shapes.get(period, 'box')
            
            # Formation type affects border
            formation = node_data.get('formation', node_data.get('formazione', ''))
            if formation == 'Naturale':
                style = 'filled,dashed'
                color = 'green'
            elif formation == 'Antropica':
                style = 'filled,solid'
                color = 'blue'
            else:
                style = 'filled'
                color = 'black'
            
            # Add node to graph
            G.add_node(
                node,
                label=label,
                shape=shape,
                style=style,
                fillcolor=fillcolor,
                color=color,
                fontcolor='black'
            )
    
    def _add_edges_to_graph(self, G, graph: nx.DiGraph):
        """Add edges with proper styling based on relationship type"""
        for source, target in graph.edges():
            edge_data = graph.get_edge_data(source, target)
            relationship = edge_data.get('relationship', 'sopra')
            certainty = edge_data.get('certainty', 'certain')
            
            # Get relationship style
            rel_style = self.relationship_styles.get(relationship, self.relationship_styles['sopra'])
            
            # Modify style based on certainty
            if certainty in ['probabile', 'probable']:
                style = 'dashed'
                alpha = '0.7'
            elif certainty in ['dubbia', 'doubtful']:
                style = 'dotted'
                alpha = '0.5'
            elif certainty in ['ipotetica', 'hypothetical']:
                style = 'dotted'
                alpha = '0.3'
            else:
                style = rel_style['style']
                alpha = '1.0'
            
            # Create edge label
            label = relationship
            if certainty != 'certain' and certainty != 'certa':
                label += f"\\n({certainty})"
            
            # Add edge
            G.add_edge(
                source,
                target,
                label=label,
                color=rel_style['color'],
                style=style,
                arrowhead=rel_style['arrowhead'],
                fontcolor=rel_style['color'],
                penwidth='2'
            )
    
    def create_temporal_matrix(self, graph: nx.DiGraph, output_path: Optional[str] = None) -> str:
        """
        Create Harris Matrix with temporal/chronological ordering
        Groups by periods and phases with hierarchical display
        """
        try:
            import pygraphviz as pgv
        except ImportError:
            raise ImportError("pygraphviz is required")
        
        # Create graph with temporal layout
        G = pgv.AGraph(directed=True, strict=False)
        
        # Temporal layout attributes
        G.graph_attr.update({
            'rankdir': 'TB',
            'splines': 'ortho',
            'ranksep': '2.0',
            'nodesep': '1.0',
            'concentrate': 'true',
            'compound': 'true'
        })
        
        # Group by periods and phases
        temporal_groups = {}
        for node in graph.nodes():
            node_data = graph.nodes[node]
            period = node_data.get('periodo_iniziale', 'Sconosciuto')
            phase = node_data.get('fase_iniziale', '0')
            
            key = f"{period}_Fase_{phase}"
            if key not in temporal_groups:
                temporal_groups[key] = []
            temporal_groups[key].append(node)
        
        # Create subgraphs for each temporal group
        for group_name, nodes in temporal_groups.items():
            if nodes:
                period, phase = group_name.split('_Fase_')
                subgraph_name = f"cluster_{group_name}"
                
                G.add_subgraph(
                    nodes,
                    name=subgraph_name,
                    label=f"{period}\\nFase {phase}",
                    style='filled,rounded',
                    fillcolor='lightgray',
                    fontsize='14'
                )
        
        # Add nodes and edges
        self._add_nodes_to_graph(G, graph, 'period')
        self._add_edges_to_graph(G, graph)
        
        G.layout(prog='dot')
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.png')
        
        G.draw(output_path, format='png')
        return output_path
    
    def export_multiple_formats(self, graph: nx.DiGraph, base_filename: str, 
                               grouping: str = 'area') -> Dict[str, str]:
        """Export Harris Matrix in multiple formats"""
        exports = {}
        
        formats = ['png', 'svg', 'pdf', 'dot']
        
        for fmt in formats:
            try:
                output_path = f"{base_filename}_{grouping}.{fmt}"
                self.create_graphviz_matrix(graph, grouping, fmt, output_path)
                exports[fmt] = output_path
            except Exception as e:
                print(f"Failed to export {fmt}: {e}")
        
        return exports
    
    def create_relationship_legend(self, output_path: Optional[str] = None) -> str:
        """Create a legend showing all relationship types and their visual styles"""
        try:
            import pygraphviz as pgv
        except ImportError:
            raise ImportError("pygraphviz is required")
        
        G = pgv.AGraph(directed=True)
        
        G.graph_attr.update({
            'rankdir': 'LR',
            'bgcolor': 'white',
            'label': 'Legenda Relazioni Stratigrafiche',
            'fontsize': '16',
            'fontname': 'Arial Bold'
        })
        
        # Create example nodes
        for i, (rel_type, style) in enumerate(self.relationship_styles.items()):
            if rel_type in ['copre', 'taglia', 'riempie', 'uguale a', 'si lega a', 'si appoggia']:
                # Create two nodes for each relationship
                node1 = f"US_{i*2+1}"
                node2 = f"US_{i*2+2}"
                
                G.add_node(node1, label=f"US {i*2+1}", shape='box', style='filled', fillcolor='lightblue')
                G.add_node(node2, label=f"US {i*2+2}", shape='box', style='filled', fillcolor='lightblue')
                
                G.add_edge(
                    node1, node2,
                    label=rel_type,
                    color=style['color'],
                    style=style['style'],
                    arrowhead=style['arrowhead'],
                    fontcolor=style['color']
                )
        
        G.layout(prog='dot')
        
        if output_path is None:
            output_path = tempfile.mktemp(suffix='_legend.png')
        
        G.draw(output_path, format='png')
        return output_path
    
    def analyze_matrix_statistics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze Harris Matrix and provide statistics"""
        stats = {
            'total_nodes': len(graph.nodes()),
            'total_edges': len(graph.edges()),
            'is_dag': nx.is_directed_acyclic_graph(graph),
            'weakly_connected_components': nx.number_weakly_connected_components(graph),
            'relationship_types': {},
            'areas': set(),
            'periods': set(),
            'phases': set()
        }
        
        # Analyze relationships
        for source, target in graph.edges():
            edge_data = graph.get_edge_data(source, target)
            rel_type = edge_data.get('relationship', 'sopra')
            
            if rel_type not in stats['relationship_types']:
                stats['relationship_types'][rel_type] = 0
            stats['relationship_types'][rel_type] += 1
        
        # Analyze node attributes
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            area = node_data.get('area', '')
            if area:
                stats['areas'].add(area)
            
            period = node_data.get('periodo_iniziale', '')
            if period:
                stats['periods'].add(period)
            
            phase = node_data.get('fase_iniziale', '')
            if phase:
                stats['phases'].add(phase)
        
        # Convert sets to lists for JSON serialization
        stats['areas'] = list(stats['areas'])
        stats['periods'] = list(stats['periods'])
        stats['phases'] = list(stats['phases'])
        
        return stats