"""
Tests for OpenCog Integration - Cognitive Load Balancer
"""

import unittest
import frappe
from frappe.tests import IntegrationTestCase
from erpnext.opencog_integration.load_balancer import CognitiveLoadBalancer


class TestCognitiveLoadBalancer(IntegrationTestCase):
	def setUp(self):
		self.load_balancer = CognitiveLoadBalancer()

	def test_register_resource(self):
		"""Test resource registration"""
		success = self.load_balancer.register_resource(
			"worker1", "accounting_worker", {"concurrent_tasks": 10, "cpu": 2}
		)
		
		self.assertTrue(success)
		self.assertIn("worker1", self.load_balancer.resources)
		
		resource = self.load_balancer.resources["worker1"]
		self.assertEqual(resource["type"], "accounting_worker")
		self.assertEqual(resource["current_load"], 0)

	def test_allocate_task(self):
		"""Test task allocation to resources"""
		# Register resources
		self.load_balancer.register_resource("worker1", "general_worker", {"concurrent_tasks": 5})
		self.load_balancer.register_resource("worker2", "general_worker", {"concurrent_tasks": 5})
		
		# Allocate task
		task = {"id": "task1", "type": "test_task"}
		resource_id = self.load_balancer.allocate_task(task)
		
		self.assertIsNotNone(resource_id)
		self.assertIn(resource_id, ["worker1", "worker2"])
		
		# Verify resource load increased
		self.assertEqual(self.load_balancer.resources[resource_id]["current_load"], 1)

	def test_allocate_task_no_resources(self):
		"""Test task allocation when no resources available"""
		task = {"id": "task1", "type": "test_task"}
		resource_id = self.load_balancer.allocate_task(task)
		
		self.assertIsNone(resource_id)

	def test_suitability_score_calculation(self):
		"""Test suitability score calculation"""
		# Register specialized resource
		self.load_balancer.register_resource(
			"accounting_worker", "accounting_worker", {"concurrent_tasks": 10}
		)
		
		resource = self.load_balancer.resources["accounting_worker"]
		
		# Test with matching task type
		task = {"id": "task1", "type": "sales_invoice"}
		score = self.load_balancer._calculate_suitability_score(resource, task)
		
		self.assertGreater(score, 0)
		self.assertLessEqual(score, 100)

	def test_release_resource(self):
		"""Test resource release"""
		# Register and allocate
		self.load_balancer.register_resource("worker1", "general_worker", {"concurrent_tasks": 5})
		task = {"id": "task1", "type": "test_task"}
		resource_id = self.load_balancer.allocate_task(task)
		
		# Release resource
		task_result = {"success": True, "processing_time": 60}
		self.load_balancer.release_resource(resource_id, task_result)
		
		# Verify load decreased
		self.assertEqual(self.load_balancer.resources[resource_id]["current_load"], 0)

	def test_resource_metrics_update(self):
		"""Test that resource metrics are updated after task completion"""
		# Register resource
		self.load_balancer.register_resource("worker1", "general_worker", {"concurrent_tasks": 5})
		
		# Allocate and release with result
		task = {"id": "task1", "type": "test_task"}
		resource_id = self.load_balancer.allocate_task(task)
		
		task_result = {"success": True, "processing_time": 100}
		self.load_balancer.release_resource(resource_id, task_result)
		
		# Check metrics
		metrics = self.load_balancer.resource_metrics[resource_id]
		self.assertEqual(metrics["total_tasks_processed"], 1)
		self.assertEqual(metrics["success_rate"], 1.0)

	def test_rebalance(self):
		"""Test load rebalancing"""
		# Register resources with different loads
		self.load_balancer.register_resource("worker1", "general_worker", {"concurrent_tasks": 10})
		self.load_balancer.register_resource("worker2", "general_worker", {"concurrent_tasks": 10})
		
		# Simulate high load on worker1
		self.load_balancer.resources["worker1"]["current_load"] = 9  # 90% utilization
		self.load_balancer.resources["worker2"]["current_load"] = 1  # 10% utilization
		
		# Trigger rebalancing
		result = self.load_balancer.rebalance()
		
		self.assertIn("rebalanced", result)
		self.assertIn("overloaded_resources", result)
		self.assertIn("underutilized_resources", result)

	def test_get_load_distribution(self):
		"""Test getting load distribution"""
		# Register resources with different loads
		self.load_balancer.register_resource("worker1", "general_worker", {"concurrent_tasks": 10})
		self.load_balancer.register_resource("worker2", "general_worker", {"concurrent_tasks": 5})
		
		self.load_balancer.resources["worker1"]["current_load"] = 5
		self.load_balancer.resources["worker2"]["current_load"] = 2
		
		distribution = self.load_balancer.get_load_distribution()
		
		self.assertIn("resources", distribution)
		self.assertIn("total_resources", distribution)
		self.assertIn("average_utilization", distribution)
		self.assertEqual(distribution["total_resources"], 2)

	def test_resource_specialization(self):
		"""Test resource specialization matching"""
		# Register specialized resource
		self.load_balancer.register_resource(
			"accounting_worker", "accounting_worker", {"concurrent_tasks": 10}
		)
		
		resource = self.load_balancer.resources["accounting_worker"]
		
		# Test specialization check
		is_specialized = self.load_balancer._is_resource_specialized(resource, "sales_invoice")
		self.assertTrue(is_specialized)
		
		is_specialized = self.load_balancer._is_resource_specialized(resource, "random_task")
		self.assertFalse(is_specialized)

	def test_learning_toggle(self):
		"""Test enabling/disabling learning"""
		self.assertTrue(self.load_balancer.learning_enabled)
		
		self.load_balancer.enable_learning(False)
		self.assertFalse(self.load_balancer.learning_enabled)
		
		self.load_balancer.enable_learning(True)
		self.assertTrue(self.load_balancer.learning_enabled)
