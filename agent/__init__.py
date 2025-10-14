"""
Connect Agent Package - ENHANCED VERSION

A production-ready intelligent agent system for querying the professional
network knowledge graph via MCP protocol with GPT-4o integration.

Architecture:
- Workflow: Enhanced linear LangGraph execution (Enhanced Planner → Enhanced Executor → Enhanced Synthesizer)
- Query Processing: GPT-4o powered query decomposition and sub-query generation
- Execution: Priority-based parallel execution with smart aggregation
- Synthesis: GPT-4o powered professional response generation
- MCP Integration: Async MCP client with 19 tools
"""

from .workflow.graph_builder import WorkflowGraphBuilder
__version__ = "3.0.0"
__all__ = [
    "WorkflowGraphBuilder"
]