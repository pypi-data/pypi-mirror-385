"""
OutcomeForge Core - Registry and Discovery Mechanisms
"""

from .registry import NodeRegistry, node_registry
from .scenario_loader import ScenarioLoader
from .scenario_registry import ScenarioRegistry
from .context_integration import ContextInjector, inject_context_to_scenario_run
from .template_generator import NodeTemplateGenerator, ScenarioTemplateGenerator
from .config import ConfigManager, config_manager

# Create global scenario registry instance
scenario_registry = ScenarioRegistry(node_registry)

__all__ = [
    'NodeRegistry',
    'node_registry',
    'ScenarioLoader',
    'ScenarioRegistry',
    'scenario_registry',
    'ContextInjector',
    'inject_context_to_scenario_run',
    'NodeTemplateGenerator',
    'ScenarioTemplateGenerator',
    'ConfigManager',
    'config_manager'
]
