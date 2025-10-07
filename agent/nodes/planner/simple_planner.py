"""
SIMPLIFIED Planner Node for LangGraph

Removes all complex features that cause issues:
- No complex query analysis
- No tool mapping
- No execution plan generation
- Just basic planning
"""

from agent.state import AgentState


async def simple_planner_node(state: AgentState) -> AgentState:
    """
    SIMPLIFIED Planner node for LangGraph workflow.
    
    This version removes all problematic complexity:
    - No complex query analysis
    - No tool mapping
    - No execution plan generation
    - Just basic planning
    
    Args:
        state: Current AgentState with user query
        
    Returns:
        Updated AgentState with simple execution plan
    """
    
    # Update status
    state['workflow_status'] = 'planning'
    
    try:
        user_query = state.get('user_query', '')
        
        # Simple planning - just note that we'll do a search
        simple_plan = {
            'strategy': 'simple_search',
            'tools_to_use': ['natural_language_search'],
            'query': user_query
        }
        
        state['execution_plan'] = simple_plan
        state['workflow_status'] = 'planning_complete'
        
    except Exception as e:
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Planning error: {str(e)}")
        state['workflow_status'] = 'error'
    
    return state