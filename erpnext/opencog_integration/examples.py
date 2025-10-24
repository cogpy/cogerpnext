"""
Integration Examples for OpenCog in ERPNext
Demonstrates how to use the cognitive architecture in real ERPNext scenarios
"""

import frappe
from erpnext.opencog_integration.api import (
	get_orchestrator,
	get_load_balancer,
	get_atomspace,
)


def example_sales_order_optimization():
	"""
	Example: Using cognitive orchestrator to optimize sales order processing
	"""
	orchestrator = get_orchestrator()
	
	# Register sales order processing task
	task_id = orchestrator.register_task(
		task_type="sales_order",
		task_data={
			"doc_name": "SO-001",
			"action": "validate_and_submit",
			"priority_level": "high",
			"estimated_duration": 30,
		},
		priority=8,
	)
	
	print(f"Sales order task registered: {task_id}")
	
	# Analyze workload to get recommendations
	analysis = orchestrator.analyze_workload()
	print(f"Workload analysis: {analysis}")
	
	return task_id


def example_inventory_load_balancing():
	"""
	Example: Using cognitive load balancer for inventory operations
	"""
	load_balancer = get_load_balancer()
	
	# Register inventory processing resource
	success = load_balancer.register_resource(
		resource_id="inventory_processor_1",
		resource_type="inventory_worker",
		capacity={"concurrent_tasks": 15, "cpu": 4, "memory_gb": 8},
	)
	
	print(f"Resource registered: {success}")
	
	# Allocate multiple inventory tasks
	tasks = [
		{"id": "inv_task_1", "type": "stock_entry", "estimated_duration": 45},
		{"id": "inv_task_2", "type": "delivery_note", "estimated_duration": 30},
		{"id": "inv_task_3", "type": "purchase_receipt", "estimated_duration": 40},
	]
	
	allocations = []
	for task in tasks:
		resource_id = load_balancer.allocate_task(task)
		allocations.append({"task": task["id"], "resource": resource_id})
		print(f"Task {task['id']} allocated to {resource_id}")
	
	# Get load distribution
	distribution = load_balancer.get_load_distribution()
	print(f"Load distribution: {distribution}")
	
	return allocations


def example_customer_pattern_recognition():
	"""
	Example: Using AtomSpace to recognize customer behavior patterns
	"""
	atomspace = get_atomspace()
	
	# Store customer entities
	customers = ["CUST-001", "CUST-002", "CUST-003"]
	
	for customer in customers:
		entity_id = atomspace.store_erp_entity(
			doctype="Customer",
			doc_name=customer,
			attributes={
				"customer_group": "Commercial",
				"territory": "All Territories",
				"status": "Active",
			},
		)
		
		# Update attention for active customers
		atomspace.update_attention(entity_id, sti_delta=20, lti_delta=10)
		print(f"Customer {customer} stored with entity ID: {entity_id}")
	
	# Find high-attention customers (most important)
	important_customers = atomspace.get_high_attention_atoms(limit=5)
	print(f"Most important customers: {important_customers}")
	
	# Find patterns
	patterns = atomspace.find_patterns("frequent_links")
	print(f"Discovered patterns: {patterns}")
	
	return important_customers


def example_manufacturing_orchestration():
	"""
	Example: Orchestrating manufacturing workflow with cognitive optimization
	"""
	orchestrator = get_orchestrator()
	
	# Register manufacturing tasks with dependencies
	bom_task = orchestrator.register_task(
		task_type="bom_creation",
		task_data={"item": "ITEM-001", "qty": 100},
		priority=7,
	)
	
	# Work order depends on BOM
	wo_task = orchestrator.register_task(
		task_type="work_order",
		task_data={"bom": bom_task, "dependencies": [bom_task]},
		priority=8,
	)
	
	# Job card depends on work order
	job_card_task = orchestrator.register_task(
		task_type="job_card",
		task_data={"work_order": wo_task, "dependencies": [wo_task]},
		priority=6,
	)
	
	print(f"Manufacturing workflow registered:")
	print(f"  BOM Task: {bom_task}")
	print(f"  Work Order Task: {wo_task}")
	print(f"  Job Card Task: {job_card_task}")
	
	# Optimize task order
	optimized_tasks = orchestrator.optimize_task_order()
	print(f"Optimized task order: {[t['id'] for t in optimized_tasks]}")
	
	return {"bom": bom_task, "work_order": wo_task, "job_card": job_card_task}


def example_real_time_monitoring():
	"""
	Example: Real-time monitoring of cognitive system
	"""
	orchestrator = get_orchestrator()
	load_balancer = get_load_balancer()
	atomspace = get_atomspace()
	
	# Get comprehensive status
	status = {
		"orchestrator": orchestrator.get_status(),
		"load_balancer": load_balancer.get_load_distribution(),
		"atomspace": atomspace.get_statistics(),
	}
	
	print("=" * 60)
	print("COGNITIVE SYSTEM STATUS")
	print("=" * 60)
	print(f"\nOrchestrator:")
	print(f"  Pending Tasks: {status['orchestrator']['pending_tasks']}")
	print(f"  Active Tasks: {status['orchestrator']['active_tasks']}")
	print(f"  Completed Tasks: {status['orchestrator']['completed_tasks']}")
	
	print(f"\nLoad Balancer:")
	print(f"  Total Resources: {status['load_balancer']['total_resources']}")
	print(f"  Average Utilization: {status['load_balancer']['average_utilization']:.2f}%")
	
	print(f"\nAtomSpace:")
	print(f"  Total Atoms: {status['atomspace']['total_atoms']}")
	print(f"  Total Links: {status['atomspace']['total_links']}")
	print(f"  Avg STI: {status['atomspace']['avg_sti']:.2f}")
	print(f"  Avg LTI: {status['atomspace']['avg_lti']:.2f}")
	print("=" * 60)
	
	return status


# Whitelisted function for API access
@frappe.whitelist()
def run_example(example_name):
	"""
	Run a specific example
	
	Args:
		example_name: Name of the example to run
	"""
	examples = {
		"sales_order": example_sales_order_optimization,
		"inventory": example_inventory_load_balancing,
		"customer_patterns": example_customer_pattern_recognition,
		"manufacturing": example_manufacturing_orchestration,
		"monitoring": example_real_time_monitoring,
	}
	
	if example_name not in examples:
		return {"success": False, "error": f"Example '{example_name}' not found"}
	
	try:
		result = examples[example_name]()
		return {"success": True, "result": result}
	except Exception as e:
		frappe.log_error(f"Example error: {str(e)}", "OpenCog Examples")
		return {"success": False, "error": str(e)}
