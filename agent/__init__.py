"""
Connect Agent Package

A sophisticated intelligent agent system for querying and analyzing people data
using a knowledge graph backed by Neo4j. Features cyclical workflow with intelligent
retry logic, quality assessment, and modular architecture.

Architecture:
- Workflow: LangGraph-based cyclical execution (Planner → Tool Executor → Synthesizer)
- State Management: Comprehensive tracking of queries, retries, and results
- Nodes: Modular components for planning, execution, and synthesis
- MCP Integration: Model Context Protocol for tool communication
"""

from .main_agent import ConnectAgent, agent
from .helpers import (
    ask_sync,
    ask_detailed_sync, 
    batch_ask,
    get_agent_info,
    clear_session,
    get_session_summary
)

__version__ = "1.0.0"
__all__ = [
    "ConnectAgent", 
    "agent",
    "ask_sync",
    "ask_detailed_sync",
    "batch_ask", 
    "get_agent_info",
    "clear_session",
    "get_session_summary"
]