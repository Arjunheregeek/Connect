"""
Agent Workflow Nodes - SIMPLIFIED VERSION

This package contains simplified workflow nodes for the LangGraph agent that avoid
all the problematic complexity that was causing import and execution failures.
"""

# SIMPLIFIED: Import simplified node functions that actually work
from .planner.simple_planner import simple_planner_node
from .executor.simple_executor import simple_executor_node
from .synthesizer.simple_synthesizer import simple_synthesizer_node

# Alias simplified nodes to the expected names for backward compatibility
planner_node = simple_planner_node
tool_executor_node = simple_executor_node
synthesizer_node = simple_synthesizer_node

# Try to import utils but don't fail if they don't exist
try:
    from .utils import NodeUtils
except ImportError:
    NodeUtils = None

# Export public API - simplified version
__all__ = [
    # Main workflow node functions (simplified versions that work)
    'planner_node',
    'tool_executor_node',
    'synthesizer_node',
    'simple_planner_node',
    'simple_executor_node', 
    'simple_synthesizer_node'
]