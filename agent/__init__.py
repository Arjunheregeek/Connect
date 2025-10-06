"""
LangGraph Agent Package

This package contains the Single Stateful LangGraph Agent implementation
that connects to the Connect MCP server via HTTP.

Main Components:
- MCPClient: High-level client for MCP communication
- AgentState: State management for the agent workflow
- Workflow nodes: Planner, Tool Executor, Synthesizer
- LangGraph workflow: Complete agent implementation
"""

from .mcp_client import MCPClient, MCPResponse, MCPClientError
from .mcp_client import MCPClientConfig, ToolCall
from .state import AgentState, WorkflowStatus, StateManager, PlanStep, ExecutionPlan
from .nodes import planner_node, tool_executor_node, synthesizer_node

__all__ = [
    # MCP Client
    'MCPClient',
    'MCPResponse', 
    'MCPClientError',
    'MCPClientConfig',
    'ToolCall',
    
    # State Management
    'AgentState',
    'WorkflowStatus',
    'StateManager', 
    'PlanStep',
    'ExecutionPlan',
    
    # Workflow Nodes
    'planner_node',
    'tool_executor_node',
    'synthesizer_node'
]