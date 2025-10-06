"""
Workflow Status Enums for Agent State Management

This module defines the status enums used throughout the agent workflow
to track the current phase and individual step statuses.
"""

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