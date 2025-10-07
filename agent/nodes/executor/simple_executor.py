"""
SIMPLIFIED Tool Executor Node for LangGraph

Removes all complex features that cause issues:
- No async context managers
- No complex error handling
- No plan validation
- Just basic tool execution
"""

from agent.state import AgentState
from agent.mcp_client import MCPClient


async def simple_executor_node(state: AgentState) -> AgentState:
    """
    SIMPLIFIED Tool Executor node for LangGraph workflow.
    
    This version removes all problematic complexity:
    - No async context managers
    - No plan validation
    - No complex retry logic
    - Just basic tool execution
    
    Args:
        state: Current AgentState with execution plan
        
    Returns:
        Updated AgentState with tool execution results
    """
    
    # Update status
    state['workflow_status'] = 'executing_tools'
    
    # Create simple MCP client (no context manager)
    mcp_client = MCPClient()
    
    # Simple execution - make real MCP call
    try:
        user_query = state.get('user_query', '')
        
        # Make actual natural language search call to MCP server
        response = await mcp_client.tools.natural_language_search(user_query)
        
        # Process the response
        if response.success and response.data:
            # Extract text from MCP response format
            if 'content' in response.data and response.data['content']:
                result_text = response.data['content'][0].get('text', 'No text in response')
                success = True
            else:
                result_text = f"Empty response for: {user_query}"
                success = False
        else:
            result_text = f"No results found for: {user_query}"
            success = False
        
        # Add result to state
        if 'tool_results' not in state:
            state['tool_results'] = []
        
        state['tool_results'].append({
            'tool_name': 'natural_language_search',
            'result': result_text,
            'success': success
        })
        
        if 'accumulated_data' not in state:
            state['accumulated_data'] = []
        
        if success:
            state['accumulated_data'].append(result_text)
        
        state['workflow_status'] = 'tools_complete'
        
    except Exception as e:
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Execution error: {str(e)}")
        state['workflow_status'] = 'error'
    
    finally:
        # Clean up MCP client
        try:
            await mcp_client.close()
        except:
            pass  # Best effort cleanup
    
    return state