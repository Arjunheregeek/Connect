"""
SIMPLIFIED Synthesizer Node for LangGraph

Removes all complex features that cause issues:
- No complex data analysis
- No quality assessment
- Just basic response generation
"""

from agent.state import AgentState


async def simple_synthesizer_node(state: AgentState) -> AgentState:
    """
    SIMPLIFIED Synthesizer node for LangGraph workflow.
    
    This version removes all problematic complexity:
    - No complex data analysis
    - No quality assessment 
    - Just basic response generation
    
    Args:
        state: Current AgentState with tool results
        
    Returns:
        Updated AgentState with final response
    """
    
    # Update status
    state['workflow_status'] = 'synthesizing'
    
    try:
        # Simple response generation
        user_query = state.get('user_query', '')
        tool_results = state.get('tool_results', [])
        accumulated_data = state.get('accumulated_data', [])
        
        # Create a simple response from real MCP data
        if tool_results or accumulated_data:
            # Check if we have successful results
            successful_results = [r for r in tool_results if r.get('success', False)]
            
            if successful_results:
                response = f"Here are the results for your query: '{user_query}'\n\n"
                
                # Add the actual MCP response data
                for i, result in enumerate(successful_results, 1):
                    result_data = result.get('result', 'No result')
                    # Truncate very long responses for readability
                    if len(result_data) > 500:
                        result_data = result_data[:500] + "..."
                    response += f"{result_data}\n"
            else:
                response = f"I searched for '{user_query}' but didn't find any useful results."
        else:
            response = f"I searched for information about '{user_query}' but didn't find specific results."
        
        state['final_response'] = response
        state['workflow_status'] = 'completed'
        
    except Exception as e:
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Synthesis error: {str(e)}")
        state['final_response'] = f"I encountered an error while processing your query: '{user_query}'"
        state['workflow_status'] = 'error'
    
    return state