"""
Tool Executor Node Implementation

The Tool Executor node is responsible for executing the MCP tools according to
the execution plan created by the Planner node.

Key Functions:
1. Plan Validation - Ensuring the execution plan is valid and executable
2. Tool Execution - Running MCP tools in the correct order with dependencies
3. Result Collection - Gathering and storing tool execution results
4. Error Handling - Managing failures and implementing fallback strategies

Workflow:
AgentState → Plan Validation → Tool Execution Loop → Result Aggregation → Updated State
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from agent.state import AgentState, WorkflowStatus, StateManager, PlanStepStatus
from agent.mcp_client import MCPClient, MCPResponse, MCPClientError


class PlanValidator:
    """
    Validates execution plans before execution to ensure they are feasible.
    
    Checks for proper step configuration, argument validation, and dependency resolution.
    """
    
    @classmethod
    def validate_plan(cls, state: AgentState) -> Dict[str, Any]:
        """
        Validate the execution plan in the current state.
        
        Args:
            state: Current agent state with execution plan
            
        Returns:
            Validation result with status and any issues found
        """
        
        if 'execution_plan' not in state:
            return {
                'valid': False,
                'error': 'No execution plan found in state',
                'issues': ['Missing execution plan']
            }
        
        plan = state['execution_plan']
        issues = []
        
        # Check if plan has steps
        if not plan.steps:
            issues.append('Execution plan has no steps')
        
        # Validate each step
        for step in plan.steps:
            step_issues = cls._validate_step(step)
            issues.extend(step_issues)
        
        # Check for circular dependencies
        if cls._has_circular_dependencies(plan.steps):
            issues.append('Circular dependencies detected in plan steps')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_steps': len(plan.steps),
            'critical_steps': len([s for s in plan.steps if s.critical])
        }
    
    @classmethod
    def _validate_step(cls, step) -> List[str]:
        """Validate a single plan step."""
        issues = []
        
        # Check required fields
        if not step.id:
            issues.append(f'Step missing ID')
        if not step.tool_name:
            issues.append(f'Step {step.id} missing tool name')
        if not isinstance(step.arguments, dict):
            issues.append(f'Step {step.id} has invalid arguments format')
        
        # Check tool name validity (basic check for known patterns)
        valid_tool_patterns = [
            'find_person', 'find_people', 'get_company', 'natural_language',
            'get_skill', 'find_colleagues', 'find_domain'
        ]
        
        if not any(pattern in step.tool_name for pattern in valid_tool_patterns):
            issues.append(f'Step {step.id} has potentially invalid tool name: {step.tool_name}')
        
        return issues
    
    @classmethod
    def _has_circular_dependencies(cls, steps) -> bool:
        """Check for circular dependencies in plan steps."""
        # Create dependency graph
        deps = {step.id: step.depends_on for step in steps}
        
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in deps.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in deps:
            if has_cycle(step_id):
                return True
        
        return False


class ToolExecutor:
    """
    Executes individual MCP tools and manages the execution lifecycle.
    
    Handles tool invocation, result processing, error recovery, and timing.
    """
    
    def __init__(self, mcp_client: MCPClient):
        """
        Initialize the tool executor with an MCP client.
        
        Args:
            mcp_client: Connected MCP client instance
        """
        self.mcp_client = mcp_client
        self.execution_stats = {
            'tools_executed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_time': 0.0
        }
    
    async def execute_step(self, step) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: PlanStep to execute
            
        Returns:
            Execution result with status, data, timing, and any errors
        """
        start_time = time.time()
        
        try:
            # Update step status to executing
            step.status = PlanStepStatus.EXECUTING
            step.timestamp = datetime.now()
            
            # Execute the tool
            response = await self._call_mcp_tool(step.tool_name, step.arguments)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Process the response
            if response.success:
                step.status = PlanStepStatus.COMPLETED
                step.result = response.data
                step.execution_time = execution_time
                
                self.execution_stats['successful_executions'] += 1
                
                return {
                    'success': True,
                    'step_id': step.id,
                    'tool_name': step.tool_name,
                    'data': response.data,
                    'execution_time': execution_time,
                    'metadata': response.metadata
                }
            else:
                step.status = PlanStepStatus.FAILED
                step.error = response.error
                step.execution_time = execution_time
                
                self.execution_stats['failed_executions'] += 1
                
                return {
                    'success': False,
                    'step_id': step.id,
                    'tool_name': step.tool_name,
                    'error': response.error,
                    'execution_time': execution_time
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            step.status = PlanStepStatus.FAILED
            step.error = str(e)
            step.execution_time = execution_time
            
            self.execution_stats['failed_executions'] += 1
            
            return {
                'success': False,
                'step_id': step.id,
                'tool_name': step.tool_name,
                'error': str(e),
                'execution_time': execution_time
            }
        finally:
            self.execution_stats['tools_executed'] += 1
            self.execution_stats['total_time'] += execution_time
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """
        Call a specific MCP tool with the given arguments.
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPResponse from the tool execution
        """
        
        # Map tool names to client methods
        if hasattr(self.mcp_client.tools, tool_name):
            tool_method = getattr(self.mcp_client.tools, tool_name)
            
            # Call the tool method with arguments
            if arguments:
                # Handle different argument patterns
                if tool_name == 'find_person_by_name':
                    return await tool_method(arguments.get('name', ''))
                elif tool_name == 'find_people_by_skill':
                    return await tool_method(arguments.get('skill', ''))
                elif tool_name == 'find_people_by_company':
                    return await tool_method(arguments.get('company_name', ''))
                elif tool_name == 'find_colleagues_at_company':
                    return await tool_method(
                        arguments.get('person_name', ''),
                        arguments.get('company_name', '')
                    )
                elif tool_name == 'natural_language_search':
                    return await tool_method(arguments.get('question', ''))
                elif tool_name == 'find_people_with_multiple_skills':
                    return await tool_method(arguments.get('skills', []))
                elif tool_name == 'get_skill_popularity':
                    return await tool_method(arguments.get('limit', 10))
                else:
                    # Generic call for other tools
                    return await self.mcp_client.call_tool(tool_name, arguments)
            else:
                # Call without arguments
                return await tool_method()
        else:
            # Fallback to generic tool call
            return await self.mcp_client.call_tool(tool_name, arguments)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get current execution statistics."""
        return self.execution_stats.copy()


class ResultAggregator:
    """
    Aggregates and processes results from multiple tool executions.
    
    Combines data from different tools, identifies patterns, and prepares
    comprehensive results for the Synthesizer node.
    """
    
    @classmethod
    def aggregate_results(cls, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple tool executions.
        
        Args:
            execution_results: List of execution results from ToolExecutor
            
        Returns:
            Aggregated results with combined data and insights
        """
        
        successful_results = [r for r in execution_results if r['success']]
        failed_results = [r for r in execution_results if not r['success']]
        
        # Combine all successful data
        combined_data = []
        data_sources = []
        
        for result in successful_results:
            if result.get('data'):
                combined_data.append(result['data'])
                data_sources.append(result['tool_name'])
        
        # Extract insights
        insights = cls._extract_insights(successful_results)
        
        # Calculate execution metrics
        total_time = sum(r.get('execution_time', 0) for r in execution_results)
        success_rate = len(successful_results) / len(execution_results) if execution_results else 0
        
        return {
            'combined_data': combined_data,
            'data_sources': data_sources,
            'insights': insights,
            'execution_summary': {
                'total_tools': len(execution_results),
                'successful_tools': len(successful_results),
                'failed_tools': len(failed_results),
                'success_rate': success_rate,
                'total_execution_time': total_time
            },
            'errors': [r.get('error') for r in failed_results if r.get('error')]
        }
    
    @classmethod
    def _extract_insights(cls, results: List[Dict[str, Any]]) -> List[str]:
        """Extract insights from successful tool executions."""
        insights = []
        
        # Count different types of results
        tool_types = {}
        for result in results:
            tool_name = result['tool_name']
            tool_types[tool_name] = tool_types.get(tool_name, 0) + 1
        
        # Generate insights based on tool usage
        if 'find_people_by_skill' in tool_types:
            insights.append("Skill-based search was performed to find relevant professionals")
        
        if 'find_person_by_name' in tool_types:
            insights.append("Direct person search was conducted for specific individuals")
        
        if 'natural_language_search' in tool_types:
            insights.append("Natural language processing was used for comprehensive analysis")
        
        if len(results) > 1:
            insights.append(f"Multiple search strategies were employed using {len(results)} different tools")
        
        return insights


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