"""
Scheduler integration for autonomous cognitive operations
Provides background tasks for continuous optimization and learning
"""

import frappe
from .api import get_orchestrator, get_load_balancer, get_atomspace
from .config import get_opencog_settings


def cognitive_optimization_cycle():
	"""
	Main cognitive optimization cycle - runs periodically
	Orchestrates tasks, balances load, and updates cognitive models
	"""
	settings = get_opencog_settings()
	
	if not settings.get("enabled"):
		return
	
	try:
		orchestrator = get_orchestrator()
		load_balancer = get_load_balancer()
		
		# Analyze workload
		analysis = orchestrator.analyze_workload()
		
		# Log analysis for monitoring
		frappe.logger().info(f"Cognitive workload analysis: {analysis}")
		
		# Optimize task order
		if settings.get("auto_orchestration"):
			optimized_tasks = orchestrator.optimize_task_order()
			
			# Execute high-priority tasks (with limit to prevent overload)
			max_tasks = min(3, len(optimized_tasks))
			for task in optimized_tasks[:max_tasks]:
				# Allocate resource
				resource_id = load_balancer.allocate_task(task)
				
				if resource_id:
					# Execute task
					result = orchestrator.execute_task(task["id"])
					
					# Release resource
					load_balancer.release_resource(resource_id, result)
					
					# Learn from execution
					orchestrator.learn_from_execution(
						task["id"], {"duration": 60, "confidence": 0.8}
					)
		
		# Perform load rebalancing
		if settings.get("load_balancing_enabled"):
			rebalance_result = load_balancer.rebalance()
			if rebalance_result.get("rebalanced"):
				frappe.logger().info(f"Load rebalancing performed: {rebalance_result}")
		
		# Update attention values (decay)
		_update_attention_values()
		
	except Exception as e:
		frappe.log_error(f"Cognitive optimization cycle error: {str(e)}", "OpenCog Integration")


def _update_attention_values():
	"""Update attention values with decay over time"""
	settings = get_opencog_settings()
	decay_rate = settings.get("attention_decay_rate", 0.05)
	
	atomspace = get_atomspace()
	
	# Apply attention decay to all atoms
	for atom_id in list(atomspace.attention_values.keys()):
		current_sti = atomspace.attention_values[atom_id]["sti"]
		current_lti = atomspace.attention_values[atom_id]["lti"]
		
		# Decay STI (short-term importance) faster than LTI
		new_sti = max(0, current_sti - (current_sti * decay_rate))
		new_lti = max(0, current_lti - (current_lti * decay_rate * 0.1))
		
		atomspace.attention_values[atom_id]["sti"] = new_sti
		atomspace.attention_values[atom_id]["lti"] = new_lti


def pattern_recognition_cycle():
	"""
	Pattern recognition cycle - identifies patterns in ERPNext data
	"""
	settings = get_opencog_settings()
	
	if not settings.get("enabled"):
		return
	
	try:
		atomspace = get_atomspace()
		
		# Find frequent patterns
		patterns = atomspace.find_patterns("frequent_links")
		
		if patterns:
			frappe.logger().info(f"Identified {len(patterns)} patterns in AtomSpace")
			
			# Store patterns for future reference
			for pattern in patterns:
				# Could be enhanced to store patterns in database for persistence
				pass
		
	except Exception as e:
		frappe.log_error(f"Pattern recognition cycle error: {str(e)}", "OpenCog Integration")


def sync_erp_entities_to_atomspace():
	"""
	Synchronize ERPNext entities to AtomSpace for cognitive processing
	"""
	settings = get_opencog_settings()
	
	if not settings.get("enabled"):
		return
	
	try:
		atomspace = get_atomspace()
		
		# Sync recent Sales Orders
		recent_sales_orders = frappe.get_all(
			"Sales Order",
			filters={"modified": [">", frappe.utils.add_days(None, -1)]},
			fields=["name", "customer", "status", "grand_total"],
			limit=100,
		)
		
		for so in recent_sales_orders:
			atomspace.store_erp_entity(
				"Sales Order",
				so.name,
				{
					"customer": so.customer,
					"status": so.status,
					"grand_total": so.grand_total,
				},
			)
		
		# Sync recent Purchase Orders
		recent_purchase_orders = frappe.get_all(
			"Purchase Order",
			filters={"modified": [">", frappe.utils.add_days(None, -1)]},
			fields=["name", "supplier", "status", "grand_total"],
			limit=100,
		)
		
		for po in recent_purchase_orders:
			atomspace.store_erp_entity(
				"Purchase Order",
				po.name,
				{
					"supplier": po.supplier,
					"status": po.status,
					"grand_total": po.grand_total,
				},
			)
		
		frappe.logger().info(
			f"Synced {len(recent_sales_orders) + len(recent_purchase_orders)} entities to AtomSpace"
		)
		
	except Exception as e:
		frappe.log_error(f"Entity sync error: {str(e)}", "OpenCog Integration")


def initialize_default_resources():
	"""Initialize default resources for load balancing"""
	try:
		load_balancer = get_load_balancer()
		
		# Register default workers if not already registered
		if not load_balancer.resources:
			# Register accounting worker
			load_balancer.register_resource(
				"accounting_worker_1",
				"accounting_worker",
				{"concurrent_tasks": 10, "cpu": 2, "memory_gb": 4},
			)
			
			# Register inventory worker
			load_balancer.register_resource(
				"inventory_worker_1",
				"inventory_worker",
				{"concurrent_tasks": 15, "cpu": 2, "memory_gb": 4},
			)
			
			# Register manufacturing worker
			load_balancer.register_resource(
				"manufacturing_worker_1",
				"manufacturing_worker",
				{"concurrent_tasks": 8, "cpu": 4, "memory_gb": 8},
			)
			
			frappe.logger().info("Initialized default cognitive resources")
		
	except Exception as e:
		frappe.log_error(f"Resource initialization error: {str(e)}", "OpenCog Integration")
