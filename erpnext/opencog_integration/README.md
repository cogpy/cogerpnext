# OpenCog Integration for ERPNext

This module implements OpenCog as an autonomous orchestrating and load-balancing cognitive architecture for optimization of ERPNext Enterprise Resource Planning.

## Overview

The OpenCog integration provides:

1. **Cognitive Orchestration**: Autonomous task management and workflow optimization using cognitive principles
2. **Intelligent Load Balancing**: Resource allocation based on learned patterns and real-time metrics
3. **Knowledge Representation**: AtomSpace-based hypergraph for storing and reasoning about ERP entities
4. **Pattern Recognition**: Automatic discovery of patterns in business processes
5. **Autonomous Operation**: Background tasks for continuous optimization

## Architecture

### Components

#### 1. AtomSpace Manager (`atomspace_manager.py`)
Manages the hypergraph knowledge representation system that stores ERPNext entities, relationships, and patterns.

**Key Features:**
- Node and link creation for knowledge representation
- Attention value management (STI/LTI)
- Pattern finding and mining
- ERP entity storage and retrieval

#### 2. Cognitive Orchestrator (`cognitive_orchestrator.py`)
Autonomous orchestrator for task management and workflow optimization.

**Key Features:**
- Task registration and prioritization
- Dependency-aware task scheduling
- Cognitive task ordering optimization
- Workload analysis and recommendations
- Learning from task execution

#### 3. Cognitive Load Balancer (`load_balancer.py`)
Intelligent load balancer that distributes workload across resources using cognitive decision-making.

**Key Features:**
- Resource registration and management
- Suitability score calculation for task-resource matching
- Dynamic load rebalancing
- Performance metrics tracking
- Resource specialization support

## Installation

The OpenCog integration is automatically initialized when ERPNext is installed or migrated. Default cognitive resources are created during initialization.

## Usage

### API Endpoints

All API endpoints are accessible via Frappe's REST API:

#### Get Cognitive Status
```python
frappe.call({
    method: "erpnext.opencog_integration.api.get_cognitive_status",
    callback: function(r) {
        console.log(r.message);
    }
});
```

#### Register a Task
```python
frappe.call({
    method: "erpnext.opencog_integration.api.register_task",
    args: {
        task_type: "sales_order",
        task_data: {
            doc_name: "SO-001",
            action: "process"
        },
        priority: 7
    },
    callback: function(r) {
        console.log("Task ID:", r.message.task_id);
    }
});
```

#### Get Workload Analysis
```python
frappe.call({
    method: "erpnext.opencog_integration.api.get_workload_analysis",
    callback: function(r) {
        console.log("Analysis:", r.message);
    }
});
```

#### Register a Resource
```python
frappe.call({
    method: "erpnext.opencog_integration.api.register_resource",
    args: {
        resource_id: "worker_3",
        resource_type: "accounting_worker",
        capacity: {
            concurrent_tasks: 10,
            cpu: 2,
            memory_gb: 4
        }
    },
    callback: function(r) {
        console.log("Resource registered:", r.message);
    }
});
```

#### Trigger Load Rebalancing
```python
frappe.call({
    method: "erpnext.opencog_integration.api.trigger_rebalancing",
    callback: function(r) {
        console.log("Rebalancing result:", r.message);
    }
});
```

### Scheduler Tasks

The integration includes several scheduled tasks:

1. **Cognitive Optimization Cycle** (every 5 minutes)
   - Analyzes workload
   - Executes high-priority tasks
   - Performs load rebalancing
   - Updates attention values

2. **Pattern Recognition Cycle** (hourly)
   - Identifies patterns in AtomSpace
   - Logs discovered patterns

3. **ERP Entity Synchronization** (hourly)
   - Syncs recent Sales Orders and Purchase Orders to AtomSpace
   - Enables cognitive reasoning about business entities

## Configuration

Configuration can be done through the OpenCog Settings doctype (to be created) or by directly using the config module:

```python
from erpnext.opencog_integration.config import get_opencog_settings, get_default_settings

# Get current settings
settings = get_opencog_settings()

# Get default settings
defaults = get_default_settings()
```

### Configuration Options

- `enabled`: Enable/disable OpenCog integration
- `auto_orchestration`: Enable autonomous task orchestration
- `load_balancing_enabled`: Enable cognitive load balancing
- `learning_rate`: Rate at which system learns from executions (0-1)
- `attention_decay_rate`: Rate at which attention values decay (0-1)
- `max_concurrent_tasks`: Maximum tasks to process concurrently
- `cognitive_optimization_interval`: Interval for optimization cycle (seconds)
- `pattern_recognition_threshold`: Minimum occurrences for pattern recognition
- `rebalancing_threshold`: Utilization threshold for triggering rebalancing (0-1)

## Testing

Run the test suite:

```bash
# Run all OpenCog integration tests
bench --site [site-name] run-tests --module erpnext.opencog_integration

# Run specific test file
bench --site [site-name] run-tests --module erpnext.opencog_integration.test_atomspace_manager
bench --site [site-name] run-tests --module erpnext.opencog_integration.test_cognitive_orchestrator
bench --site [site-name] run-tests --module erpnext.opencog_integration.test_load_balancer
```

## Monitoring

### Get System Status

```python
from erpnext.opencog_integration.api import get_orchestrator, get_load_balancer, get_atomspace

orchestrator = get_orchestrator()
print(orchestrator.get_status())

load_balancer = get_load_balancer()
print(load_balancer.get_load_distribution())

atomspace = get_atomspace()
print(atomspace.get_statistics())
```

## Advanced Usage

### Custom Task Types

Register custom task types with specialized handling:

```python
from erpnext.opencog_integration.api import get_orchestrator

orchestrator = get_orchestrator()
task_id = orchestrator.register_task(
    "custom_optimization",
    {
        "target": "inventory",
        "parameters": {"threshold": 100},
        "estimated_duration": 120
    },
    priority=8
)
```

### Resource Specialization

Register specialized resources for specific task types:

```python
from erpnext.opencog_integration.api import get_load_balancer

load_balancer = get_load_balancer()
load_balancer.register_resource(
    "specialized_worker",
    "manufacturing_worker",  # Specialized for manufacturing tasks
    {
        "concurrent_tasks": 8,
        "cpu": 4,
        "memory_gb": 8,
        "specialization": ["work_order", "bom", "job_card"]
    }
)
```

## Performance Considerations

1. **AtomSpace Size**: The in-memory AtomSpace can grow large. Consider implementing persistence or periodic cleanup.
2. **Optimization Frequency**: The 5-minute optimization cycle can be adjusted based on system load.
3. **Resource Allocation**: Ensure adequate resources are registered to handle peak workloads.
4. **Pattern Recognition**: Pattern mining can be CPU-intensive for large AtomSpaces.

## Future Enhancements

- Persistent AtomSpace storage (Redis/database)
- Advanced reasoning algorithms (PLN - Probabilistic Logic Networks)
- Integration with ERPNext UI for visualization
- Machine learning for better task time estimation
- Distributed AtomSpace for scalability
- Custom DocType for OpenCog Settings

## License

This integration is part of ERPNext and follows the same GNU General Public License (v3).

## References

- [OpenCog Framework](https://opencog.org/)
- [AtomSpace Documentation](https://wiki.opencog.org/w/AtomSpace)
- [ERPNext Documentation](https://docs.erpnext.com/)
