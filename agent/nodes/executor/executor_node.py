"""
Executor Node Orchestrator

Main orchestrator that coordinates plan validation, tool execution, and result aggregation.
This module brings together all the executor components.
"""

from typing import Dict, Any
from agent.state import AgentState, WorkflowStatus, StateManager
from agent.mcp_client import MCPClient
from .plan_validator import PlanValidator
from .tool_executor import ToolExecutor
from .result_aggregator import ResultAggregator


async def tool_executor_node(state: AgentState) -> AgentState:
    """
    Main Tool Executor node function for LangGraph workflow.
    
    This is the entry point for the Tool Executor node that processes the execution plan,
    runs the specified MCP tools, and collects results.
    
    Args:
        state: Current AgentState with execution plan
        
    Returns:
        Updated AgentState with tool execution results
    """
    
    # Update status to indicate tool execution has started
    updated_state = StateManager.update_status(state, WorkflowStatus.EXECUTING_TOOLS)
    
    try:
        # Step 1: Validate the execution plan
        validation_result = PlanValidator.validate_plan(state)
        
        if not validation_result['valid']:
            # Handle validation failure
            error_state = StateManager.add_error(
                updated_state,
                'plan_validation_error',
                f"Execution plan validation failed: {', '.join(validation_result['issues'])}",
                {'validation_result': validation_result}
            )
            return StateManager.update_status(error_state, WorkflowStatus.ERROR)
        
        # Step 2: Initialize MCP client and tool executor
        async with MCPClient() as mcp_client:
            executor = ToolExecutor(mcp_client)
            
            # Step 3: Execute plan steps
            execution_plan = state['execution_plan']
            execution_results = []
            
            # Execute steps (respecting dependencies - for now, sequential execution)
            for step in execution_plan.steps:
                # Check if dependencies are met (simplified for now)
                if step.depends_on:
                    # In a full implementation, we'd check if dependent steps are completed
                    pass
                
                # Execute the step
                result = await executor.execute_step(step)
                execution_results.append(result)
                
                # Add tool result to state
                if result['success']:
                    updated_state = StateManager.add_tool_result(
                        updated_state,
                        step.id,
                        step.tool_name,
                        result['data'],
                        result['execution_time']
                    )
                
                # Stop execution if a critical step fails
                if not result['success'] and step.critical:
                    # Try fallback if available
                    if execution_plan.fallback_strategy and 'natural_language_search' not in step.tool_name:
                        # Execute fallback natural language search
                        fallback_result = await executor._call_mcp_tool(
                            'natural_language_search',
                            {'question': state['user_query']}
                        )
                        
                        if fallback_result.success:
                            execution_results.append({
                                'success': True,
                                'step_id': f'fallback-{step.id}',
                                'tool_name': 'natural_language_search',
                                'data': fallback_result.data,
                                'execution_time': 1.0
                            })
                            
                            updated_state = StateManager.add_tool_result(
                                updated_state,
                                f'fallback-{step.id}',
                                'natural_language_search',
                                fallback_result.data,
                                1.0
                            )
                    else:
                        # Critical step failed and no fallback available
                        break
            
            # Step 4: Aggregate results
            aggregated_results = ResultAggregator.aggregate_results(execution_results)
            
            # Step 5: Update state with aggregated results
            updated_state['accumulated_data'] = aggregated_results['combined_data']
            updated_state['intermediate_insights'] = aggregated_results['insights']
            
            # Add execution metrics
            if 'execution_metrics' not in updated_state:
                updated_state['execution_metrics'] = {}
            
            updated_state['execution_metrics'].update(aggregated_results['execution_summary'])
            updated_state['execution_metrics']['executor_stats'] = executor.get_execution_stats()
            
            # Update status based on results
            if aggregated_results['execution_summary']['success_rate'] > 0:
                updated_state = StateManager.update_status(updated_state, WorkflowStatus.TOOLS_COMPLETE)
            else:
                # All tools failed
                error_state = StateManager.add_error(
                    updated_state,
                    'tool_execution_error',
                    'All tool executions failed',
                    {'errors': aggregated_results['errors']}
                )
                updated_state = StateManager.update_status(error_state, WorkflowStatus.ERROR)
            
            return updated_state
            
    except Exception as e:
        # Handle unexpected execution errors
        error_state = StateManager.add_error(
            updated_state,
            'execution_error',
            f"Unexpected error during tool execution: {str(e)}",
            {'query': state['user_query']}
        )
        
        return StateManager.update_status(error_state, WorkflowStatus.ERROR)