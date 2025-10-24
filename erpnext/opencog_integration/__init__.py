"""
OpenCog Integration for ERPNext
Provides autonomous orchestrating and load-balancing cognitive architecture
"""

__version__ = "1.0.0"

from .cognitive_orchestrator import CognitiveOrchestrator
from .load_balancer import CognitiveLoadBalancer
from .atomspace_manager import AtomSpaceManager

__all__ = [
	"CognitiveOrchestrator",
	"CognitiveLoadBalancer",
	"AtomSpaceManager",
]
