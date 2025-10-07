"""
Connect Agent Workflow

Main entry point for the Connect Agent workflow system.
Imports the modular workflow implementation.
"""

from .workflow import connect_workflow, ConnectWorkflow

# Export the main workflow instance and class
__all__ = ['connect_workflow', 'ConnectWorkflow']