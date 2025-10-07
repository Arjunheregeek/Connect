"""
Connect Agent - Main Interface

Simple, clean interface for the Connect Agent that wraps the powerful
cyclical workflow system with user-friendly methods.
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

from agent.workflow import connect_workflow
from agent.state import AgentState, WorkflowStatus


class ConnectAgent:
    """
    Main interface for the Connect Agent.
    
    Provides a clean, user-friendly API for querying the people knowledge graph
    using the intelligent cyclical workflow with retry logic.
    """
    
    def __init__(self):
        """Initialize the Connect Agent."""
        self.workflow = connect_workflow
        self._session_history: List[Dict[str, Any]] = []
    
    async def ask(self, question: str, conversation_id: Optional[str] = None) -> str:
        """
        Ask the agent a question and get a response.
        
        Args:
            question: Your question about people, skills, companies, etc.
            conversation_id: Optional conversation ID for context tracking
            
        Returns:
            The agent's response as a string
            
        Example:
            >>> agent = ConnectAgent()
            >>> response = await agent.ask("Find Python developers at Google")
            >>> print(response)
        """
        
        if not question or not question.strip():
            return "Please provide a question for me to answer."
        
        try:
            # Run the workflow
            result_state = await self.workflow.run(question, conversation_id)
            
            # Extract the response
            response = result_state.get('final_response', 'I apologize, but I could not generate a response.')
            
            # Store in session history
            self._add_to_history(question, response, result_state)
            
            return response
            
        except Exception as e:
            error_response = f"I encountered an error while processing your question: {str(e)}"
            self._add_to_history(question, error_response, {'error': str(e)})
            return error_response
    
    async def ask_with_details(self, question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question and get detailed response with metadata.
        
        Args:
            question: Your question
            conversation_id: Optional conversation ID
            
        Returns:
            Dictionary with response, metadata, debug info, and execution details
        """
        
        if not question or not question.strip():
            return {
                'response': "Please provide a question for me to answer.",
                'success': False,
                'metadata': {},
                'debug_info': {}
            }
        
        try:
            # Run the workflow
            result_state = await self.workflow.run(question, conversation_id)
            
            # Extract detailed information
            response = result_state.get('final_response', 'I could not generate a response.')
            success = result_state.get('workflow_status') == WorkflowStatus.COMPLETED
            
            # Format the detailed response
            detailed_result = {
                'response': response,
                'success': success,
                'metadata': {
                    'conversation_id': result_state.get('conversation_id'),
                    'workflow_status': result_state.get('workflow_status', '').value if hasattr(result_state.get('workflow_status', ''), 'value') else str(result_state.get('workflow_status', '')),
                    'execution_time': self._calculate_execution_time(result_state),
                    'tools_used': self._extract_tools_used(result_state),
                    'retry_info': result_state.get('retry_info', {}),
                    'data_found': len(result_state.get('accumulated_data', [])) + len(result_state.get('tool_results', [])),
                    'response_metadata': result_state.get('response_metadata', {})
                },
                'debug_info': result_state.get('debug_info', {}),
                'errors': result_state.get('errors', [])
            }
            
            # Store in session history
            self._add_to_history(question, response, result_state)
            
            return detailed_result
            
        except Exception as e:
            error_result = {
                'response': f"I encountered an error: {str(e)}",
                'success': False,
                'metadata': {'error': str(e)},
                'debug_info': {},
                'errors': [{'type': 'agent_error', 'message': str(e)}]
            }
            
            self._add_to_history(question, error_result['response'], {'error': str(e)})
            return error_result
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow configuration."""
        return self.workflow.get_workflow_info()
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get the current session's question/answer history."""
        return self._session_history.copy()
    
    def clear_history(self) -> None:
        """Clear the session history."""
        self._session_history.clear()
    
    def _add_to_history(self, question: str, response: str, state: AgentState) -> None:
        """Add a question/response pair to session history."""
        
        history_entry = {
            'timestamp': datetime.now(),
            'question': question,
            'response': response,
            'conversation_id': state.get('conversation_id'),
            'success': state.get('workflow_status') == WorkflowStatus.COMPLETED,
            'retry_count': state.get('retry_info', {}).get('attempt_count', 1),
            'tools_used': self._extract_tools_used(state),
            'execution_time': self._calculate_execution_time(state)
        }
        
        self._session_history.append(history_entry)
        
        # Keep only last 50 entries to prevent memory issues
        if len(self._session_history) > 50:
            self._session_history = self._session_history[-50:]
    
    def _extract_tools_used(self, state: AgentState) -> List[str]:
        """Extract list of tools that were used in the workflow."""
        
        tools_used = []
        
        # From execution plan
        if 'execution_plan' in state:
            plan = state['execution_plan']
            tools_used.extend([step.tool_name for step in plan.steps])
        
        # From tool results
        tool_results = state.get('tool_results', [])
        for result in tool_results:
            if result.get('tool_name') and result['tool_name'] not in tools_used:
                tools_used.append(result['tool_name'])
        
        return tools_used
    
    def _calculate_execution_time(self, state: AgentState) -> float:
        """Calculate total execution time from state timestamps."""
        
        created_at = state.get('created_at')
        updated_at = state.get('updated_at')
        
        if created_at and updated_at:
            return (updated_at - created_at).total_seconds()
        
        # Fallback to execution metrics if available
        execution_metrics = state.get('execution_metrics', {})
        return execution_metrics.get('total_execution_time', 0.0)


# Create the main agent instance
agent = ConnectAgent()