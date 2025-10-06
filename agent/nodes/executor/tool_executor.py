"""
Tool Executor Module

Executes individual MCP tools and manages the execution lifecycle.
This module focuses solely on tool execution and result processing.
"""

import time
from datetime import datetime
from typing import Dict, Any
from agent.mcp_client import MCPClient
from agent.state import PlanStepStatus


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
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]):
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