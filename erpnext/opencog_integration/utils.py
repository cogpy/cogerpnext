"""
Utility functions for OpenCog Integration
"""

import frappe
from typing import Dict, Any, List, Optional


def sync_doctype_to_atomspace(doctype: str, filters: Optional[Dict] = None, limit: int = 100):
	"""
	Sync documents of a specific doctype to AtomSpace
	
	Args:
		doctype: Name of the doctype to sync
		filters: Optional filters for fetching documents
		limit: Maximum number of documents to sync
	"""
	from erpnext.opencog_integration.api import get_atomspace
	
	atomspace = get_atomspace()
	
	# Get documents
	docs = frappe.get_all(doctype, filters=filters or {}, limit=limit)
	
	synced_count = 0
	for doc in docs:
		try:
			# Get full document
			full_doc = frappe.get_doc(doctype, doc.name)
			
			# Extract relevant attributes
			attributes = {}
			for field in full_doc.meta.fields:
				if field.fieldtype in ["Data", "Select", "Link", "Float", "Int", "Currency"]:
					value = getattr(full_doc, field.fieldname, None)
					if value is not None:
						attributes[field.fieldname] = value
			
			# Store in AtomSpace
			atomspace.store_erp_entity(doctype, doc.name, attributes)
			synced_count += 1
			
		except Exception as e:
			frappe.log_error(f"Error syncing {doctype} {doc.name}: {str(e)}", "AtomSpace Sync")
	
	return synced_count


def create_cognitive_task_from_doc(doc, priority: int = 5) -> str:
	"""
	Create a cognitive task from a Frappe document
	
	Args:
		doc: Frappe document
		priority: Task priority
		
	Returns:
		Task ID
	"""
	from erpnext.opencog_integration.api import get_orchestrator
	
	orchestrator = get_orchestrator()
	
	task_data = {
		"doctype": doc.doctype,
		"doc_name": doc.name,
		"action": "process",
		"status": doc.get("status"),
	}
	
	task_id = orchestrator.register_task(doc.doctype, task_data, priority)
	
	return task_id


def allocate_doc_processing(doc) -> Optional[str]:
	"""
	Allocate document processing to a cognitive resource
	
	Args:
		doc: Frappe document to process
		
	Returns:
		Resource ID if allocated, None otherwise
	"""
	from erpnext.opencog_integration.api import get_load_balancer
	
	load_balancer = get_load_balancer()
	
	task = {
		"id": f"{doc.doctype}:{doc.name}",
		"type": doc.doctype,
		"doc": doc,
	}
	
	resource_id = load_balancer.allocate_task(task)
	
	return resource_id


def get_cognitive_insights(doctype: str, doc_name: str) -> Dict[str, Any]:
	"""
	Get cognitive insights for a specific document
	
	Args:
		doctype: Document type
		doc_name: Document name
		
	Returns:
		Insights dictionary
	"""
	from erpnext.opencog_integration.api import get_atomspace
	
	atomspace = get_atomspace()
	
	entity_id = f"ConceptNode:{doctype}:{doc_name}"
	
	insights = {
		"entity_id": entity_id,
		"exists_in_atomspace": entity_id in atomspace.atoms,
		"attention": atomspace.attention_values.get(entity_id, {}),
		"related_entities": [],
	}
	
	# Find related entities through links
	for link_id, link_data in atomspace.links.items():
		if entity_id in link_data.get("outgoing", []):
			insights["related_entities"].append(
				{"link_type": link_data["type"], "link_id": link_id}
			)
	
	return insights


def optimize_workflow(workflow_name: str, tasks: List[Dict]) -> List[Dict]:
	"""
	Optimize a workflow using cognitive orchestration
	
	Args:
		workflow_name: Name of the workflow
		tasks: List of tasks in the workflow
		
	Returns:
		Optimized task list
	"""
	from erpnext.opencog_integration.api import get_orchestrator
	
	orchestrator = get_orchestrator()
	
	# Register all tasks
	task_ids = []
	for task in tasks:
		task_id = orchestrator.register_task(
			task_type=task.get("type", workflow_name),
			task_data=task.get("data", {}),
			priority=task.get("priority", 5),
		)
		task_ids.append(task_id)
	
	# Optimize task order
	optimized = orchestrator.optimize_task_order()
	
	return optimized


def batch_process_with_load_balancing(
	items: List[Any], processor_function, batch_size: int = 10
) -> List[Any]:
	"""
	Process a batch of items with cognitive load balancing
	
	Args:
		items: Items to process
		processor_function: Function to process each item
		batch_size: Number of items per batch
		
	Returns:
		Processing results
	"""
	import time
	from erpnext.opencog_integration.api import get_load_balancer
	
	load_balancer = get_load_balancer()
	results = []
	item_counter = 0
	
	for i in range(0, len(items), batch_size):
		batch = items[i : i + batch_size]
		
		for j, item in enumerate(batch):
			# Allocate task with unique ID
			task = {"id": f"batch_item_{i}_{j}", "type": "batch_processing"}
			resource_id = load_balancer.allocate_task(task)
			
			if resource_id:
				start_time = time.time()
				try:
					# Process item
					result = processor_function(item)
					results.append(result)
					
					# Calculate actual processing time
					processing_time = time.time() - start_time
					
					# Release resource with success
					load_balancer.release_resource(
						resource_id, {"success": True, "processing_time": processing_time}
					)
				except Exception as e:
					# Calculate processing time even on failure
					processing_time = time.time() - start_time
					
					# Release resource with failure
					load_balancer.release_resource(
						resource_id, {"success": False, "processing_time": processing_time}
					)
					frappe.log_error(f"Batch processing error: {str(e)}", "Batch Processing")
			
			item_counter += 1
	
	return results


def get_system_health() -> Dict[str, Any]:
	"""
	Get overall cognitive system health status
	
	Returns:
		Health status dictionary
	"""
	from erpnext.opencog_integration.api import (
		get_orchestrator,
		get_load_balancer,
		get_atomspace,
	)
	
	orchestrator = get_orchestrator()
	load_balancer = get_load_balancer()
	atomspace = get_atomspace()
	
	# Check orchestrator health
	orchestrator_status = orchestrator.get_status()
	orchestrator_health = "healthy"
	if orchestrator_status["pending_tasks"] > 100:
		orchestrator_health = "warning"
	if orchestrator_status["pending_tasks"] > 500:
		orchestrator_health = "critical"
	
	# Check load balancer health
	load_dist = load_balancer.get_load_distribution()
	lb_health = "healthy"
	if load_dist["average_utilization"] > 80:
		lb_health = "warning"
	if load_dist["average_utilization"] > 95:
		lb_health = "critical"
	
	# Check atomspace health
	atomspace_stats = atomspace.get_statistics()
	atomspace_health = "healthy"
	if atomspace_stats["total_atoms"] > 10000:
		atomspace_health = "warning"
	if atomspace_stats["total_atoms"] > 50000:
		atomspace_health = "critical"
	
	# Overall health
	health_levels = [orchestrator_health, lb_health, atomspace_health]
	if "critical" in health_levels:
		overall_health = "critical"
	elif "warning" in health_levels:
		overall_health = "warning"
	else:
		overall_health = "healthy"
	
	return {
		"overall_health": overall_health,
		"orchestrator": {"health": orchestrator_health, "status": orchestrator_status},
		"load_balancer": {"health": lb_health, "distribution": load_dist},
		"atomspace": {"health": atomspace_health, "statistics": atomspace_stats},
	}


@frappe.whitelist()
def sync_recent_docs(doctype, days=1, limit=100):
	"""
	API endpoint to sync recent documents to AtomSpace
	
	Args:
		doctype: Document type to sync
		days: Number of days to look back
		limit: Maximum documents to sync
	"""
	filters = {"modified": [">", frappe.utils.add_days(None, -int(days))]}
	
	count = sync_doctype_to_atomspace(doctype, filters, int(limit))
	
	return {"success": True, "synced_count": count, "doctype": doctype}
