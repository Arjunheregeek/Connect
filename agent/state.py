"""
Agent State Management for Single Stateful LangGraph Agent

This module defines the state structures that persist throughout the agent's
execution lifecycle. The state tracks user queries, execution plans, tool results,
and workflow status across all three nodes: Planner → Tool Executor → Synthesizer.

Key Design Principles:
- Immutable state updates (TypedDict with proper copying)
- Rich metadata for debugging and analytics
- Clear separation of concerns between workflow phases
- Comprehensive error and status tracking
"""

from typing import Dict, List, Any, Optional, Union, Literal
from typing_extensions import TypedDict, NotRequired
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    """Current status of the agent workflow"""
    INITIALIZED = "initialized"           # State created, ready to start
    PLANNING = "planning"                 # Planner node active
    PLAN_READY = "plan_ready"            # Plan created, ready for execution
    EXECUTING_TOOLS = "executing_tools"   # Tool Executor node active
    TOOLS_COMPLETE = "tools_complete"     # All tools completed
    SYNTHESIZING = "synthesizing"         # Synthesizer node active
    COMPLETED = "completed"               # Final response ready
    ERROR = "error"                       # Error occurred, workflow stopped

class PlanStepStatus(str, Enum):
    """Status of individual plan steps"""
    PENDING = "pending"         # Not yet started
    EXECUTING = "executing"     # Currently running
    COMPLETED = "completed"     # Successfully finished
    FAILED = "failed"          # Failed with error
    SKIPPED = "skipped"        # Skipped due to dependencies

@dataclass
class PlanStep:
    """
    Individual step in the execution plan.
    
    Each step represents a specific MCP tool call with its parameters,
    rationale, and execution status.
    """
    id: str                                    # Unique step identifier
    tool_name: str                            # MCP tool to call
    arguments: Dict[str, Any]                 # Tool arguments
    rationale: str                            # Why this step is needed
    expected_output: str                      # What we expect to get
    status: PlanStepStatus = PlanStepStatus.PENDING
    
    # Execution results
    result: Optional[Any] = None              # Tool execution result
    error: Optional[str] = None               # Error message if failed
    execution_time: Optional[float] = None    # Time taken to execute
    timestamp: Optional[datetime] = None      # When executed
    
    # Dependencies and flow control
    depends_on: List[str] = field(default_factory=list)  # Step IDs this depends on
    critical: bool = True                     # If False, failure won't stop workflow

@dataclass 
class ExecutionPlan:
    """
    Complete execution plan created by the Planner node.
    
    Contains the strategy, steps, and metadata for how to approach
    the user's query using available MCP tools.
    """
    strategy: str                             # High-level approach description
    steps: List[PlanStep]                     # Ordered list of execution steps
    estimated_time: float                     # Estimated execution time
    confidence: float                         # Planner's confidence (0.0-1.0)
    fallback_strategy: Optional[str] = None   # Alternative approach if main fails
    
    # Execution tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next pending step that's ready to execute"""
        for step in self.steps:
            if step.status == PlanStepStatus.PENDING:
                # Check if all dependencies are completed
                if all(self.get_step_by_id(dep_id).status == PlanStepStatus.COMPLETED 
                       for dep_id in step.depends_on):
                    return step
        return None
    
    def get_step_by_id(self, step_id: str) -> Optional[PlanStep]:
        """Find a step by its ID"""
        return next((step for step in self.steps if step.id == step_id), None)
    
    def is_complete(self) -> bool:
        """Check if all critical steps are completed or all steps are done"""
        critical_steps = [s for s in self.steps if s.critical]
        return all(s.status in [PlanStepStatus.COMPLETED, PlanStepStatus.SKIPPED] 
                  for s in critical_steps)
    
    def has_failures(self) -> bool:
        """Check if any critical steps have failed"""
        return any(s.status == PlanStepStatus.FAILED and s.critical for s in self.steps)

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

# =================================================================
# STATE MANAGEMENT UTILITIES
# =================================================================

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