"""
Agent State Management - Modular Import Facade

This file provides backward compatibility by importing from the modular
state management package. The actual implementation has been split into
organized modules for better maintainability.

For new code, import directly from the state package:
    from agent.state import AgentState, WorkflowStatus, StateManager
"""

# Import everything from the modular state package
from .state import (
    # Enums
    WorkflowStatus,
    PlanStepStatus,
    
    # Data structures  
    PlanStep,
    ExecutionPlan,
    AgentState,
    
    # Utilities
    StateManager
)

# Maintain backward compatibility
__all__ = [
    'WorkflowStatus',
    'PlanStepStatus', 
    'PlanStep',
    'ExecutionPlan',
    'AgentState',
    'StateManager'
]