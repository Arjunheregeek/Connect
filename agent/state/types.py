"""
Agent State TypedDict Definition

This module defines the main AgentState TypedDict structure that is passed
between workflow nodes and maintains the complete context of agent execution.
"""

from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime

from .enums import WorkflowStatus
from .plan import ExecutionPlan


class AgentState(TypedDict, total=False):
    """
    Main state structure for the Single Stateful LangGraph Agent.
    
    This TypedDict is passed between all workflow nodes and maintains
    the complete context of the agent's execution.
    
    Using total=False makes all fields optional by default, which works
    better with LangGraph's state management.
    """
    
    # =================================================================
    # USER INPUT AND CONTEXT
    # =================================================================
    user_query: str                           # Original user question/request
    conversation_id: str                      # Unique conversation identifier
    message_history: List[Dict[str, Any]]     # Previous messages in conversation
    user_context: Dict[str, Any]              # Additional user context/preferences
    
    # =================================================================
    # EXECUTION PLAN AND WORKFLOW
    # =================================================================
    workflow_status: WorkflowStatus           # Current workflow phase
    execution_plan: ExecutionPlan             # Complete execution plan
    current_step_id: str                      # ID of currently executing step
    
    # =================================================================
    # LANGGRAPH INTEGRATION
    # =================================================================
    messages: List[Dict[str, Any]]            # LangGraph message chain
    session_id: str                           # Session identifier
    planning_rounds: int                      # Number of planning iterations
    tools_used: List[str]                     # List of tools called
    synthesis_attempts: int                   # Number of synthesis attempts
    retry_count: int                          # Number of workflow retries
    
    # =================================================================
    # TOOL EXECUTION RESULTS
    # =================================================================
    tool_results: List[Dict[str, Any]]        # All tool execution results
    accumulated_data: Dict[str, Any]          # Processed/aggregated data
    intermediate_insights: List[str]          # Insights discovered during execution
    
    # =================================================================
    # FINAL OUTPUT
    # =================================================================
    final_response: str                       # Synthesized final response
    response_metadata: Dict[str, Any]         # Response confidence, sources, etc.
    
    # =================================================================
    # ERROR HANDLING AND RECOVERY
    # =================================================================
    errors: List[Dict[str, Any]]              # All errors encountered
    warnings: List[str]                       # Non-critical warnings
    recovery_attempts: int                    # Number of recovery attempts made
    
    # =================================================================
    # METADATA AND ANALYTICS
    # =================================================================
    workflow_version: str                     # Version of workflow used
    created_at: datetime                      # When state was initialized
    updated_at: datetime                      # Last state update
    execution_metrics: Dict[str, float]       # Performance metrics
    debug_info: Dict[str, Any]                # Debug information