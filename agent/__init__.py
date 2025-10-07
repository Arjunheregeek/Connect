"""
Connect Agent Package - SIMPLIFIED VERSION

A simplified, working intelligent agent system for querying the professional
network knowledge graph via MCP protocol.

Architecture:
- Workflow: Simple linear LangGraph execution (Planner → Executor → Synthesizer)
- State Management: Minimal state tracking for reliability
- Nodes: Simplified nodes that actually work without complex retry cycles
- MCP Integration: Direct MCP client for tool communication
"""

from .workflow.graph_builder import WorkflowGraphBuilder
__version__ = "1.0.0"
__all__ = [
    "WorkflowGraphBuilder"
]