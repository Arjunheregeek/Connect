"""
Workflow Package

Modular LangGraph workflow implementation with cyclical retry logic:

- WorkflowQualityAssessor: Evaluates result quality and usefulness
- RetryManager: Manages retry attempts and failure tracking  
- EnhancedWorkflowNodes: Wrapper nodes with retry and quality logic
- WorkflowGraphBuilder: Constructs the LangGraph workflow
- ConnectWorkflow: Main orchestrator with clean interface

The workflow supports:
- Cyclical execution with up to 2 retries (3 total attempts)
- Intelligent re-planning based on failure analysis
- Quality assessment of results before proceeding
- Comprehensive failure tracking and pattern analysis
"""

from .main_workflow import ConnectWorkflow, connect_workflow
from .graph_builder import WorkflowGraphBuilder
from .quality_assessor import WorkflowQualityAssessor
from .retry_manager import RetryManager
from .workflow_nodes import EnhancedWorkflowNodes

__all__ = [
    'ConnectWorkflow',
    'connect_workflow',
    'WorkflowGraphBuilder', 
    'WorkflowQualityAssessor',
    'RetryManager',
    'EnhancedWorkflowNodes'
]