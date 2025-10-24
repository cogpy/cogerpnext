"""
API endpoints for OpenCog Integration
Provides REST API for cognitive architecture management and monitoring
"""

import frappe
from frappe import _
from typing import Dict, Any
from .cognitive_orchestrator import CognitiveOrchestrator
from .load_balancer import CognitiveLoadBalancer
from .atomspace_manager import AtomSpaceManager


# Global instances (in production, these should be properly managed with lifecycle)
_orchestrator = None
_load_balancer = None
_atomspace = None


def get_orchestrator():
	"""Get or create cognitive orchestrator instance"""
	global _orchestrator
	if _orchestrator is None:
		_orchestrator = CognitiveOrchestrator()
	return _orchestrator


def get_load_balancer():
	"""Get or create cognitive load balancer instance"""
	global _load_balancer
	if _load_balancer is None:
		_load_balancer = CognitiveLoadBalancer()
	return _load_balancer


def get_atomspace():
	"""Get or create atomspace manager instance"""
	global _atomspace
	if _atomspace is None:
		_atomspace = AtomSpaceManager()
	return _atomspace


@frappe.whitelist()
def get_cognitive_status():
	"""
	Get current status of the cognitive architecture
	
	Returns:
		Status information including orchestrator, load balancer, and atomspace
	"""
	orchestrator = get_orchestrator()
	load_balancer = get_load_balancer()
	atomspace = get_atomspace()
	
	return {
		"orchestrator_status": orchestrator.get_status(),
		"load_distribution": load_balancer.get_load_distribution(),
		"atomspace_statistics": atomspace.get_statistics(),
		"timestamp": frappe.utils.now(),
	}


@frappe.whitelist()
def register_task(task_type, task_data, priority=5):
	"""
	Register a new task for cognitive orchestration
	
	Args:
		task_type: Type of task
		task_data: Task data (JSON string or dict)
		priority: Task priority (1-10)
		
	Returns:
		Task ID
	"""
	if isinstance(task_data, str):
		task_data = frappe.parse_json(task_data)
	
	orchestrator = get_orchestrator()
	task_id = orchestrator.register_task(task_type, task_data, int(priority))
	
	return {"success": True, "task_id": task_id}


@frappe.whitelist()
def get_workload_analysis():
	"""
	Get workload analysis and recommendations
	
	Returns:
		Workload analysis report
	"""
	orchestrator = get_orchestrator()
	return orchestrator.analyze_workload()


@frappe.whitelist()
def register_resource(resource_id, resource_type, capacity):
	"""
	Register a resource for load balancing
	
	Args:
		resource_id: Unique resource identifier
		resource_type: Type of resource
		capacity: Resource capacity (JSON string or dict)
		
	Returns:
		Success status
	"""
	if isinstance(capacity, str):
		capacity = frappe.parse_json(capacity)
	
	load_balancer = get_load_balancer()
	success = load_balancer.register_resource(resource_id, resource_type, capacity)
	
	return {"success": success, "resource_id": resource_id}


@frappe.whitelist()
def trigger_rebalancing():
	"""
	Trigger cognitive load rebalancing
	
	Returns:
		Rebalancing report
	"""
	load_balancer = get_load_balancer()
	result = load_balancer.rebalance()
	
	return result


@frappe.whitelist()
def get_resource_metrics(resource_id=None):
	"""
	Get resource performance metrics
	
	Args:
		resource_id: Optional specific resource ID
		
	Returns:
		Resource metrics
	"""
	load_balancer = get_load_balancer()
	return load_balancer.get_resource_metrics(resource_id)


@frappe.whitelist()
def store_erp_entity(doctype, doc_name, attributes):
	"""
	Store an ERPNext entity in the AtomSpace for cognitive processing
	
	Args:
		doctype: ERPNext doctype
		doc_name: Document name
		attributes: Document attributes (JSON string or dict)
		
	Returns:
		Entity ID in AtomSpace
	"""
	if isinstance(attributes, str):
		attributes = frappe.parse_json(attributes)
	
	atomspace = get_atomspace()
	entity_id = atomspace.store_erp_entity(doctype, doc_name, attributes)
	
	return {"success": True, "entity_id": entity_id}


@frappe.whitelist()
def find_patterns(pattern_type):
	"""
	Find patterns in the AtomSpace
	
	Args:
		pattern_type: Type of pattern to search for
		
	Returns:
		List of patterns found
	"""
	atomspace = get_atomspace()
	patterns = atomspace.find_patterns(pattern_type)
	
	return {"patterns": patterns, "count": len(patterns)}


@frappe.whitelist()
def optimize_task_order():
	"""
	Get optimized task execution order
	
	Returns:
		Optimized task list
	"""
	orchestrator = get_orchestrator()
	optimized_tasks = orchestrator.optimize_task_order()
	
	return {"tasks": optimized_tasks, "count": len(optimized_tasks)}


@frappe.whitelist()
def get_high_attention_entities(limit=10):
	"""
	Get entities with highest attention values
	
	Args:
		limit: Maximum number of entities to return
		
	Returns:
		List of high-attention entities
	"""
	atomspace = get_atomspace()
	entities = atomspace.get_high_attention_atoms(int(limit))
	
	return {"entities": entities, "count": len(entities)}
