// Cognitive Dashboard JavaScript
// Provides interactive UI for monitoring cognitive system

frappe.pages['cognitive-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Cognitive Dashboard',
		single_column: true
	});
	
	page.add_inner_button(__('Refresh'), function() {
		load_dashboard_data(page);
	});
	
	page.add_inner_button(__('Trigger Rebalancing'), function() {
		trigger_rebalancing(page);
	});
	
	// Initial load
	load_dashboard_data(page);
	
	// Auto-refresh every 30 seconds
	setInterval(function() {
		load_dashboard_data(page);
	}, 30000);
}

function load_dashboard_data(page) {
	frappe.call({
		method: 'erpnext.opencog_integration.page.cognitive_dashboard.cognitive_dashboard.get_dashboard_data',
		callback: function(r) {
			if (r.message && r.message.success) {
				render_dashboard(page, r.message);
			} else {
				frappe.msgprint(__('Failed to load dashboard data'));
			}
		}
	});
}

function render_dashboard(page, data) {
	let html = `
		<div class="cognitive-dashboard">
			<h3>System Status</h3>
			<div class="row">
				<div class="col-md-4">
					<div class="card">
						<div class="card-body">
							<h5 class="card-title">Orchestrator</h5>
							<p>Pending Tasks: ${data.orchestrator.status.pending_tasks}</p>
							<p>Active Tasks: ${data.orchestrator.status.active_tasks}</p>
							<p>Completed Tasks: ${data.orchestrator.status.completed_tasks}</p>
						</div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="card">
						<div class="card-body">
							<h5 class="card-title">Load Balancer</h5>
							<p>Total Resources: ${data.load_balancer.distribution.total_resources}</p>
							<p>Average Utilization: ${data.load_balancer.distribution.average_utilization.toFixed(2)}%</p>
							<p>Total Allocations: ${data.load_balancer.distribution.total_allocations}</p>
						</div>
					</div>
				</div>
				<div class="col-md-4">
					<div class="card">
						<div class="card-body">
							<h5 class="card-title">AtomSpace</h5>
							<p>Total Atoms: ${data.atomspace.statistics.total_atoms}</p>
							<p>Total Links: ${data.atomspace.statistics.total_links}</p>
							<p>Avg STI: ${data.atomspace.statistics.avg_sti.toFixed(2)}</p>
						</div>
					</div>
				</div>
			</div>
			
			<h3>Workload Analysis</h3>
			<div class="row">
				<div class="col-md-12">
					<div class="card">
						<div class="card-body">
							<p>Estimated Completion Time: ${data.orchestrator.workload.estimated_completion_time_seconds} seconds</p>
							<h6>Task Distribution:</h6>
							<ul>
								${Object.entries(data.orchestrator.workload.task_distribution || {}).map(([type, count]) => 
									`<li>${type}: ${count}</li>`
								).join('')}
							</ul>
							<h6>Recommendations:</h6>
							<ul>
								${(data.orchestrator.workload.recommendations || []).map(rec => 
									`<li>${rec}</li>`
								).join('')}
							</ul>
						</div>
					</div>
				</div>
			</div>
			
			<h3>Resource Distribution</h3>
			<div class="row">
				<div class="col-md-12">
					<table class="table table-bordered">
						<thead>
							<tr>
								<th>Resource ID</th>
								<th>Type</th>
								<th>Current Load</th>
								<th>Capacity</th>
								<th>Utilization</th>
								<th>Status</th>
							</tr>
						</thead>
						<tbody>
							${(data.load_balancer.distribution.resources || []).map(r => `
								<tr>
									<td>${r.resource_id}</td>
									<td>${r.type}</td>
									<td>${r.current_load}</td>
									<td>${r.capacity}</td>
									<td>${r.utilization_percent.toFixed(2)}%</td>
									<td><span class="badge badge-${r.status === 'available' ? 'success' : 'warning'}">${r.status}</span></td>
								</tr>
							`).join('')}
						</tbody>
					</table>
				</div>
			</div>
			
			<p class="text-muted"><small>Last updated: ${data.timestamp}</small></p>
		</div>
	`;
	
	page.main.html(html);
}

function trigger_rebalancing(page) {
	frappe.call({
		method: 'erpnext.opencog_integration.api.trigger_rebalancing',
		callback: function(r) {
			if (r.message) {
				if (r.message.rebalanced) {
					frappe.msgprint(__('Load rebalancing triggered successfully'));
				} else {
					frappe.msgprint(__('No rebalancing needed'));
				}
				load_dashboard_data(page);
			}
		}
	});
}
