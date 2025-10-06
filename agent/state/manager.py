"""
State Management Utilities

This module provides utility functions for managing state transitions,
updates, and common operations while ensuring immutability and validation.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .types import AgentState
from .enums import WorkflowStatus, PlanStepStatus


class StateManager:
    """
    Utility class for managing state transitions and updates.
    
    Provides helper methods for common state operations while ensuring
    immutability and proper state validation.
    """
    
    @staticmethod
    def create_initial_state(user_query: str, conversation_id: str) -> AgentState:
        """
        Create initial state for a new agent execution.
        
        Args:
            user_query: The user's question or request
            conversation_id: Unique identifier for this conversation
            
        Returns:
            Initialized AgentState ready for the Planner node
        """
        return AgentState(
            user_query=user_query,
            conversation_id=conversation_id,
            workflow_status=WorkflowStatus.INITIALIZED,
            created_at=datetime.now(),
            tool_results=[],
            errors=[],
            warnings=[],
            recovery_attempts=0
        )
    
    @staticmethod
    def update_status(state: AgentState, new_status: WorkflowStatus) -> AgentState:
        """
        Update workflow status with proper timestamp tracking.
        
        Args:
            state: Current agent state
            new_status: New workflow status
            
        Returns:
            Updated state with new status and timestamp
        """
        updated_state = state.copy()
        updated_state["workflow_status"] = new_status
        updated_state["updated_at"] = datetime.now()
        return updated_state
    
    @staticmethod
    def add_tool_result(
        state: AgentState, 
        step_id: str, 
        tool_name: str, 
        result: Any, 
        execution_time: float
    ) -> AgentState:
        """
        Add a tool execution result to state.
        
        Args:
            state: Current agent state
            step_id: ID of the executed step
            tool_name: Name of the MCP tool that was called
            result: Tool execution result
            execution_time: Time taken for execution
            
        Returns:
            Updated state with new tool result
        """
        updated_state = state.copy()
        
        # Add to tool results list
        if "tool_results" not in updated_state:
            updated_state["tool_results"] = []
        
        tool_result = {
            "step_id": step_id,
            "tool_name": tool_name,
            "result": result,
            "execution_time": execution_time,
            "timestamp": datetime.now()
        }
        updated_state["tool_results"].append(tool_result)
        
        # Update execution plan step status if plan exists
        if "execution_plan" in updated_state:
            plan = updated_state["execution_plan"]
            step = plan.get_step_by_id(step_id)
            if step:
                step.result = result
                step.execution_time = execution_time
                step.timestamp = datetime.now()
                step.status = PlanStepStatus.COMPLETED
        
        updated_state["updated_at"] = datetime.now()
        return updated_state
    
    @staticmethod
    def add_error(
        state: AgentState, 
        error_type: str, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentState:
        """
        Add an error to state with proper context.
        
        Args:
            state: Current agent state
            error_type: Type/category of error
            message: Error message
            context: Additional error context
            
        Returns:
            Updated state with error information
        """
        updated_state = state.copy()
        
        if "errors" not in updated_state:
            updated_state["errors"] = []
        
        error_entry = {
            "type": error_type,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now(),
            "workflow_status": updated_state["workflow_status"]
        }
        updated_state["errors"].append(error_entry)
        updated_state["updated_at"] = datetime.now()
        
        return updated_state
    
    @staticmethod
    def is_ready_for_synthesis(state: AgentState) -> bool:
        """
        Check if state has enough information for final synthesis.
        
        Args:
            state: Current agent state
            
        Returns:
            True if ready for Synthesizer node
        """
        # Must have completed execution plan or sufficient tool results
        if "execution_plan" in state:
            return state["execution_plan"].is_complete()
        
        # Fallback: check if we have any tool results
        tool_results = state.get("tool_results", [])
        return len(tool_results) > 0
    
    @staticmethod
    def get_execution_summary(state: AgentState) -> Dict[str, Any]:
        """
        Generate execution summary for debugging and analytics.
        
        Args:
            state: Current agent state
            
        Returns:
            Summary of execution metrics and status
        """
        tool_results = state.get("tool_results", [])
        errors = state.get("errors", [])
        
        total_execution_time = sum(
            result.get("execution_time", 0) for result in tool_results
        )
        
        return {
            "workflow_status": state["workflow_status"],
            "total_tools_executed": len(tool_results),
            "total_execution_time": total_execution_time,
            "error_count": len(errors),
            "has_plan": "execution_plan" in state,
            "plan_complete": (
                state["execution_plan"].is_complete() 
                if "execution_plan" in state else False
            ),
            "created_at": state["created_at"],
            "updated_at": state.get("updated_at"),
            "conversation_id": state["conversation_id"]
        }