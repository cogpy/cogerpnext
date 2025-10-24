"""
Configuration settings for OpenCog Integration
"""

import frappe


def get_opencog_settings():
	"""Get OpenCog integration settings"""
	return {
		"enabled": frappe.db.get_single_value("OpenCog Settings", "enabled") or False,
		"auto_orchestration": frappe.db.get_single_value("OpenCog Settings", "auto_orchestration")
		or False,
		"load_balancing_enabled": frappe.db.get_single_value(
			"OpenCog Settings", "load_balancing_enabled"
		)
		or False,
		"learning_rate": frappe.db.get_single_value("OpenCog Settings", "learning_rate") or 0.1,
		"attention_decay_rate": frappe.db.get_single_value("OpenCog Settings", "attention_decay_rate")
		or 0.05,
		"max_concurrent_tasks": frappe.db.get_single_value("OpenCog Settings", "max_concurrent_tasks")
		or 10,
	}


def get_default_settings():
	"""Get default OpenCog settings"""
	return {
		"enabled": True,
		"auto_orchestration": True,
		"load_balancing_enabled": True,
		"learning_rate": 0.1,
		"attention_decay_rate": 0.05,
		"max_concurrent_tasks": 10,
		"cognitive_optimization_interval": 300,  # seconds
		"pattern_recognition_threshold": 5,
		"rebalancing_threshold": 0.8,
	}


def validate_settings(settings):
	"""Validate OpenCog settings"""
	errors = []
	
	if settings.get("learning_rate", 0) < 0 or settings.get("learning_rate", 0) > 1:
		errors.append("Learning rate must be between 0 and 1")
	
	if settings.get("attention_decay_rate", 0) < 0 or settings.get("attention_decay_rate", 0) > 1:
		errors.append("Attention decay rate must be between 0 and 1")
	
	if settings.get("max_concurrent_tasks", 0) < 1:
		errors.append("Maximum concurrent tasks must be at least 1")
	
	return errors
