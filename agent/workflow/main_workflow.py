"""
Main Workflow Orchestrator

Simple, clean interface for running the Connect Agent workflow.
"""

import uuid
from typing import Optional
from datetime import datetime

from agent.state import AgentState, WorkflowStatus, StateManager
from .graph_builder import WorkflowGraphBuilder


class ConnectWorkflow:
    """
    Main workflow orchestrator for the Connect Agent.
    
    Provides a clean interface for running queries through the cyclical
    workflow with intelligent retry logic.
    """
    
    def __init__(self):
        """Initialize the workflow with compiled graph."""
        self.graph = WorkflowGraphBuilder.build_graph()
        self.max_attempts = 3
    
    async def run(self, user_query: str, conversation_id: Optional[str] = None) -> AgentState:
        """
        Run the complete workflow for a user query.
        
        Args:
            user_query: The user's query string
            conversation_id: Optional conversation ID for context tracking
            
        Returns:
            Final AgentState with response and metadata
        """
        
        # Initialize state
        initial_state: AgentState = {
            'conversation_id': conversation_id or str(uuid.uuid4()),
            'user_query': user_query,
            'workflow_status': WorkflowStatus.INITIALIZED,
            'messages': [],
            'accumulated_data': [],
            'tool_results': [],
            'errors': [],
            'session_id': str(uuid.uuid4()),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'retry_info': {
                'attempt_count': 1,
                'max_retries': 2,
                'previous_failures': [],
                'tools_already_tried': [],
                'strategies_tried': []
            },
            'tools_used': [],
            'retry_count': 0,
            'planning_rounds': 0,
            'synthesis_attempts': 0,
            'workflow_version': '1.0.0'
        }
        
        try:
            # Run the workflow with increased recursion limit
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"recursion_limit": 10}  # Reasonable limit for 2 retries
            )
            
            # Ensure we have a final response
            if 'final_response' not in final_state:
                final_state = self._create_emergency_fallback(final_state)
            
            # Update final timestamp
            final_state['updated_at'] = datetime.now()
            
            return final_state
            
        except Exception as e:
            # Handle unexpected workflow errors
            return self._handle_workflow_error(initial_state, e)
    
    def _create_emergency_fallback(self, state: AgentState) -> AgentState:
        """
        Create an emergency fallback response when workflow completes without a response.
        
        Args:
            state: Current state without final_response
            
        Returns:
            State with emergency fallback response
        """
        
        error_state = StateManager.add_error(
            state,
            'missing_response_error',
            'Workflow completed but no final response was generated',
            {'query': state['user_query']}
        )
        
        error_state['final_response'] = (
            f"I apologize, but I wasn't able to generate a proper response for your query: "
            f"'{state['user_query']}'. Please try rephrasing your question or try again later."
        )
        
        error_state = StateManager.update_status(error_state, WorkflowStatus.ERROR)
        
        return error_state
    
    def _handle_workflow_error(self, initial_state: AgentState, error: Exception) -> AgentState:
        """
        Handle unexpected workflow errors.
        
        Args:
            initial_state: Initial state when error occurred
            error: The exception that was raised
            
        Returns:
            Error state with appropriate response
        """
        
        error_state = StateManager.add_error(
            initial_state,
            'workflow_error',
            f"Unexpected workflow error: {str(error)}",
            {
                'query': initial_state['user_query'],
                'conversation_id': initial_state['conversation_id'],
                'error_type': type(error).__name__
            }
        )
        
        error_state['final_response'] = (
            f"I encountered an unexpected error while processing your query: '{initial_state['user_query']}'. "
            f"Please try again, and if the problem persists, try rephrasing your question."
        )
        
        error_state = StateManager.update_status(error_state, WorkflowStatus.ERROR)
        
        return error_state
    
    def get_workflow_info(self) -> dict:
        """
        Get information about the workflow configuration.
        
        Returns:
            Workflow configuration information
        """
        
        return {
            'max_attempts': self.max_attempts,
            'workflow_type': 'cyclical_with_retry',
            'retry_triggers': ['empty_results', 'no_useful_data', 'insufficient_useful_data'],
            'quality_thresholds': {
                'min_success_rate': 0.1,
                'min_useful_items': 2
            },
            'workflow_diagram': WorkflowGraphBuilder.get_workflow_diagram()
        }


# Create the main workflow instance
connect_workflow = ConnectWorkflow()