"""
AtomSpace Manager for OpenCog Integration
Manages the hypergraph knowledge representation for ERPNext data
"""

import frappe
from typing import Dict, Any, List, Optional


class AtomSpaceManager:
	"""
	Manages AtomSpace - OpenCog's hypergraph knowledge representation system
	Stores and reasons about ERPNext entities, relationships, and patterns
	"""

	def __init__(self):
		self.atoms = {}  # Simplified in-memory storage for atoms
		self.links = {}  # Stores relationships between atoms
		self.attention_values = {}  # STI (Short-Term Importance) and LTI (Long-Term Importance)

	def add_node(self, node_type: str, node_name: str, truth_value: Optional[Dict] = None) -> str:
		"""
		Add a node to the AtomSpace
		
		Args:
			node_type: Type of node (e.g., 'ConceptNode', 'PredicateNode')
			node_name: Name/identifier of the node
			truth_value: Optional truth value {strength, confidence}
			
		Returns:
			Unique identifier for the created node
		"""
		atom_id = f"{node_type}:{node_name}"
		
		if atom_id not in self.atoms:
			self.atoms[atom_id] = {
				"type": node_type,
				"name": node_name,
				"truth_value": truth_value or {"strength": 1.0, "confidence": 1.0},
				"created_at": frappe.utils.now(),
			}
			
			# Initialize attention values
			self.attention_values[atom_id] = {
				"sti": 0,  # Short-term importance
				"lti": 0,  # Long-term importance
				"vlti": False,  # Very long-term importance flag
			}
			
		return atom_id

	def add_link(
		self, link_type: str, outgoing: List[str], truth_value: Optional[Dict] = None
	) -> str:
		"""
		Add a link (relationship) between atoms
		
		Args:
			link_type: Type of link (e.g., 'InheritanceLink', 'EvaluationLink')
			outgoing: List of atom IDs that this link connects
			truth_value: Optional truth value
			
		Returns:
			Unique identifier for the created link
		"""
		link_id = f"{link_type}:{':'.join(outgoing)}"
		
		if link_id not in self.links:
			self.links[link_id] = {
				"type": link_type,
				"outgoing": outgoing,
				"truth_value": truth_value or {"strength": 1.0, "confidence": 1.0},
				"created_at": frappe.utils.now(),
			}
			
		return link_id

	def get_atom(self, atom_id: str) -> Optional[Dict]:
		"""Get atom details by ID"""
		return self.atoms.get(atom_id) or self.links.get(atom_id)

	def update_attention(self, atom_id: str, sti_delta: int = 0, lti_delta: int = 0):
		"""
		Update attention values for an atom
		
		Args:
			atom_id: Atom identifier
			sti_delta: Change in short-term importance
			lti_delta: Change in long-term importance
		"""
		if atom_id in self.attention_values:
			self.attention_values[atom_id]["sti"] += sti_delta
			self.attention_values[atom_id]["lti"] += lti_delta

	def get_high_attention_atoms(self, limit: int = 10) -> List[str]:
		"""
		Get atoms with highest attention values
		Used for focusing cognitive resources on important entities
		
		Args:
			limit: Maximum number of atoms to return
			
		Returns:
			List of atom IDs sorted by attention
		"""
		sorted_atoms = sorted(
			self.attention_values.items(),
			key=lambda x: x[1]["sti"] + x[1]["lti"],
			reverse=True,
		)
		return [atom_id for atom_id, _ in sorted_atoms[:limit]]

	def store_erp_entity(self, doctype: str, doc_name: str, attributes: Dict[str, Any]):
		"""
		Store an ERPNext entity in the AtomSpace
		
		Args:
			doctype: ERPNext doctype
			doc_name: Document name
			attributes: Document attributes to store
		"""
		# Create concept node for the entity
		entity_id = self.add_node("ConceptNode", f"{doctype}:{doc_name}")
		
		# Create attribute nodes and links
		for attr_name, attr_value in attributes.items():
			if attr_value is not None:
				attr_node = self.add_node("ConceptNode", f"{attr_name}:{attr_value}")
				# Create evaluation link connecting entity to attribute
				self.add_link("EvaluationLink", [entity_id, attr_node])
		
		return entity_id

	def find_patterns(self, pattern_type: str) -> List[Dict]:
		"""
		Find patterns in the AtomSpace
		Used for pattern mining and predictive analytics
		
		Args:
			pattern_type: Type of pattern to find
			
		Returns:
			List of pattern matches
		"""
		patterns = []
		
		# Simple pattern matching - can be extended with more sophisticated algorithms
		if pattern_type == "frequent_links":
			link_counts = {}
			for link_id, link_data in self.links.items():
				link_type = link_data["type"]
				link_counts[link_type] = link_counts.get(link_type, 0) + 1
			
			for link_type, count in link_counts.items():
				if count > 5:  # Threshold for "frequent"
					patterns.append({"type": link_type, "count": count})
		
		return patterns

	def get_statistics(self) -> Dict[str, Any]:
		"""Get AtomSpace statistics for monitoring"""
		return {
			"total_atoms": len(self.atoms),
			"total_links": len(self.links),
			"avg_sti": (
				sum(av["sti"] for av in self.attention_values.values()) / len(self.attention_values)
				if self.attention_values
				else 0
			),
			"avg_lti": (
				sum(av["lti"] for av in self.attention_values.values()) / len(self.attention_values)
				if self.attention_values
				else 0
			),
		}
