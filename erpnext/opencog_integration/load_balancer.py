"""
Cognitive Load Balancer for ERPNext
Implements intelligent load balancing using cognitive decision-making and pattern recognition
"""

import frappe
from typing import Dict, Any, List, Optional
from datetime import datetime
import statistics


class CognitiveLoadBalancer:
	"""
	Cognitive load balancer that distributes workload intelligently across
	resources using learned patterns and real-time system metrics
	"""

	def __init__(self):
		self.resources = {}
		self.resource_metrics = {}
		self.allocation_history = []
		self.learning_enabled = True

	def register_resource(
		self, resource_id: str, resource_type: str, capacity: Dict[str, Any]
	) -> bool:
		"""
		Register a resource for load balancing
		
		Args:
			resource_id: Unique resource identifier
			resource_type: Type of resource (e.g., 'worker', 'queue', 'server')
			capacity: Resource capacity metrics (cpu, memory, concurrent_tasks, etc.)
			
		Returns:
			Success status
		"""
		self.resources[resource_id] = {
			"id": resource_id,
			"type": resource_type,
			"capacity": capacity,
			"current_load": 0,
			"status": "available",
			"registered_at": frappe.utils.now(),
		}
		
		self.resource_metrics[resource_id] = {
			"total_tasks_processed": 0,
			"average_processing_time": 0,
			"success_rate": 1.0,
			"recent_performance": [],
		}
		
		return True

	def allocate_task(self, task: Dict[str, Any]) -> Optional[str]:
		"""
		Allocate a task to the most suitable resource using cognitive decision-making
		
		Args:
			task: Task to be allocated with requirements
			
		Returns:
			Selected resource ID or None if no suitable resource found
		"""
		if not self.resources:
			return None
		
		# Calculate suitability scores for each available resource
		scores = {}
		
		for resource_id, resource in self.resources.items():
			if resource["status"] != "available":
				continue
			
			score = self._calculate_suitability_score(resource, task)
			scores[resource_id] = score
		
		if not scores:
			return None
		
		# Select resource with highest suitability score
		selected_resource_id = max(scores, key=scores.get)
		
		# Update resource load
		self.resources[selected_resource_id]["current_load"] += 1
		
		# Record allocation
		self.allocation_history.append(
			{
				"task_id": task.get("id"),
				"resource_id": selected_resource_id,
				"allocated_at": frappe.utils.now(),
				"suitability_score": scores[selected_resource_id],
			}
		)
		
		return selected_resource_id

	def _calculate_suitability_score(self, resource: Dict[str, Any], task: Dict[str, Any]) -> float:
		"""
		Calculate suitability score for a resource-task pairing
		Uses multiple factors: capacity, current load, past performance, task requirements
		
		Args:
			resource: Resource details
			task: Task details
			
		Returns:
			Suitability score (0-100)
		"""
		score = 0.0
		
		# Factor 1: Available capacity (30% weight)
		capacity = resource["capacity"].get("concurrent_tasks", 10)
		current_load = resource["current_load"]
		capacity_score = ((capacity - current_load) / capacity) * 30
		score += max(capacity_score, 0)
		
		# Factor 2: Historical performance (40% weight)
		metrics = self.resource_metrics.get(resource["id"], {})
		success_rate = metrics.get("success_rate", 1.0)
		performance_score = success_rate * 40
		score += performance_score
		
		# Factor 3: Resource type matching (20% weight)
		task_type = task.get("type", "")
		if self._is_resource_specialized(resource, task_type):
			score += 20
		else:
			score += 10  # Partial credit for general resources
		
		# Factor 4: Recent performance trend (10% weight)
		recent_perf = metrics.get("recent_performance", [])
		if recent_perf:
			trend = statistics.mean(recent_perf[-5:]) if len(recent_perf) >= 5 else statistics.mean(recent_perf)
			trend_score = trend * 10
			score += trend_score
		else:
			score += 5  # Neutral for new resources
		
		return score

	def _is_resource_specialized(self, resource: Dict[str, Any], task_type: str) -> bool:
		"""Check if resource is specialized for a specific task type"""
		# Simple specialization check - can be enhanced with more sophisticated logic
		resource_type = resource["type"]
		
		# Define specializations
		specializations = {
			"accounting_worker": ["sales_invoice", "purchase_invoice", "payment_entry"],
			"inventory_worker": ["stock_entry", "delivery_note", "purchase_receipt"],
			"manufacturing_worker": ["work_order", "bom", "job_card"],
		}
		
		return task_type in specializations.get(resource_type, [])

	def release_resource(self, resource_id: str, task_result: Optional[Dict[str, Any]] = None):
		"""
		Release a resource after task completion and update metrics
		
		Args:
			resource_id: Resource to release
			task_result: Optional task execution result for learning
		"""
		if resource_id not in self.resources:
			return
		
		# Decrease load
		self.resources[resource_id]["current_load"] = max(
			0, self.resources[resource_id]["current_load"] - 1
		)
		
		# Update metrics if task result provided
		if task_result and self.learning_enabled:
			self._update_resource_metrics(resource_id, task_result)

	def _update_resource_metrics(self, resource_id: str, task_result: Dict[str, Any]):
		"""
		Update resource metrics based on task execution results
		Enables cognitive learning and adaptation
		
		Args:
			resource_id: Resource identifier
			task_result: Task execution results
		"""
		metrics = self.resource_metrics[resource_id]
		
		# Update total tasks processed
		metrics["total_tasks_processed"] += 1
		
		# Update success rate
		task_success = 1.0 if task_result.get("success", False) else 0.0
		current_success_rate = metrics["success_rate"]
		total_tasks = metrics["total_tasks_processed"]
		metrics["success_rate"] = (
			(current_success_rate * (total_tasks - 1) + task_success) / total_tasks
		)
		
		# Update processing time
		processing_time = task_result.get("processing_time", 0)
		if processing_time > 0:
			current_avg = metrics["average_processing_time"]
			metrics["average_processing_time"] = (
				(current_avg * (total_tasks - 1) + processing_time) / total_tasks
			)
		
		# Update recent performance
		performance_score = task_success  # Can be more sophisticated
		metrics["recent_performance"].append(performance_score)
		
		# Keep only recent history (last 100 tasks)
		if len(metrics["recent_performance"]) > 100:
			metrics["recent_performance"] = metrics["recent_performance"][-100:]

	def rebalance(self) -> Dict[str, Any]:
		"""
		Perform cognitive rebalancing of workload across resources
		Identifies and redistributes load from overloaded resources
		
		Returns:
			Rebalancing report
		"""
		if not self.resources:
			return {"rebalanced": False, "reason": "No resources registered"}
		
		# Identify overloaded and underutilized resources
		overloaded = []
		underutilized = []
		
		for resource_id, resource in self.resources.items():
			capacity = resource["capacity"].get("concurrent_tasks", 10)
			current_load = resource["current_load"]
			utilization = current_load / capacity if capacity > 0 else 0
			
			if utilization > 0.8:  # Over 80% capacity
				overloaded.append(resource_id)
			elif utilization < 0.3:  # Under 30% capacity
				underutilized.append(resource_id)
		
		rebalancing_actions = []
		
		# Generate rebalancing recommendations
		if overloaded and underutilized:
			rebalancing_actions.append(
				{
					"action": "redistribute",
					"from": overloaded,
					"to": underutilized,
					"reason": "Load imbalance detected",
				}
			)
		
		return {
			"rebalanced": len(rebalancing_actions) > 0,
			"overloaded_resources": overloaded,
			"underutilized_resources": underutilized,
			"actions": rebalancing_actions,
			"timestamp": frappe.utils.now(),
		}

	def get_load_distribution(self) -> Dict[str, Any]:
		"""
		Get current load distribution across all resources
		
		Returns:
			Load distribution report
		"""
		distribution = []
		
		for resource_id, resource in self.resources.items():
			capacity = resource["capacity"].get("concurrent_tasks", 10)
			current_load = resource["current_load"]
			utilization = (current_load / capacity * 100) if capacity > 0 else 0
			
			distribution.append(
				{
					"resource_id": resource_id,
					"type": resource["type"],
					"current_load": current_load,
					"capacity": capacity,
					"utilization_percent": utilization,
					"status": resource["status"],
				}
			)
		
		# Calculate overall statistics
		if distribution:
			avg_utilization = statistics.mean([r["utilization_percent"] for r in distribution])
		else:
			avg_utilization = 0
		
		return {
			"resources": distribution,
			"total_resources": len(distribution),
			"average_utilization": avg_utilization,
			"total_allocations": len(self.allocation_history),
		}

	def get_resource_metrics(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
		"""
		Get performance metrics for a specific resource or all resources
		
		Args:
			resource_id: Optional specific resource ID
			
		Returns:
			Resource metrics
		"""
		if resource_id:
			return self.resource_metrics.get(resource_id, {})
		
		return self.resource_metrics

	def enable_learning(self, enabled: bool = True):
		"""Enable or disable cognitive learning"""
		self.learning_enabled = enabled
