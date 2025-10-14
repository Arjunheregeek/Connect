"""
Agent State TypedDict Definition - SIMPLIFIED VERSION

This module defines a simplified AgentState TypedDict structure that avoids
serialization issues with LangGraph by removing datetime objects and complex types.
"""

from typing import Dict, List, Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """
    SIMPLIFIED state structure for the LangGraph Agent.
    
    Removed problematic fields that cause LangGraph serialization issues:
    - datetime objects (created_at, updated_at)
    - Complex nested Any types (debug_info, execution_metrics)
    - Over-engineered retry/quality assessment fields
    
    This minimal version focuses on getting basic Planning → Execution → Synthesis working.
    """
    
    # =================================================================
    # USER INPUT AND CONTEXT (ESSENTIAL)
    # =================================================================
    user_query: str                           # Original user question/request
    conversation_id: str                      # Unique conversation identifier
    
    # =================================================================
    # EXECUTION PLAN AND WORKFLOW (ESSENTIAL)
    # =================================================================
    workflow_status: str                      # Current workflow phase (simplified to string)
    
    # Enhanced Planning Fields (QueryDecomposer + SubQueryGenerator)
    filters: Dict[str, Any]                   # Extracted filters from QueryDecomposer
    sub_queries: List[Dict[str, Any]]         # Sub-queries with tool mappings from SubQueryGenerator
    execution_strategy: str                   # parallel_intersect | parallel_union | sequential
    planning_metadata: Dict[str, Any]         # Planning metadata (tokens, counts, etc.)
    
    # =================================================================
    # LANGGRAPH INTEGRATION (ESSENTIAL)
    # =================================================================
    messages: List[Dict[str, str]]            # LangGraph message chain (simplified)
    session_id: str                           # Session identifier
    tools_used: List[str]                     # List of tools called
    
    # =================================================================
    # TOOL EXECUTION RESULTS (ESSENTIAL)
    # =================================================================
    tool_results: List[Dict[str, Any]]        # All tool execution results
    accumulated_data: List[Any]               # Processed/aggregated data (simplified)
    
    # =================================================================
    # FINAL OUTPUT (ESSENTIAL)
    # =================================================================
    final_response: str                       # Synthesized final response
    
    # =================================================================
    # ERROR HANDLING (MINIMAL)
    # =================================================================
    errors: List[str]                         # Simple error messages
    
    # COMMENTED OUT - COMPLEX FIELDS THAT CAUSE LANGGRAPH ISSUES
    # =================================================================
    # message_history: List[Dict[str, Any]]     # Previous messages in conversation
    # user_context: Dict[str, Any]              # Additional user context/preferences
    # current_step_id: str                      # ID of currently executing step
    # planning_rounds: int                      # Number of planning iterations
    # synthesis_attempts: int                   # Number of synthesis attempts
    # retry_count: int                          # Number of workflow retries
    # intermediate_insights: List[str]          # Insights discovered during execution
    # response_metadata: Dict[str, Any]         # Response confidence, sources, etc.
    # warnings: List[str]                       # Non-critical warnings
    # recovery_attempts: int                    # Number of recovery attempts made
    # workflow_version: str                     # Version of workflow used
    # created_at: datetime                      # ❌ SERIALIZATION PROBLEM
    # updated_at: datetime                      # ❌ SERIALIZATION PROBLEM
    # execution_metrics: Dict[str, float]       # ❌ SERIALIZATION PROBLEM
    # debug_info: Dict[str, Any]                # ❌ SERIALIZATION PROBLEM