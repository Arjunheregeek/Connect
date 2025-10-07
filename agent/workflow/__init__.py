"""
Workflow Package - SIMPLIFIED VERSION

Simple LangGraph workflow implementation without complex retry logic:

- WorkflowGraphBuilder: Constructs simple linear LangGraph workflow

The workflow supports:
- Linear execution: Planner → Executor → Synthesizer → End
- No retry cycles, no quality assessment complexity
- Direct MCP tool execution
"""

from .graph_builder import WorkflowGraphBuilder

__all__ = [
    'WorkflowGraphBuilder'
]