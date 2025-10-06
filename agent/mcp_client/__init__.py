"""
MCP Client Package for LangGraph Agent

This package contains all MCP (Model Context Protocol) client functionality
for connecting to and interacting with the Connect MCP server.

Main Components:
- types: Data structures and type definitions
- base_client: Core HTTP communication layer
- tool_client: High-level tool interfaces
- mcp_client: Main client facade

Usage:
    from agent.mcp_client import MCPClient
    
    client = MCPClient("http://localhost:8000", "your-api-key")
    result = await client.tools.search_profiles("AI engineer")
"""

from .mcp_client import MCPClient
from .types import MCPResponse, MCPClientConfig, ToolCall, MCPClientError

__all__ = [
    'MCPClient',
    'MCPResponse', 
    'MCPClientConfig',
    'ToolCall',
    'MCPClientError'
]