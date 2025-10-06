"""
Agent State TypedDict Definition

This module defines the main AgentState TypedDict structure that is passed
between workflow nodes and maintains the complete context of agent execution.
"""

from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict, NotRequired
from datetime import datetime

from .enums import WorkflowStatus
from .plan import ExecutionPlan


class AgentState(TypedDict):
    """
    Main state structure for the Single Stateful LangGraph Agent.
    
    This TypedDict is passed between all workflow nodes and maintains
    the complete context of the agent's execution.
    """
    
    # =================================================================
    # USER INPUT AND CONTEXT
    # =================================================================
    user_query: str                           # Original user question/request
    conversation_id: str                      # Unique conversation identifier
    message_history: NotRequired[List[Dict[str, Any]]]  # Previous messages in conversation
    user_context: NotRequired[Dict[str, Any]] # Additional user context/preferences
    
    # =================================================================
    # EXECUTION PLAN AND WORKFLOW
    # =================================================================
    workflow_status: WorkflowStatus          # Current workflow phase
    execution_plan: NotRequired[ExecutionPlan]  # Complete execution plan
    current_step_id: NotRequired[str]        # ID of currently executing step
    
    # =================================================================
    # TOOL EXECUTION RESULTS
    # =================================================================
    tool_results: NotRequired[List[Dict[str, Any]]]     # All tool execution results
    accumulated_data: NotRequired[Dict[str, Any]]       # Processed/aggregated data
    intermediate_insights: NotRequired[List[str]]       # Insights discovered during execution
    
    # =================================================================
    # FINAL OUTPUT
    # =================================================================
    final_response: NotRequired[str]          # Synthesized final response
    response_metadata: NotRequired[Dict[str, Any]]  # Response confidence, sources, etc.
    
    # =================================================================
    # ERROR HANDLING AND RECOVERY
    # =================================================================
    errors: NotRequired[List[Dict[str, Any]]] # All errors encountered
    warnings: NotRequired[List[str]]          # Non-critical warnings
    recovery_attempts: NotRequired[int]       # Number of recovery attempts made
    
    # =================================================================
    # METADATA AND ANALYTICS
    # =================================================================
    created_at: datetime                      # When state was initialized
    updated_at: NotRequired[datetime]         # Last state update
    execution_metrics: NotRequired[Dict[str, float]]  # Performance metrics
    debug_info: NotRequired[Dict[str, Any]]   # Debug information