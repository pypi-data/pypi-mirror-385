#!/usr/bin/env python3
"""
Stratigraphic paradox validator for PyArchInit-Mini
Validates stratigraphic relationships to detect logical paradoxes
"""

from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
from ..utils.exceptions import ValidationError

class StratigraphicValidator:
    """
    Validates stratigraphic relationships to detect paradoxes
    """
    
    # Relationship types and their meanings
    RELATIONSHIP_TYPES = {
        'copre': 'covers',
        'coperto da': 'covered_by',
        'taglia': 'cuts',
        'tagliato da': 'cut_by',
        'riempie': 'fills',
        'riempito da': 'filled_by',
        'si lega a': 'bonded_to',
        'si appoggia a': 'abuts',
        'gli si appoggia': 'abutted_by',
        'uguale a': 'equals',
        'contemporaneo a': 'contemporary_with'
    }
    
    # Inverse relationships
    INVERSE_RELATIONS = {
        'copre': 'coperto da',
        'coperto da': 'copre',
        'taglia': 'tagliato da',
        'tagliato da': 'taglia',
        'riempie': 'riempito da',
        'riempito da': 'riempie',
        'si lega a': 'si lega a',
        'si appoggia a': 'gli si appoggia',
        'gli si appoggia': 'si appoggia a',
        'uguale a': 'uguale a',
        'contemporaneo a': 'contemporaneo a'
    }
    
    # Paradoxical relationship combinations
    PARADOX_RULES = [
        # A unit cannot both cover and be covered by the same unit
        ('copre', 'coperto da'),
        ('taglia', 'tagliato da'),
        ('riempie', 'riempito da'),
        
        # A cut cannot fill (cuts are negative actions)
        # This is checked based on unit interpretation
        
        # A unit cannot be both earlier and later than another
        ('copre', 'tagliato da'),  # If A covers B, A cannot be cut by B
        ('taglia', 'coperto da'),  # If A cuts B, A cannot be covered by B
        ('riempie', 'tagliato da'),  # If A fills B, A cannot be cut by B
        
        # Contemporary/equal units cannot have stratigraphic relationships
        ('uguale a', 'copre'),
        ('uguale a', 'coperto da'),
        ('uguale a', 'taglia'),
        ('uguale a', 'tagliato da'),
        ('contemporaneo a', 'copre'),
        ('contemporaneo a', 'coperto da'),
    ]
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.relationships = {}
        self.units = {}
        
    def add_unit(self, us_number: int, unit_data: Dict) -> None:
        """Add a stratigraphic unit"""
        self.units[us_number] = unit_data
        self.graph.add_node(us_number)
        
    def add_relationship(self, from_us: int, to_us: int, rel_type: str) -> None:
        """Add a stratigraphic relationship"""
        if from_us not in self.relationships:
            self.relationships[from_us] = {}
        if to_us not in self.relationships[from_us]:
            self.relationships[from_us][to_us] = []
            
        self.relationships[from_us][to_us].append(rel_type)
        
        # Add edge for sequence validation
        if rel_type in ['copre', 'taglia', 'riempie']:
            self.graph.add_edge(from_us, to_us)
        elif rel_type in ['coperto da', 'tagliato da', 'riempito da']:
            self.graph.add_edge(to_us, from_us)
            
    def parse_relationships(self, us_number: int, rapporti_text: str) -> List[Tuple[str, int]]:
        """Parse relationship text into structured format"""
        if not rapporti_text:
            return []
            
        relationships = []
        parts = rapporti_text.split(';')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Parse relationship type and target US
            for rel_type in self.RELATIONSHIP_TYPES.keys():
                if part.lower().startswith(rel_type):
                    # Extract US numbers after relationship type
                    remainder = part[len(rel_type):].strip()
                    # Split by comma for multiple targets
                    targets = remainder.split(',')
                    for target in targets:
                        target = target.strip()
                        try:
                            target_us = int(target)
                            relationships.append((rel_type, target_us))
                        except ValueError:
                            # Skip if not a valid number
                            pass
                    break
                    
        return relationships
        
    def validate_unit_relationships(self, us_number: int) -> List[str]:
        """Validate relationships for a single unit"""
        errors = []
        
        if us_number not in self.relationships:
            return errors
            
        unit_data = self.units.get(us_number, {})
        
        # Check for direct paradoxes
        for target_us, rel_types in self.relationships[us_number].items():
            # Check for contradictory relationships with same target
            for i, rel1 in enumerate(rel_types):
                for rel2 in rel_types[i+1:]:
                    if self._is_paradox(rel1, rel2):
                        errors.append(
                            f"US {us_number}: Paradox - cannot both '{rel1}' and '{rel2}' US {target_us}"
                        )
                        
            # Check for inverse relationships
            if target_us in self.relationships:
                target_rels = self.relationships[target_us].get(us_number, [])
                for rel1 in rel_types:
                    for rel2 in target_rels:
                        if self._is_inverse_paradox(rel1, rel2):
                            errors.append(
                                f"US {us_number} → {target_us}: Paradox - '{rel1}' conflicts with "
                                f"US {target_us} '{rel2}' US {us_number}"
                            )
                            
        # Check interpretation-based paradoxes
        if unit_data.get('d_interpretativa'):
            interp = unit_data['d_interpretativa'].lower()
            if any(word in interp for word in ['taglio', 'fossa', 'buca', 'cut']):
                # This is a cut - it cannot fill
                for target_us, rel_types in self.relationships[us_number].items():
                    if 'riempie' in rel_types:
                        errors.append(
                            f"US {us_number}: Paradox - a cut/fossa cannot fill (riempie) another unit"
                        )
                        
        return errors
        
    def _is_paradox(self, rel1: str, rel2: str) -> bool:
        """Check if two relationships form a paradox"""
        for paradox_pair in self.PARADOX_RULES:
            if (rel1, rel2) == paradox_pair or (rel2, rel1) == paradox_pair:
                return True
        return False
        
    def _is_inverse_paradox(self, rel1: str, rel2: str) -> bool:
        """Check if relationship conflicts with its inverse"""
        # If A covers B, then B should be covered by A
        expected_inverse = self.INVERSE_RELATIONS.get(rel1)
        if expected_inverse and rel2 != expected_inverse:
            # Check if they have incompatible relationships
            if (rel1 in ['copre', 'taglia', 'riempie'] and 
                rel2 in ['copre', 'taglia', 'riempie']):
                return True
        return False
        
    def validate_sequence(self) -> List[str]:
        """Validate the entire stratigraphic sequence for cycles"""
        errors = []
        
        # Check for cycles (temporal paradoxes)
        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                cycle_str = " → ".join(str(us) for us in cycle + [cycle[0]])
                errors.append(f"Temporal paradox (cycle): {cycle_str}")
        except nx.NetworkXError:
            pass
            
        return errors
        
    def validate_all(self, us_list: List[Dict]) -> List[str]:
        """Validate all stratigraphic relationships"""
        errors = []
        
        # Reset validator
        self.graph.clear()
        self.relationships.clear()
        self.units.clear()
        
        # Build relationship graph
        for us_data in us_list:
            us_number = us_data.get('us')
            if not us_number:
                continue
                
            self.add_unit(us_number, us_data)
            
            # Parse and add relationships
            rapporti = us_data.get('rapporti', '')
            if rapporti:
                relationships = self.parse_relationships(us_number, rapporti)
                for rel_type, target_us in relationships:
                    self.add_relationship(us_number, target_us, rel_type)
                    
        # Validate each unit
        for us_number in self.units:
            unit_errors = self.validate_unit_relationships(us_number)
            errors.extend(unit_errors)
            
        # Validate overall sequence
        sequence_errors = self.validate_sequence()
        errors.extend(sequence_errors)
        
        return errors
        
    def get_validation_report(self, us_list: List[Dict]) -> Dict:
        """Get detailed validation report"""
        errors = self.validate_all(us_list)
        
        report = {
            'valid': len(errors) == 0,
            'error_count': len(errors),
            'errors': errors,
            'units_checked': len(self.units),
            'relationships_found': sum(
                len(targets) for targets in self.relationships.values()
            )
        }
        
        return report
    
    def generate_relationship_fixes(self, us_list: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Generate fixes for missing reciprocal relationships and missing US
        
        Returns:
            Dictionary with 'updates' and 'creates' lists
        """
        fixes = {
            'updates': [],  # US records to update with missing reciprocal relationships
            'creates': []   # New US records to create
        }
        
        # Build a map of existing US numbers
        existing_us = {}
        for us_data in us_list:
            key = (us_data['sito'], us_data.get('area', ''), us_data['us'])
            existing_us[key] = us_data
        
        # Track all referenced US that don't exist
        missing_us = set()
        
        # Check each US for missing reciprocal relationships
        for us_data in us_list:
            us_number = us_data['us']
            site = us_data['sito']
            area = us_data.get('area', '')
            rapporti = us_data.get('rapporti', '')
            
            if not rapporti:
                continue
                
            relationships = self.parse_relationships(us_number, rapporti)
            
            for rel_type, target_us in relationships:
                target_key = (site, area, target_us)
                
                # Check if target US exists
                if target_key not in existing_us:
                    missing_us.add((site, area, target_us, us_number, rel_type))
                    continue
                
                # Check if reciprocal relationship exists
                inverse_rel = self.INVERSE_RELATIONS.get(rel_type)
                if not inverse_rel:
                    continue
                    
                target_data = existing_us[target_key]
                target_rapporti = target_data.get('rapporti', '')
                
                # Check if inverse relationship already exists
                target_relationships = self.parse_relationships(target_us, target_rapporti)
                has_inverse = any(
                    rel == inverse_rel and target == us_number 
                    for rel, target in target_relationships
                )
                
                if not has_inverse:
                    # Generate fix to add reciprocal relationship
                    new_rapporti = target_rapporti
                    if new_rapporti and not new_rapporti.endswith(';'):
                        new_rapporti += '; '
                    new_rapporti += f"{inverse_rel} {us_number}"
                    
                    fixes['updates'].append({
                        'us_id': target_data.get('id_us'),
                        'sito': site,
                        'area': area,
                        'us': target_us,
                        'field': 'rapporti',
                        'old_value': target_rapporti,
                        'new_value': new_rapporti.strip(),
                        'reason': f"Aggiunta relazione reciproca: US {us_number} {rel_type} {target_us}"
                    })
        
        # Create missing US records
        for site, area, us_num, source_us, rel_type in missing_us:
            # Generate inverse relationship
            inverse_rel = self.INVERSE_RELATIONS.get(rel_type, '')
            
            fixes['creates'].append({
                'sito': site,
                'area': area if area else None,
                'us': us_num,
                'unita_tipo': 'US',
                'd_stratigrafica': f'US creata automaticamente (riferita da US {source_us})',
                'd_interpretativa': 'Da verificare',
                'rapporti': f"{inverse_rel} {source_us}" if inverse_rel else '',
                'scavato': 'No',
                'anno_scavo': None,
                'created_from': source_us,
                'reason': f"US riferita da US {source_us} con relazione '{rel_type}'"
            })
        
        return fixes