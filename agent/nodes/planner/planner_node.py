"""
Planner Node Orchestrator

Main orchestrator that coordinates query analysis, tool selection, and plan generation.
This module brings together all the planner components.
"""

from typing import Dict, Any
from agent.state import AgentState, WorkflowStatus, StateManager
from .query_analyzer import QueryAnalyzer
from .tool_mapper import ToolMapper
from .plan_generator import PlanGenerator


async def planner_node(state: AgentState) -> AgentState:
    """
    Main Planner node function for LangGraph workflow.
    
    This is the entry point for the Planner node that processes the current state,
    analyzes the user query, selects appropriate tools, and creates an execution plan.
    
    Args:
        state: Current AgentState from the workflow
        
    Returns:
        Updated AgentState with execution plan and status
    """
    
    # Update status to indicate planning has started
    updated_state = StateManager.update_status(state, WorkflowStatus.PLANNING)
    
    try:
        # Step 1: Analyze the user query
        query_analysis = QueryAnalyzer.analyze_query(state['user_query'])
        
        # Step 2: Select appropriate MCP tools
        selected_tools = ToolMapper.select_tools(query_analysis)
        
        # Step 3: Generate execution plan
        execution_plan = PlanGenerator.create_execution_plan(query_analysis, selected_tools)
        
        # Step 4: Add plan to state
        updated_state['execution_plan'] = execution_plan
        updated_state = StateManager.update_status(updated_state, WorkflowStatus.PLAN_READY)
        
        # Add debug information
        if 'debug_info' not in updated_state:
            updated_state['debug_info'] = {}
        
        updated_state['debug_info']['planner'] = {
            'query_analysis': query_analysis,
            'selected_tools': selected_tools,
            'plan_confidence': execution_plan.confidence,
            'estimated_time': execution_plan.estimated_time
        }
        
        return updated_state
        
    except Exception as e:
        # Handle planning errors
        error_state = StateManager.add_error(
            updated_state,
            'planning_error',
            f"Failed to create execution plan: {str(e)}",
            {'query': state['user_query']}
        )
        
        return StateManager.update_status(error_state, WorkflowStatus.ERROR)