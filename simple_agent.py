#!/usr/bin/env python3
"""
Simple Working Agent

A simplified version of the Connect Agent that works reliably without 
complex LangGraph cycles that can cause recursion issues.
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from agent.mcp_client import MCPClient
from agent.nodes.planner import planner_node
from agent.nodes.executor import tool_executor_node
from agent.nodes.synthesizer import synthesizer_node
from agent.state import AgentState, WorkflowStatus, StateManager
from agent.workflow.quality_assessor import WorkflowQualityAssessor


class SimpleConnectAgent:
    """
    Simplified Connect Agent with manual retry logic instead of complex LangGraph cycles.
    
    This version is more reliable and easier to debug while maintaining all the
    intelligent features like quality assessment and retry logic.
    """
    
    def __init__(self):
        """Initialize the simple agent."""
        self.session_history = []
    
    async def ask(self, user_query: str, conversation_id: Optional[str] = None) -> str:
        """Ask a question and get a simple response."""
        result = await self.ask_with_details(user_query, conversation_id)
        return result['response']
    
    async def ask_with_details(
        self, 
        user_query: str, 
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask a question and get detailed response with metadata.
        
        Args:
            user_query: The user's question
            conversation_id: Optional conversation ID for context
            
        Returns:
            Detailed response dictionary with metadata
        """
        
        start_time = time.time()
        conversation_id = conversation_id or str(uuid.uuid4())
        
        # Initialize state
        state = self._create_initial_state(user_query, conversation_id)
        
        try:
            # Execute workflow with manual retry logic
            final_state = await self._execute_workflow_with_retries(state)
            execution_time = time.time() - start_time
            
            # Build response
            response = await self._build_response(final_state, execution_time)
            
            # Record in session history
            self._record_session(response)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_response = self._create_error_response(
                user_query, conversation_id, str(e), execution_time
            )
            self._record_session(error_response)
            return error_response
    
    def _create_initial_state(self, user_query: str, conversation_id: str) -> AgentState:
        """Create initial agent state."""
        return {
            'user_query': user_query,
            'conversation_id': conversation_id,
            'workflow_status': WorkflowStatus.INITIALIZED,
            'messages': [],
            'accumulated_data': [],
            'tool_results': [],
            'errors': [],
            'session_id': str(uuid.uuid4()),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'tools_used': [],
            'retry_count': 0,
            'planning_rounds': 0,
            'synthesis_attempts': 0,
            'workflow_version': '1.0.0'
        }
    
    async def _execute_workflow_with_retries(self, state: AgentState) -> AgentState:
        """Execute the workflow with manual retry logic."""
        
        max_attempts = 3
        attempt = 1
        
        while attempt <= max_attempts:
            print(f"🔄 Attempt {attempt}/{max_attempts}")
            
            try:
                # Step 1: Planning
                state = StateManager.update_status(state, WorkflowStatus.PLANNING)
                state = await planner_node(state)
                
                # Step 2: Tool Execution  
                state = StateManager.update_status(state, WorkflowStatus.EXECUTING_TOOLS)
                state = await tool_executor_node(state)
                
                # Step 3: Quality Assessment
                quality_assessment = WorkflowQualityAssessor.assess_result_quality(state)
                state['quality_assessment'] = quality_assessment
                
                # Step 4: Check if results are good enough
                if quality_assessment.get('is_useful', False):
                    print("✅ Quality assessment: Results are useful, proceeding to synthesis")
                    
                    # Step 5: Synthesis
                    state = StateManager.update_status(state, WorkflowStatus.SYNTHESIZING)
                    state = await synthesizer_node(state)
                    state = StateManager.update_status(state, WorkflowStatus.COMPLETED)
                    
                    return state
                
                else:
                    print(f"⚠️  Quality assessment: Results not useful - {quality_assessment.get('reason', 'unknown')}")
                    
                    # Check if we should retry
                    if attempt < max_attempts:
                        print(f"🔄 Retrying with different approach (attempt {attempt + 1})")
                        attempt += 1
                        state['retry_count'] = attempt - 1
                        
                        # Add some variation for retry (could be more sophisticated)
                        state['planning_rounds'] = attempt - 1
                        continue
                    else:
                        print("❌ Max attempts reached, creating fallback response")
                        break
                        
            except Exception as e:
                print(f"❌ Error in attempt {attempt}: {e}")
                if attempt < max_attempts:
                    attempt += 1
                    continue
                else:
                    raise e
        
        # Create fallback response
        state = await self._create_fallback_response(state)
        return state
    
    async def _create_fallback_response(self, state: AgentState) -> AgentState:
        """Create a fallback response when all attempts fail."""
        
        fallback_response = (
            f"I searched for information about '{state['user_query']}' but couldn't find "
            f"useful results after {state.get('retry_count', 0) + 1} attempts. "
            f"This might be because:\n"
            f"• The query is too specific or contains terms not in the database\n"
            f"• The search criteria need to be adjusted\n"
            f"• The information might not be available in the current dataset\n\n"
            f"Try rephrasing your question or using broader search terms."
        )
        
        state['final_response'] = fallback_response
        state = StateManager.update_status(state, WorkflowStatus.COMPLETED)
        
        return state
    
    async def _build_response(self, state: AgentState, execution_time: float) -> Dict[str, Any]:
        """Build the detailed response dictionary."""
        
        success = state.get('workflow_status') == WorkflowStatus.COMPLETED
        response_text = state.get('final_response', 'No response generated')
        
        # Count data found
        data_found = len(state.get('accumulated_data', []))
        for result in state.get('tool_results', []):
            if isinstance(result.get('result'), (list, tuple)):
                data_found += len(result['result'])
        
        return {
            'response': response_text,
            'success': success,
            'metadata': {
                'conversation_id': state['conversation_id'],
                'workflow_status': state['workflow_status'].value if hasattr(state['workflow_status'], 'value') else str(state['workflow_status']),
                'execution_time': execution_time,
                'tools_used': state.get('tools_used', []),
                'retry_count': state.get('retry_count', 0),
                'data_found': data_found,
                'quality_assessment': state.get('quality_assessment', {}),
                'response_metadata': state.get('response_metadata', {})
            },
            'debug_info': state.get('debug_info', {}),
            'errors': state.get('errors', [])
        }
    
    def _create_error_response(
        self, 
        user_query: str, 
        conversation_id: str, 
        error_message: str, 
        execution_time: float
    ) -> Dict[str, Any]:
        """Create an error response."""
        
        return {
            'response': f"I encountered an error while processing your query: '{user_query}'. Error: {error_message}",
            'success': False,
            'metadata': {
                'conversation_id': conversation_id,
                'workflow_status': 'error',
                'execution_time': execution_time,
                'tools_used': [],
                'retry_count': 0,
                'data_found': 0,
                'response_metadata': {}
            },
            'debug_info': {},
            'errors': [
                {
                    'type': 'agent_error',
                    'message': error_message,
                    'timestamp': datetime.now()
                }
            ]
        }
    
    def _record_session(self, response: Dict[str, Any]):
        """Record the response in session history."""
        
        session_entry = {
            'timestamp': datetime.now(),
            'query': response['metadata'].get('conversation_id', 'unknown'),
            'success': response['success'],
            'execution_time': response['metadata'].get('execution_time', 0),
            'tools_used': response['metadata'].get('tools_used', []),
            'retry_count': response['metadata'].get('retry_count', 0)
        }
        
        self.session_history.append(session_entry)
    
    def get_session_history(self):
        """Get session history."""
        return self.session_history.copy()
    
    def clear_history(self):
        """Clear session history."""
        self.session_history.clear()


# Create global instance
simple_agent = SimpleConnectAgent()


# Simple sync wrappers
def ask_simple(question: str, conversation_id: Optional[str] = None) -> str:
    """Simple synchronous wrapper."""
    return asyncio.run(simple_agent.ask(question, conversation_id))


def ask_simple_detailed(question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Simple detailed synchronous wrapper."""
    return asyncio.run(simple_agent.ask_with_details(question, conversation_id))


if __name__ == "__main__":
    # Test the simple agent
    print("🤖 Testing Simple Connect Agent")
    
    response = ask_simple("Find Python developers")
    print(f"Response: {response[:100]}...")
    
    detailed = ask_simple_detailed("Find React developers") 
    print(f"Success: {detailed['success']}")
    print(f"Execution time: {detailed['metadata']['execution_time']:.2f}s")
    print(f"Tools used: {detailed['metadata']['tools_used']}")