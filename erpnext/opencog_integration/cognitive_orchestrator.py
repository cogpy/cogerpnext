"""
Cognitive Orchestrator for ERPNext
Manages autonomous task orchestration and workflow optimization using cognitive principles
"""

import frappe
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .atomspace_manager import AtomSpaceManager


class CognitiveOrchestrator:
	"""
	Autonomous orchestrator that uses cognitive principles to manage and optimize
	ERPNext workflows, tasks, and business processes
	"""

	def __init__(self):
		self.atomspace = AtomSpaceManager()
		self.task_queue = []
		self.active_tasks = {}
		self.completed_tasks = []
		self.optimization_rules = []

	def register_task(
		self, task_type: str, task_data: Dict[str, Any], priority: int = 5
	) -> str:
		"""
		Register a new task for cognitive orchestration
		
		Args:
			task_type: Type of task (e.g., 'sales_order', 'purchase_order')
			task_data: Task details and context
			priority: Task priority (1-10, 10 being highest)
			
		Returns:
			Task ID
		"""
		task_id = frappe.generate_hash(length=10)
		
		task = {
			"id": task_id,
			"type": task_type,
			"data": task_data,
			"priority": priority,
			"status": "pending",
			"created_at": frappe.utils.now(),
			"dependencies": task_data.get("dependencies", []),
			"estimated_duration": task_data.get("estimated_duration", 60),  # seconds
		}
		
		self.task_queue.append(task)
		
		# Store in AtomSpace for cognitive reasoning
		task_node = self.atomspace.add_node("ConceptNode", f"Task:{task_id}")
		type_node = self.atomspace.add_node("ConceptNode", f"TaskType:{task_type}")
		self.atomspace.add_link("InheritanceLink", [task_node, type_node])
		
		# Update attention based on priority
		self.atomspace.update_attention(task_node, sti_delta=priority * 10)
		
		return task_id

	def optimize_task_order(self) -> List[Dict]:
		"""
		Optimize task execution order using cognitive principles
		Considers priority, dependencies, resource availability, and learned patterns
		
		Returns:
			Optimized task list
		"""
		# Sort by priority and attention values
		optimized_tasks = []
		
		# First, separate tasks with and without dependencies
		independent_tasks = [t for t in self.task_queue if not t["dependencies"]]
		dependent_tasks = [t for t in self.task_queue if t["dependencies"]]
		
		# Sort independent tasks by priority
		independent_tasks.sort(key=lambda t: t["priority"], reverse=True)
		
		# For dependent tasks, check if dependencies are completed
		resolved_dependent_tasks = []
		for task in dependent_tasks:
			dependencies_met = all(
				dep_id in [ct["id"] for ct in self.completed_tasks]
				for dep_id in task["dependencies"]
			)
			if dependencies_met:
				resolved_dependent_tasks.append(task)
		
		resolved_dependent_tasks.sort(key=lambda t: t["priority"], reverse=True)
		
		# Combine optimized task order
		optimized_tasks = independent_tasks + resolved_dependent_tasks
		
		return optimized_tasks

	def execute_task(self, task_id: str) -> Dict[str, Any]:
		"""
		Execute a task with cognitive monitoring
		
		Args:
			task_id: Task identifier
			
		Returns:
			Execution result
		"""
		task = next((t for t in self.task_queue if t["id"] == task_id), None)
		
		if not task:
			return {"success": False, "error": "Task not found"}
		
		# Move to active tasks
		self.task_queue.remove(task)
		task["status"] = "executing"
		task["started_at"] = frappe.utils.now()
		self.active_tasks[task_id] = task
		
		# Simulate task execution (in real implementation, this would call actual ERPNext functions)
		result = {
			"success": True,
			"task_id": task_id,
			"task_type": task["type"],
			"executed_at": frappe.utils.now(),
		}
		
		# Update AtomSpace with execution results
		task_node = f"ConceptNode:Task:{task_id}"
		self.atomspace.update_attention(task_node, lti_delta=10)  # Increase long-term importance
		
		# Move to completed tasks
		task["status"] = "completed"
		task["completed_at"] = frappe.utils.now()
		self.completed_tasks.append(task)
		del self.active_tasks[task_id]
		
		return result

	def learn_from_execution(self, task_id: str, performance_metrics: Dict[str, Any]):
		"""
		Learn from task execution to improve future orchestration
		
		Args:
			task_id: Completed task ID
			performance_metrics: Metrics like duration, resource usage, success rate
		"""
		task = next((t for t in self.completed_tasks if t["id"] == task_id), None)
		
		if not task:
			return
		
		# Store learned patterns in AtomSpace
		task_type = task["type"]
		actual_duration = performance_metrics.get("duration", 0)
		
		# Create pattern node
		pattern_node = self.atomspace.add_node(
			"ConceptNode", f"Pattern:{task_type}:duration:{actual_duration}"
		)
		
		# Link pattern to task type with truth value representing confidence
		confidence = min(performance_metrics.get("confidence", 0.5), 1.0)
		self.atomspace.add_link(
			"EvaluationLink",
			[f"ConceptNode:TaskType:{task_type}", pattern_node],
			truth_value={"strength": 0.8, "confidence": confidence},
		)

	def analyze_workload(self) -> Dict[str, Any]:
		"""
		Analyze current workload and provide insights
		
		Returns:
			Workload analysis with recommendations
		"""
		total_tasks = len(self.task_queue) + len(self.active_tasks)
		
		# Analyze task distribution by type
		task_types = {}
		for task in self.task_queue + list(self.active_tasks.values()):
			task_type = task["type"]
			task_types[task_type] = task_types.get(task_type, 0) + 1
		
		# Estimate total workload time
		estimated_time = sum(t["estimated_duration"] for t in self.task_queue)
		
		# Get high-attention atoms from AtomSpace
		high_attention = self.atomspace.get_high_attention_atoms(limit=5)
		
		analysis = {
			"total_pending_tasks": len(self.task_queue),
			"total_active_tasks": len(self.active_tasks),
			"total_completed_tasks": len(self.completed_tasks),
			"task_distribution": task_types,
			"estimated_completion_time_seconds": estimated_time,
			"high_priority_entities": high_attention,
			"recommendations": self._generate_recommendations(task_types, estimated_time),
		}
		
		return analysis

	def _generate_recommendations(
		self, task_types: Dict[str, int], estimated_time: int
	) -> List[str]:
		"""Generate recommendations based on workload analysis"""
		recommendations = []
		
		# Check for task overload
		if len(self.task_queue) > 100:
			recommendations.append(
				"High task queue detected. Consider scaling resources or optimizing workflows."
			)
		
		# Check for long estimated completion time
		if estimated_time > 3600:  # More than 1 hour
			recommendations.append(
				f"Estimated completion time is {estimated_time / 3600:.1f} hours. "
				"Consider prioritizing critical tasks."
			)
		
		# Check for task type imbalance
		if task_types:
			max_type = max(task_types.values())
			if max_type > len(self.task_queue) * 0.5:
				recommendations.append(
					"Task distribution is imbalanced. Consider load balancing across task types."
				)
		
		return recommendations

	def get_status(self) -> Dict[str, Any]:
		"""Get current orchestrator status"""
		return {
			"pending_tasks": len(self.task_queue),
			"active_tasks": len(self.active_tasks),
			"completed_tasks": len(self.completed_tasks),
			"atomspace_stats": self.atomspace.get_statistics(),
		}
