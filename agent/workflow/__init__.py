"""
Workflow Package - ENHANCED VERSION

Enhanced LangGraph workflow implementation with intelligent query processing:

- WorkflowGraphBuilder: Constructs enhanced linear LangGraph workflow

The workflow supports:
- Linear execution: Enhanced Planner → Enhanced Executor → Enhanced Synthesizer → End
- GPT-4o powered query decomposition and sub-query generation
- Priority-based parallel execution with smart aggregation
- Professional response generation with GPT-4o
"""

from .graph_builder import WorkflowGraphBuilder

__all__ = [
    'WorkflowGraphBuilder'
]