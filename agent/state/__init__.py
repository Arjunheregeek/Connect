"""
Agent State Management Package

This package provides modular state management for the LangGraph Agent with
clean separation of concerns and maintainable code organization.

Modules:
- enums: Workflow and step status enumerations
- plan: Execution plan and step data structures  
- types: Main AgentState TypedDict definition
- manager: State management utilities and helper functions

Usage:
    from agent.state import AgentState, WorkflowStatus, StateManager
    
    # Create initial state
    state = StateManager.create_initial_state("Find Python experts", "conv-123")
    
    # Update workflow status
    state = StateManager.update_status(state, WorkflowStatus.PLANNING)
    
    # Add tool results
    state = StateManager.add_tool_result(state, "step-1", "find_people_by_skill", 
                                       results, 1.2)
"""

# Import all public components for easy access
from .enums import WorkflowStatus, PlanStepStatus
from .plan import PlanStep, ExecutionPlan
from .types import AgentState
from .manager import StateManager

# Export public API
__all__ = [
    # Enums
    'WorkflowStatus',
    'PlanStepStatus',
    
    # Data structures
    'PlanStep',
    'ExecutionPlan', 
    'AgentState',
    
    # Utilities
    'StateManager'
]