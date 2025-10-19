"""
Harris Matrix visualization and rendering
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

class MatrixVisualizer:
    """
    Visualizes Harris Matrix using different rendering methods
    """
    
    def __init__(self):
        self.default_style = {
            'node_width': 120,
            'node_height': 80,
            'node_spacing_x': 150,
            'node_spacing_y': 100,
            'font_size': 10,
            'colors': {
                'us': '#E8F4FD',
                'border': '#2E86AB',
                'text': '#000000',
                'relationship': '#5C7CFA'
            }
        }
    
    def render_matplotlib(self, graph: nx.DiGraph, levels: Dict[int, List[int]], 
                         output_path: Optional[str] = None, style: Optional[Dict] = None) -> str:
        """
        Render Harris Matrix using matplotlib
        
        Args:
            graph: NetworkX graph
            levels: Matrix levels from generator
            output_path: Optional file path to save
            style: Optional style overrides
            
        Returns:
            Base64 encoded image string
        """
        if style:
            current_style = {**self.default_style, **style}
        else:
            current_style = self.default_style
        
        # Calculate figure size
        max_nodes_per_level = max([len(nodes) for nodes in levels.values()]) if levels else 1
        fig_width = max(12, max_nodes_per_level * current_style['node_spacing_x'] / 100)
        fig_height = max(8, len(levels) * current_style['node_spacing_y'] / 100)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, fig_width * 100)
        ax.set_ylim(0, fig_height * 100)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Position nodes
        node_positions = {}
        y_offset = fig_height * 100 - current_style['node_spacing_y']
        
        for level, us_list in levels.items():
            x_start = (fig_width * 100 - len(us_list) * current_style['node_spacing_x']) / 2
            
            for i, us in enumerate(us_list):
                x = x_start + i * current_style['node_spacing_x']
                y = y_offset - level * current_style['node_spacing_y']
                node_positions[us] = (x, y)
        
        # Draw relationships (edges)
        for us_from, us_to in graph.edges():
            if us_from in node_positions and us_to in node_positions:
                x1, y1 = node_positions[us_from]
                x2, y2 = node_positions[us_to]
                
                # Draw arrow
                ax.annotate('', xy=(x2, y2 + current_style['node_height']/2), 
                           xytext=(x1, y1 - current_style['node_height']/2),
                           arrowprops=dict(arrowstyle='->', color=current_style['colors']['relationship'], lw=2))
        
        # Draw nodes
        for us, (x, y) in node_positions.items():
            # Get node data
            node_data = graph.nodes[us] if us in graph.nodes else {}
            
            # Draw rectangle
            rect = patches.Rectangle(
                (x - current_style['node_width']/2, y - current_style['node_height']/2),
                current_style['node_width'], current_style['node_height'],
                linewidth=2, edgecolor=current_style['colors']['border'],
                facecolor=current_style['colors']['us']
            )
            ax.add_patch(rect)
            
            # Add text
            label = f"US {us}"
            ax.text(x, y + 10, label, ha='center', va='center', 
                   fontsize=current_style['font_size'], fontweight='bold',
                   color=current_style['colors']['text'])
            
            # Add description if available
            if 'description' in node_data and node_data['description']:
                desc = node_data['description'][:20] + "..." if len(node_data['description']) > 20 else node_data['description']
                ax.text(x, y - 10, desc, ha='center', va='center', 
                       fontsize=current_style['font_size']-2,
                       color=current_style['colors']['text'])
        
        # Add title
        ax.text(fig_width * 50, fig_height * 100 - 30, 'Harris Matrix', 
               ha='center', va='center', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Save or return as base64
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        buffer.close()
        plt.close()
        
        return image_base64
    
    def render_graphviz(self, graph: nx.DiGraph, output_path: Optional[str] = None) -> str:
        """
        Render Harris Matrix using Graphviz for better layouts
        """
        try:
            import pygraphviz as pgv
            
            # Create Graphviz graph
            A = nx.nx_agraph.to_agraph(graph)
            
            # Set graph attributes
            A.graph_attr.update(rankdir='TB', splines='true', overlap='false')
            A.node_attr.update(shape='box', style='filled', fillcolor='lightblue')
            A.edge_attr.update(color='blue')
            
            # Customize nodes
            for node in A.nodes():
                node_data = graph.nodes[int(node)] if int(node) in graph.nodes else {}
                label = f"US {node}"
                if 'description' in node_data and node_data['description']:
                    desc = node_data['description'][:30]
                    label += f"\\n{desc}"
                node.attr['label'] = label
            
            # Layout and render
            A.layout(prog='dot')
            
            if output_path:
                A.draw(output_path)
            
            # Return as base64
            png_data = A.draw(format='png')
            return base64.b64encode(png_data).decode()
            
        except ImportError:
            # Fallback to matplotlib
            return self.render_matplotlib(graph, {}, output_path)
    
    def create_interactive_html(self, graph: nx.DiGraph, levels: Dict[int, List[int]]) -> str:
        """
        Create interactive HTML visualization using D3.js or similar
        """
        
        # Prepare data for JavaScript
        nodes = []
        links = []
        
        # Create nodes
        for us in graph.nodes():
            node_data = graph.nodes[us]
            nodes.append({
                'id': us,
                'label': f"US {us}",
                'description': node_data.get('description', ''),
                'interpretation': node_data.get('interpretation', ''),
                'area': node_data.get('area', ''),
                'formation': node_data.get('formation', '')
            })
        
        # Create links
        for us_from, us_to in graph.edges():
            edge_data = graph.get_edge_data(us_from, us_to)
            links.append({
                'source': us_from,
                'target': us_to,
                'relationship': edge_data.get('relationship', 'sopra'),
                'certainty': edge_data.get('certainty', 'certain')
            })
        
        html_template = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Harris Matrix - Interactive</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                .node {{ fill: #E8F4FD; stroke: #2E86AB; stroke-width: 2px; }}
                .link {{ stroke: #5C7CFA; stroke-width: 2px; marker-end: url(#arrowhead); }}
                .node-label {{ font-family: Arial; font-size: 12px; text-anchor: middle; }}
                .tooltip {{ 
                    position: absolute; background: white; padding: 10px; 
                    border: 1px solid #ccc; border-radius: 5px; pointer-events: none;
                }}
            </style>
        </head>
        <body>
            <h1>Harris Matrix</h1>
            <div id="matrix"></div>
            <div class="tooltip" style="opacity: 0;"></div>
            
            <script>
                const nodes = {nodes};
                const links = {links};
                
                const width = 1200;
                const height = 800;
                
                const svg = d3.select("#matrix")
                    .append("svg")
                    .attr("width", width)
                    .attr("height", height);
                
                // Define arrowhead marker
                svg.append("defs").append("marker")
                    .attr("id", "arrowhead")
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 15)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "#5C7CFA");
                
                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-300))
                    .force("center", d3.forceCenter(width / 2, height / 2));
                
                const link = svg.append("g")
                    .selectAll("line")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link");
                
                const node = svg.append("g")
                    .selectAll("g")
                    .data(nodes)
                    .enter().append("g")
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                node.append("rect")
                    .attr("class", "node")
                    .attr("width", 80)
                    .attr("height", 50)
                    .attr("x", -40)
                    .attr("y", -25);
                
                node.append("text")
                    .attr("class", "node-label")
                    .attr("dy", "0.35em")
                    .text(d => d.label);
                
                // Tooltip
                const tooltip = d3.select(".tooltip");
                
                node.on("mouseover", function(event, d) {{
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(`
                        <strong>${{d.label}}</strong><br/>
                        Description: ${{d.description}}<br/>
                        Area: ${{d.area}}<br/>
                        Formation: ${{d.formation}}
                    `)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function(d) {{
                    tooltip.transition().duration(500).style("opacity", 0);
                }});
                
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                }});
                
                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}
                
                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}
                
                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}
            </script>
        </body>
        </html>
        '''
        
        return html_template
    
    def export_to_formats(self, graph: nx.DiGraph, levels: Dict[int, List[int]], 
                         base_filename: str) -> Dict[str, str]:
        """
        Export Harris Matrix to multiple formats
        
        Returns:
            Dictionary mapping format to file path
        """
        exports = {}
        
        # PNG
        png_path = f"{base_filename}.png"
        self.render_matplotlib(graph, levels, png_path)
        exports['png'] = png_path
        
        # SVG (via matplotlib)
        svg_path = f"{base_filename}.svg"
        self.render_matplotlib(graph, levels, svg_path)
        exports['svg'] = svg_path
        
        # HTML Interactive
        html_path = f"{base_filename}.html"
        html_content = self.create_interactive_html(graph, levels)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        exports['html'] = html_path
        
        # DOT (Graphviz)
        try:
            dot_path = f"{base_filename}.dot"
            nx.drawing.nx_pydot.write_dot(graph, dot_path)
            exports['dot'] = dot_path
        except:
            pass
        
        return exports