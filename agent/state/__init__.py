"""
Agent State Management Package - SIMPLIFIED VERSION

This package provides minimal state management for the simplified LangGraph Agent.

Modules:
- types: Simplified AgentState TypedDict definition (no datetime objects, minimal fields)

Usage:
    from agent.state import AgentState
    
    # Create simple state
    state = {
        'user_query': 'Find Python experts',
        'workflow_status': 'initialized',
        'tool_results': [],
        'accumulated_data': []
    }
"""

# Import simplified components
from .types import AgentState

# Export public API
__all__ = [
    'AgentState'
]