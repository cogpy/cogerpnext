"""
Cognitive Dashboard - Server-side implementation
Provides data for the cognitive monitoring dashboard
"""

import frappe


@frappe.whitelist()
def get_dashboard_data():
	"""Get comprehensive dashboard data for cognitive system monitoring"""
	from erpnext.opencog_integration.api import (
		get_orchestrator,
		get_load_balancer,
		get_atomspace,
	)
	
	try:
		orchestrator = get_orchestrator()
		load_balancer = get_load_balancer()
		atomspace = get_atomspace()
		
		# Get orchestrator status
		orchestrator_status = orchestrator.get_status()
		
		# Get workload analysis
		workload_analysis = orchestrator.analyze_workload()
		
		# Get load distribution
		load_distribution = load_balancer.get_load_distribution()
		
		# Get atomspace statistics
		atomspace_stats = atomspace.get_statistics()
		
		# Get high-attention entities
		high_attention = atomspace.get_high_attention_atoms(limit=10)
		
		return {
			"success": True,
			"orchestrator": {
				"status": orchestrator_status,
				"workload": workload_analysis,
			},
			"load_balancer": {
				"distribution": load_distribution,
			},
			"atomspace": {
				"statistics": atomspace_stats,
				"high_attention_entities": high_attention,
			},
			"timestamp": frappe.utils.now(),
		}
	except Exception as e:
		frappe.log_error(f"Dashboard data error: {str(e)}", "Cognitive Dashboard")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_recent_tasks(limit=20):
	"""Get recent tasks from orchestrator"""
	from erpnext.opencog_integration.api import get_orchestrator
	
	orchestrator = get_orchestrator()
	
	# Get recent completed tasks
	recent_completed = orchestrator.completed_tasks[-limit:] if orchestrator.completed_tasks else []
	
	# Get pending tasks
	pending = orchestrator.task_queue[:limit]
	
	return {"completed": recent_completed, "pending": pending}


@frappe.whitelist()
def get_resource_performance():
	"""Get detailed resource performance metrics"""
	from erpnext.opencog_integration.api import get_load_balancer
	
	load_balancer = get_load_balancer()
	
	resources = []
	for resource_id, resource in load_balancer.resources.items():
		metrics = load_balancer.resource_metrics.get(resource_id, {})
		resources.append(
			{
				"id": resource_id,
				"type": resource["type"],
				"capacity": resource["capacity"],
				"current_load": resource["current_load"],
				"status": resource["status"],
				"metrics": metrics,
			}
		)
	
	return {"resources": resources}
