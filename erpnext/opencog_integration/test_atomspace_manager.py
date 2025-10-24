"""
Tests for OpenCog Integration - AtomSpace Manager
"""

import unittest
import frappe
from frappe.tests import IntegrationTestCase
from erpnext.opencog_integration.atomspace_manager import AtomSpaceManager


class TestAtomSpaceManager(IntegrationTestCase):
	def setUp(self):
		self.atomspace = AtomSpaceManager()

	def test_add_node(self):
		"""Test adding a node to AtomSpace"""
		node_id = self.atomspace.add_node("ConceptNode", "TestNode")
		
		self.assertIsNotNone(node_id)
		self.assertEqual(node_id, "ConceptNode:TestNode")
		
		# Verify node was stored
		node = self.atomspace.get_atom(node_id)
		self.assertIsNotNone(node)
		self.assertEqual(node["type"], "ConceptNode")
		self.assertEqual(node["name"], "TestNode")

	def test_add_link(self):
		"""Test adding a link between atoms"""
		# Create two nodes
		node1_id = self.atomspace.add_node("ConceptNode", "Node1")
		node2_id = self.atomspace.add_node("ConceptNode", "Node2")
		
		# Create link between them
		link_id = self.atomspace.add_link("InheritanceLink", [node1_id, node2_id])
		
		self.assertIsNotNone(link_id)
		
		# Verify link was stored
		link = self.atomspace.get_atom(link_id)
		self.assertIsNotNone(link)
		self.assertEqual(link["type"], "InheritanceLink")
		self.assertEqual(len(link["outgoing"]), 2)

	def test_attention_values(self):
		"""Test attention value management"""
		node_id = self.atomspace.add_node("ConceptNode", "AttentionNode")
		
		# Initial attention should be 0
		attention = self.atomspace.attention_values[node_id]
		self.assertEqual(attention["sti"], 0)
		self.assertEqual(attention["lti"], 0)
		
		# Update attention
		self.atomspace.update_attention(node_id, sti_delta=10, lti_delta=5)
		
		attention = self.atomspace.attention_values[node_id]
		self.assertEqual(attention["sti"], 10)
		self.assertEqual(attention["lti"], 5)

	def test_get_high_attention_atoms(self):
		"""Test retrieving high-attention atoms"""
		# Create multiple nodes with different attention values
		for i in range(5):
			node_id = self.atomspace.add_node("ConceptNode", f"Node{i}")
			self.atomspace.update_attention(node_id, sti_delta=i * 10)
		
		# Get top 3 high-attention atoms
		high_attention = self.atomspace.get_high_attention_atoms(limit=3)
		
		self.assertEqual(len(high_attention), 3)

	def test_store_erp_entity(self):
		"""Test storing ERPNext entity in AtomSpace"""
		entity_id = self.atomspace.store_erp_entity(
			"Sales Order", "SO-001", {"customer": "Test Customer", "status": "Open"}
		)
		
		self.assertIsNotNone(entity_id)
		
		# Verify entity node was created
		entity = self.atomspace.get_atom(entity_id)
		self.assertIsNotNone(entity)

	def test_find_patterns(self):
		"""Test pattern finding"""
		# Create multiple similar links
		for i in range(10):
			node1 = self.atomspace.add_node("ConceptNode", f"A{i}")
			node2 = self.atomspace.add_node("ConceptNode", f"B{i}")
			self.atomspace.add_link("TestLink", [node1, node2])
		
		# Find patterns
		patterns = self.atomspace.find_patterns("frequent_links")
		
		self.assertIsInstance(patterns, list)

	def test_statistics(self):
		"""Test getting AtomSpace statistics"""
		# Add some atoms
		self.atomspace.add_node("ConceptNode", "StatNode1")
		self.atomspace.add_node("ConceptNode", "StatNode2")
		
		stats = self.atomspace.get_statistics()
		
		self.assertIn("total_atoms", stats)
		self.assertIn("total_links", stats)
		self.assertGreaterEqual(stats["total_atoms"], 2)
