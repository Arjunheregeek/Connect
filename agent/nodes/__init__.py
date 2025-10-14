"""
Agent Workflow Nodes - ENHANCED VERSION

This package contains enhanced workflow nodes for the LangGraph agent with
intelligent query processing and GPT-4o integration.
"""

# Import enhanced nodes
from .planner.enhanced_planner_node import enhanced_planner_node
from .executor.enhanced_executor_node import enhanced_executor_node
from .synthesizer.enhanced_synthesizer_node import enhanced_synthesizer_node

# Backward compatibility aliases
planner_node = enhanced_planner_node
executor_node = enhanced_executor_node
synthesizer_node = enhanced_synthesizer_node

# Export public API
__all__ = [
    # Enhanced nodes (current)
    'enhanced_planner_node',
    'enhanced_executor_node',
    'enhanced_synthesizer_node',
    
    # Backward compatibility aliases
    'planner_node',
    'executor_node',
    'synthesizer_node',
]
