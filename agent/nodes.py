"""
Workflow Nodes - Backward Compatibility Facade

This file provides backward compatibility by importing from the modular
nodes package. The actual implementation has been split into organized
modules for better maintainability.

For new code, import directly from the nodes package:
    from agent.nodes import planner_node, tool_executor_node, synthesizer_node
"""

# Import everything from the modular nodes package
from .nodes import (
    # Main node functions
    planner_node,
    tool_executor_node,
    synthesizer_node,
    
    # Component classes
    QueryAnalyzer,
    ToolMapper, 
    PlanGenerator,
    PlanValidator,
    ToolExecutor,
    ResultAggregator,
    DataAnalyzer,
    ResponseGenerator,
    QualityAssessor,
    NodeUtils,
    ErrorHandler,
    PerformanceMonitor
)

# Maintain backward compatibility
__all__ = [
    'planner_node',
    'tool_executor_node',
    'synthesizer_node',
    'QueryAnalyzer',
    'ToolMapper',
    'PlanGenerator', 
    'PlanValidator',
    'ToolExecutor',
    'ResultAggregator',
    'DataAnalyzer',
    'ResponseGenerator',
    'QualityAssessor',
    'NodeUtils',
    'ErrorHandler',
    'PerformanceMonitor'
]