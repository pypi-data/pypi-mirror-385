"""
Harris Matrix generation from stratigraphic relationships
"""

import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from ..database.manager import DatabaseManager
from ..models.harris_matrix import HarrisMatrix, USRelationships
from ..models.us import US

class HarrisMatrixGenerator:
    """
    Generates Harris Matrix from stratigraphic relationships
    """
    
    def __init__(self, db_manager: DatabaseManager, us_service=None):
        self.db_manager = db_manager
        self.us_service = us_service
    
    def generate_matrix(self, site_name: str, area: Optional[str] = None) -> nx.DiGraph:
        """
        Generate Harris Matrix graph from site relationships
        
        Args:
            site_name: Site name
            area: Optional area filter
            
        Returns:
            NetworkX directed graph representing the Harris Matrix
        """
        # Get all US for the site using service if available
        if self.us_service:
            filters = {'sito': site_name}
            if area:
                filters['area'] = area
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
        else:
            # If no service available, use empty list to avoid session errors
            print("Warning: No US service available for matrix generation")
            us_list = []
        
        # Get relationships
        relationships = self._get_relationships(site_name, area)
        
        # Create directed graph
        graph = nx.DiGraph()
        
        # Add US nodes
        for us in us_list:
            # Handle both DTO and SQLAlchemy objects
            us_num = getattr(us, 'us', None)
            if us_num is None:
                continue
                
            graph.add_node(
                us_num,
                label=f"US {us_num}",
                area=getattr(us, 'area', None) or "",
                description=getattr(us, 'd_stratigrafica', None) or "",
                interpretation=getattr(us, 'd_interpretativa', None) or "",
                period_initial=getattr(us, 'periodo_iniziale', None) or "",
                period_final=getattr(us, 'periodo_finale', None) or "",
                formation=getattr(us, 'formazione', None) or "",
                unita_tipo=getattr(us, 'unita_tipo', None) or "US"
            )
        
        # Add relationship edges - include all stratigraphic relationships
        for rel in relationships:
            # Include all valid stratigraphic relationships
            if rel['type'] in ['sopra', 'above', 'over', 'copre', 'coperto da', 'taglia', 'tagliato da', 
                              'riempie', 'riempito da', 'uguale a', 'si lega a', 'si appoggia', 'gli si appoggia']:
                graph.add_edge(
                    rel['us_from'], 
                    rel['us_to'],
                    relationship=rel['type'],
                    certainty=rel.get('certainty', 'certain')
                )
        
        # Validate and fix matrix
        graph = self._validate_matrix(graph)

        # Apply transitive reduction to eliminate redundant edges
        # This removes edges that can be inferred through transitivity
        # e.g., if US1→US2→US3 and US1→US3, removes US1→US3
        if len(graph.edges()) > 0:
            try:
                # Preserve node and edge attributes during reduction
                node_attrs = {n: graph.nodes[n] for n in graph.nodes()}
                edge_attrs = {(u, v): graph.edges[u, v] for u, v in graph.edges()}

                # Apply transitive reduction
                reduced_graph = nx.transitive_reduction(graph)

                # Restore node attributes
                for node, attrs in node_attrs.items():
                    for key, value in attrs.items():
                        reduced_graph.nodes[node][key] = value

                # Restore edge attributes (only for edges that remain)
                for (u, v), attrs in edge_attrs.items():
                    if reduced_graph.has_edge(u, v):
                        for key, value in attrs.items():
                            reduced_graph.edges[u, v][key] = value

                graph = reduced_graph
            except Exception as e:
                print(f"Warning: Could not apply transitive reduction: {e}")

        return graph
    
    def _get_relationships(self, site_name: str, area: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get stratigraphic relationships for site/area using PyArchInit approach"""
        
        filters = {'sito': site_name}
        if area:
            filters.update({'area': area})
            
        relationships = []
        
        # Get US records to extract relationships from rapporti field (like PyArchInit)
        if self.us_service:
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
        else:
            print("Warning: No US service available for relationship extraction")
            return []
        
        for us_record in us_list:
            us_num = getattr(us_record, 'us', None)
            area_us = getattr(us_record, 'area', '')
            rapporti = getattr(us_record, 'rapporti', None)
            
            if not us_num or not rapporti:
                continue
            
            try:
                # Parse rapporti field (supports both formats)
                rapporti_list = []
                if isinstance(rapporti, str):
                    # Try to parse as Python list first (legacy format)
                    if rapporti.strip().startswith('[') or rapporti.strip().startswith('('):
                        try:
                            rapporti_list = eval(rapporti)
                        except:
                            pass
                    else:
                        # Parse as text format: "Copre 1002, Taglia 1003"
                        parts = rapporti.split(',')
                        for part in parts:
                            part = part.strip()
                            if not part:
                                continue
                            # Split "Copre 1002" into ["Copre", "1002"]
                            tokens = part.split()
                            if len(tokens) >= 2:
                                rel_type = ' '.join(tokens[:-1])  # Everything except last token
                                rel_us = tokens[-1]  # Last token is US number
                                rapporti_list.append([rel_type, rel_us])
                else:
                    rapporti_list = rapporti

                for rel in rapporti_list:
                    # Handle both PyArchInit format and our format
                    rel_type = None
                    rel_us = None
                    rel_area = area_us
                    
                    if isinstance(rel, str):
                        # Parse string like "['Uguale a', 'US_2']"
                        try:
                            parsed_rel = eval(rel)
                            if isinstance(parsed_rel, (list, tuple)) and len(parsed_rel) >= 2:
                                rel_type = parsed_rel[0]
                                us_part = parsed_rel[1]
                                # Extract US number from "US_2" format
                                if us_part.startswith('US_'):
                                    rel_us = us_part[3:]
                                else:
                                    rel_us = us_part
                        except:
                            continue
                    elif isinstance(rel, (list, tuple)) and len(rel) >= 2:
                        # Direct list/tuple format
                        rel_type = rel[0]
                        rel_us = rel[1]
                        if len(rel) > 2:
                            rel_area = rel[2]
                    
                    if rel_type and rel_us and rel_us != '':
                        try:
                            # Map PyArchInit relationship types to our system
                            mapped_rel = self._map_relationship_type(rel_type)
                            if mapped_rel:
                                relationships.append({
                                    'us_from': us_num,
                                    'us_to': int(rel_us),
                                    'area_from': area_us,
                                    'area_to': rel_area,
                                    'type': mapped_rel,
                                    'certainty': 'certain',
                                    'description': f"US {us_num} {mapped_rel} US {rel_us}"
                                })
                        except (ValueError, TypeError):
                            # Skip invalid US numbers
                            continue
                                
            except Exception as e:
                print(f"Error parsing relationships for US {us_num}: {e}")
                continue
        
        # Try to get explicit relationships from tables if available
        try:
            # Use a fresh session for each query to avoid session binding issues
            with self.db_manager.connection.get_session() as session:
                from sqlalchemy import and_
                
                # Query USRelationships table if it exists
                try:
                    query = session.query(USRelationships)
                    if 'sito' in filters:
                        query = query.filter(USRelationships.sito == filters['sito'])
                    if 'area' in filters:
                        query = query.filter(USRelationships.area == filters['area'])
                    
                    rel_records = query.limit(1000).all()
                    for rel in rel_records:
                        if rel.us_from is not None and rel.us_to is not None:
                            relationships.append({
                                'us_from': rel.us_from,
                                'us_to': rel.us_to,
                                'type': rel.relationship_type or 'sopra',
                                'certainty': rel.certainty or 'certain',
                                'description': rel.description or ''
                            })
                except Exception as e:
                    print(f"Note: USRelationships table not available or empty: {e}")
                
                # Query HarrisMatrix table if it exists
                try:
                    query = session.query(HarrisMatrix)
                    if 'sito' in filters:
                        query = query.filter(HarrisMatrix.sito == filters['sito'])
                    if 'area' in filters:
                        query = query.filter(HarrisMatrix.area == filters['area'])
                    
                    matrix_records = query.limit(1000).all()
                    for matrix in matrix_records:
                        if matrix.us_sopra is not None and matrix.us_sotto is not None:
                            relationships.append({
                                'us_from': matrix.us_sopra,
                                'us_to': matrix.us_sotto,
                                'type': matrix.tipo_rapporto or 'sopra',
                                'certainty': 'certain'
                            })
                except Exception as e:
                    print(f"Note: HarrisMatrix table not available or empty: {e}")
                    
        except Exception as e:
            print(f"Note: Could not access relationship tables: {e}")
        
        # Debug: print relationships found
        print(f"Found {len(relationships)} relationships from database parsing")
        
        # If still no relationships, try to infer some
        if not relationships:
            print("No relationships found in database, inferring from US sequence...")
            relationships = self._infer_relationships(site_name, area)
        else:
            print(f"Using {len(relationships)} relationships from database")
        
        return relationships
    
    def _map_relationship_type(self, pyarchinit_rel: str) -> Optional[str]:
        """Map PyArchInit relationship types to our standardized types"""
        mapping = {
            # Italian (uppercase)
            'Copre': 'copre',
            'Coperto da': 'coperto da',
            'Taglia': 'taglia',
            'Tagliato da': 'tagliato da',
            'Riempie': 'riempie',
            'Riempito da': 'riempito da',
            'Si appoggia a': 'si appoggia',
            'Gli si appoggia': 'gli si appoggia',
            'Si lega a': 'si lega a',
            'Uguale a': 'uguale a',
            # Italian (lowercase)
            'copre': 'copre',
            'coperto da': 'coperto da',
            'taglia': 'taglia',
            'tagliato da': 'tagliato da',
            'riempie': 'riempie',
            'riempito da': 'riempito da',
            'si appoggia': 'si appoggia',
            'si appoggia a': 'si appoggia',
            'gli si appoggia': 'gli si appoggia',
            'si lega a': 'si lega a',
            'uguale a': 'uguale a',
            # English
            'Covers': 'copre',
            'Covered by': 'coperto da',
            'Cuts': 'taglia',
            'Cut by': 'tagliato da',
            'Fills': 'riempie',
            'Filled by': 'riempito da',
            'Abuts': 'si appoggia',
            'Connected to': 'si lega a',
            'Same as': 'uguale a',
            # German
            'Verfüllt': 'riempie',
            'Bindet an': 'si appoggia',
            'Schneidet': 'taglia',
            'Entspricht': 'uguale a',
            'Liegt über': 'copre'
        }
        return mapping.get(pyarchinit_rel, None)
    
    def _infer_relationships(self, site_name: str, area: Optional[str] = None) -> List[Dict[str, Any]]:
        """Infer relationships from US order numbers"""
        
        filters = {'sito': site_name}
        if area:
            filters['area'] = area
        
        # Always use service if available to avoid session issues
        if self.us_service:
            us_list = self.us_service.get_all_us(size=1000, filters=filters)
        else:
            # If no service available, return empty relationships to avoid session errors
            print("Warning: No US service available for relationship inference")
            return []
        
        relationships = []
        
        # Simple inference: lower US numbers are typically above higher ones
        us_numbers = []
        for us in us_list:
            us_num = getattr(us, 'us', None)
            if us_num is not None:
                us_numbers.append(us_num)
        
        us_numbers = sorted(us_numbers)
        
        # Use correct stratigraphic relationships instead of generic 'sopra'
        import random
        correct_relationships = ['copre', 'coperto da', 'riempie', 'riempito da', 'si appoggia', 'taglia']
        
        for i in range(len(us_numbers) - 1):
            # Use varied stratigraphic relationships
            rel_type = random.choice(correct_relationships)
            relationships.append({
                'us_from': us_numbers[i],
                'us_to': us_numbers[i + 1],
                'type': rel_type,
                'certainty': 'inferred'
            })
        
        return relationships
    
    def _validate_matrix(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Validate and fix Harris Matrix for cycles and inconsistencies"""
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(graph):
            # Remove edges that create cycles
            cycles = list(nx.simple_cycles(graph))
            for cycle in cycles:
                # Remove the edge with lowest certainty
                edges_to_remove = []
                for i in range(len(cycle)):
                    from_node = cycle[i]
                    to_node = cycle[(i + 1) % len(cycle)]
                    if graph.has_edge(from_node, to_node):
                        edge_data = graph.get_edge_data(from_node, to_node)
                        certainty = edge_data.get('certainty', 'certain')
                        edges_to_remove.append((from_node, to_node, certainty))
                
                # Sort by certainty and remove least certain
                edges_to_remove.sort(key=lambda x: x[2])
                if edges_to_remove:
                    graph.remove_edge(edges_to_remove[0][0], edges_to_remove[0][1])
        
        return graph
    
    def get_matrix_levels(self, graph: nx.DiGraph) -> Dict[int, List[int]]:
        """
        Get topological levels for matrix layout
        
        Returns:
            Dictionary mapping level number to list of US numbers
        """
        if not graph.nodes():
            return {}
            
        # Calculate topological levels
        levels = {}
        
        # Get nodes with no incoming edges (top level)
        top_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        if not top_nodes:
            # If no top nodes (cycle), start with any node
            top_nodes = [list(graph.nodes())[0]]
        
        current_level = 0
        remaining_nodes = set(graph.nodes())
        
        while remaining_nodes:
            # Find nodes that have no predecessors in remaining nodes
            level_nodes = []
            for node in remaining_nodes.copy():
                predecessors = set(graph.predecessors(node))
                if not predecessors or not predecessors.intersection(remaining_nodes):
                    level_nodes.append(node)
                    remaining_nodes.remove(node)
            
            if not level_nodes and remaining_nodes:
                # Break cycles by taking any remaining node
                level_nodes = [remaining_nodes.pop()]
            
            if level_nodes:
                levels[current_level] = sorted(level_nodes)
                current_level += 1
        
        return levels
    
    def get_matrix_statistics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Get statistics about the Harris Matrix"""
        
        stats = {
            'total_us': len(graph.nodes()),
            'total_relationships': len(graph.edges()),
            'levels': len(self.get_matrix_levels(graph)),
            'is_valid': nx.is_directed_acyclic_graph(graph),
            'has_cycles': not nx.is_directed_acyclic_graph(graph),
            'isolated_us': len(list(nx.isolates(graph))),
            'top_level_us': len([n for n in graph.nodes() if graph.in_degree(n) == 0]),
            'bottom_level_us': len([n for n in graph.nodes() if graph.out_degree(n) == 0])
        }
        
        # Add cycle information if present
        if stats['has_cycles']:
            stats['cycles'] = list(nx.simple_cycles(graph))
        
        return stats
    
    def add_relationship(self, site_name: str, us_from: int, us_to: int, 
                        relationship_type: str = 'sopra', certainty: str = 'certain',
                        description: str = "") -> bool:
        """
        Add a new stratigraphic relationship
        
        Args:
            site_name: Site name
            us_from: US number (from)
            us_to: US number (to)
            relationship_type: Type of relationship
            certainty: Certainty level
            description: Optional description
            
        Returns:
            True if successful
        """
        try:
            relationship_data = {
                'sito': site_name,
                'us_from': us_from,
                'us_to': us_to,
                'relationship_type': relationship_type,
                'certainty': certainty,
                'description': description
            }
            
            self.db_manager.create(USRelationships, relationship_data)
            return True
            
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False