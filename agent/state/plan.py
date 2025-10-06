"""
Execution Plan Data Structures

This module defines the data structures for managing execution plans,
plan steps, and their lifecycle throughout the agent workflow.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from .enums import PlanStepStatus


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