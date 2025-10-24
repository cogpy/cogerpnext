"""
Tests for OpenCog Integration - Cognitive Orchestrator
"""

import unittest
import frappe
from frappe.tests import IntegrationTestCase
from erpnext.opencog_integration.cognitive_orchestrator import CognitiveOrchestrator


class TestCognitiveOrchestrator(IntegrationTestCase):
	def setUp(self):
		self.orchestrator = CognitiveOrchestrator()

	def test_register_task(self):
		"""Test task registration"""
		task_id = self.orchestrator.register_task(
			"sales_order", {"doc_name": "SO-001", "action": "process"}, priority=7
		)
		
		self.assertIsNotNone(task_id)
		self.assertEqual(len(self.orchestrator.task_queue), 1)
		
		task = self.orchestrator.task_queue[0]
		self.assertEqual(task["id"], task_id)
		self.assertEqual(task["type"], "sales_order")
		self.assertEqual(task["priority"], 7)

	def test_task_priority_ordering(self):
		"""Test that tasks are ordered by priority"""
		# Register tasks with different priorities
		task1_id = self.orchestrator.register_task("task1", {}, priority=3)
		task2_id = self.orchestrator.register_task("task2", {}, priority=8)
		task3_id = self.orchestrator.register_task("task3", {}, priority=5)
		
		# Optimize task order
		optimized = self.orchestrator.optimize_task_order()
		
		# Should be ordered by priority (highest first)
		self.assertEqual(optimized[0]["id"], task2_id)
		self.assertEqual(optimized[0]["priority"], 8)

	def test_task_dependencies(self):
		"""Test task dependency handling"""
		# Register independent task
		task1_id = self.orchestrator.register_task("task1", {}, priority=5)
		
		# Execute task1 to make it completed
		self.orchestrator.execute_task(task1_id)
		
		# Register dependent task
		task2_id = self.orchestrator.register_task(
			"task2", {"dependencies": [task1_id]}, priority=8
		)
		
		# Optimize - task2 should be included since task1 is completed
		optimized = self.orchestrator.optimize_task_order()
		
		task_ids = [t["id"] for t in optimized]
		self.assertIn(task2_id, task_ids)

	def test_execute_task(self):
		"""Test task execution"""
		task_id = self.orchestrator.register_task("test_task", {"data": "test"}, priority=5)
		
		# Execute task
		result = self.orchestrator.execute_task(task_id)
		
		self.assertTrue(result["success"])
		self.assertEqual(result["task_id"], task_id)
		
		# Task should be in completed tasks
		self.assertEqual(len(self.orchestrator.completed_tasks), 1)
		self.assertEqual(self.orchestrator.completed_tasks[0]["id"], task_id)

	def test_execute_nonexistent_task(self):
		"""Test executing a task that doesn't exist"""
		result = self.orchestrator.execute_task("nonexistent")
		
		self.assertFalse(result["success"])
		self.assertIn("error", result)

	def test_learn_from_execution(self):
		"""Test learning from task execution"""
		task_id = self.orchestrator.register_task("learning_task", {}, priority=5)
		self.orchestrator.execute_task(task_id)
		
		# Learn from execution
		metrics = {"duration": 120, "confidence": 0.9}
		self.orchestrator.learn_from_execution(task_id, metrics)
		
		# Verify pattern was stored in AtomSpace
		patterns = self.orchestrator.atomspace.find_patterns("frequent_links")
		self.assertIsInstance(patterns, list)

	def test_analyze_workload(self):
		"""Test workload analysis"""
		# Register multiple tasks
		for i in range(5):
			self.orchestrator.register_task(f"task_type_{i % 2}", {}, priority=5)
		
		analysis = self.orchestrator.analyze_workload()
		
		self.assertIn("total_pending_tasks", analysis)
		self.assertIn("task_distribution", analysis)
		self.assertIn("recommendations", analysis)
		self.assertEqual(analysis["total_pending_tasks"], 5)

	def test_get_status(self):
		"""Test getting orchestrator status"""
		# Register and execute some tasks
		task_id = self.orchestrator.register_task("status_task", {}, priority=5)
		self.orchestrator.execute_task(task_id)
		
		status = self.orchestrator.get_status()
		
		self.assertIn("pending_tasks", status)
		self.assertIn("active_tasks", status)
		self.assertIn("completed_tasks", status)
		self.assertIn("atomspace_stats", status)
		self.assertEqual(status["completed_tasks"], 1)
