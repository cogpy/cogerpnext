"""
Performance Metrics and Monitoring Utilities
Provides utilities for collecting and analyzing cognitive system performance
"""

import frappe
from datetime import datetime, timedelta
from typing import Dict, Any, List


class PerformanceMetrics:
	"""
	Collects and analyzes performance metrics for the cognitive system
	"""

	def __init__(self):
		self.metrics_history = []
		self.max_history_size = 1000

	def record_task_execution(
		self,
		task_id: str,
		task_type: str,
		execution_time: float,
		resource_id: str,
		success: bool,
	):
		"""
		Record a task execution for performance analysis
		
		Args:
			task_id: Task identifier
			task_type: Type of task
			execution_time: Time taken to execute (seconds)
			resource_id: Resource that executed the task
			success: Whether task succeeded
		"""
		metric = {
			"task_id": task_id,
			"task_type": task_type,
			"execution_time": execution_time,
			"resource_id": resource_id,
			"success": success,
			"timestamp": frappe.utils.now(),
		}
		
		self.metrics_history.append(metric)
		
		# Keep history size limited
		if len(self.metrics_history) > self.max_history_size:
			self.metrics_history = self.metrics_history[-self.max_history_size :]

	def get_average_execution_time(self, task_type: str = None) -> float:
		"""
		Get average execution time for tasks
		
		Args:
			task_type: Optional filter by task type
			
		Returns:
			Average execution time in seconds
		"""
		if not self.metrics_history:
			return 0.0
		
		relevant_metrics = self.metrics_history
		if task_type:
			relevant_metrics = [m for m in self.metrics_history if m["task_type"] == task_type]
		
		if not relevant_metrics:
			return 0.0
		
		total_time = sum(m["execution_time"] for m in relevant_metrics)
		return total_time / len(relevant_metrics)

	def get_success_rate(self, task_type: str = None) -> float:
		"""
		Get success rate for tasks
		
		Args:
			task_type: Optional filter by task type
			
		Returns:
			Success rate (0-1)
		"""
		if not self.metrics_history:
			return 1.0
		
		relevant_metrics = self.metrics_history
		if task_type:
			relevant_metrics = [m for m in self.metrics_history if m["task_type"] == task_type]
		
		if not relevant_metrics:
			return 1.0
		
		successful = sum(1 for m in relevant_metrics if m["success"])
		return successful / len(relevant_metrics)

	def get_throughput(self, time_window_minutes: int = 60) -> float:
		"""
		Get throughput (tasks per minute) for recent time window
		
		Args:
			time_window_minutes: Time window to analyze
			
		Returns:
			Throughput (tasks per minute)
		"""
		if not self.metrics_history:
			return 0.0
		
		cutoff_time = frappe.utils.add_to_date(None, minutes=-time_window_minutes)
		
		recent_metrics = [
			m for m in self.metrics_history if m["timestamp"] >= cutoff_time
		]
		
		if not recent_metrics:
			return 0.0
		
		return len(recent_metrics) / time_window_minutes

	def get_resource_performance(self, resource_id: str) -> Dict[str, Any]:
		"""
		Get performance metrics for a specific resource
		
		Args:
			resource_id: Resource identifier
			
		Returns:
			Performance metrics
		"""
		resource_metrics = [m for m in self.metrics_history if m["resource_id"] == resource_id]
		
		if not resource_metrics:
			return {
				"tasks_executed": 0,
				"average_execution_time": 0.0,
				"success_rate": 1.0,
			}
		
		total_time = sum(m["execution_time"] for m in resource_metrics)
		successful = sum(1 for m in resource_metrics if m["success"])
		
		return {
			"tasks_executed": len(resource_metrics),
			"average_execution_time": total_time / len(resource_metrics),
			"success_rate": successful / len(resource_metrics),
		}

	def get_performance_summary(self) -> Dict[str, Any]:
		"""
		Get comprehensive performance summary
		
		Returns:
			Performance summary
		"""
		if not self.metrics_history:
			return {
				"total_tasks": 0,
				"average_execution_time": 0.0,
				"success_rate": 1.0,
				"throughput_per_minute": 0.0,
			}
		
		return {
			"total_tasks": len(self.metrics_history),
			"average_execution_time": self.get_average_execution_time(),
			"success_rate": self.get_success_rate(),
			"throughput_per_minute": self.get_throughput(60),
			"throughput_per_hour": self.get_throughput(60) * 60,
		}


# Global instance
_performance_metrics = None


def get_performance_metrics():
	"""Get or create performance metrics instance"""
	global _performance_metrics
	if _performance_metrics is None:
		_performance_metrics = PerformanceMetrics()
	return _performance_metrics


@frappe.whitelist()
def get_performance_report():
	"""
	Get performance report for monitoring
	
	Returns:
		Performance report
	"""
	metrics = get_performance_metrics()
	return metrics.get_performance_summary()
