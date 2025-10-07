"""
MCP HTTP Client for LangGraph Agent

This module provides a clean, high-level interface to the Connect MCP server.
It combines modular components to offer both low-level control and high-level convenience.

Components:
- MCPClient: Main facade class with all tool methods
- MCPBaseClient: Core HTTP communication
- MCPToolClient: High-level tool interfaces
- Types: Data structures and configurations

Key Features:
- Modular, testable architecture
- JSON-RPC 2.0 protocol compliance
- X-API-Key authentication
- Comprehensive error handling
- Connection pooling and retry logic
- Type-safe interfaces for all 24 tools
"""

from typing import Dict, Any, Optional

# Import all required components
from agent.mcp_client.base_client import MCPBaseClient
from agent.mcp_client.tool_client import MCPToolClient
from agent.mcp_client.types import MCPClientConfig, MCPResponse, ToolCall, MCPClientError


class MCPClient:
    """
    Main MCP client facade that provides access to all Connect MCP server functionality.
    
    This class combines the base client and tool client to provide a clean,
    high-level interface while maintaining modularity and testability.
    
    Usage:
        async with MCPClient() as client:
            # Core MCP operations
            await client.health_check()
            await client.list_tools()
            
            # Direct tool calls (generic)
            response = await client.call_tool("find_people_by_skill", {"skill": "python"})
            
            # Typed tool access (recommended)
            response = await client.tools.find_people_by_skill("python")
            response = await client.tools.natural_language_search("Who are Python experts?")
            
            if response.success:
                print(f"Success: {response.data}")
    """
    
    def __init__(
        self,
        base_url: str = "https://connect-vxll.onrender.com",
        api_key: str = "f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            api_key: X-API-Key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        # Create configuration
        self.config = MCPClientConfig(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        # Initialize modular components
        self.base_client = MCPBaseClient(self.config)
        self.tool_client = MCPToolClient(self.base_client)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.base_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.base_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def close(self):
        """Close the client and cleanup resources"""
        await self.base_client.close()
    
    # =================================================================
    # CORE MCP METHODS
    # =================================================================
    
    async def health_check(self) -> MCPResponse:
        """Check server health status"""
        return await self.tool_client.health_check()
    
    async def list_tools(self) -> MCPResponse:
        """List all available MCP tools"""
        return await self.tool_client.list_tools()
    
    async def call_tool(self, tool_name: str, arguments: dict) -> MCPResponse:
        """Call a specific MCP tool by name"""
        tool_call = ToolCall(tool_name, arguments)
        return await self.tool_client.call_tool(tool_call)
    
    # =================================================================
    # DYNAMIC TOOL ACCESS
    # All 24 MCP tools are accessible via the tool_client property
    # This eliminates redundancy while maintaining clean access patterns
    # =================================================================
    
    @property
    def tools(self) -> MCPToolClient:
        """
        Access to all 24 MCP tools via the tool client.
        
        Usage:
            # Instead of client.find_people_by_skill("python")
            response = await client.tools.find_people_by_skill("python")
            
            # Natural language search
            response = await client.tools.natural_language_search("Who are Python experts?")
            
            # Any of the 24 available tools
            response = await client.tools.find_domain_experts(["AI", "ML"])
        """
        return self.tool_client


# Only export the main client class
__all__ = ['MCPClient']

from typing import Dict, Any, Optional

from agent.mcp_client.base_client import MCPBaseClient
from agent.mcp_client.tool_client import MCPToolClient
from agent.mcp_client.types import (
    MCPClientConfig, 
    MCPResponse, 
    ToolCall, 
    MCPClientError
)

class MCPClient:
    """
    Main MCP client facade that provides access to all Connect MCP server functionality.
    
    This class combines the base client and tool client to provide a clean,
    high-level interface while maintaining modularity and testability.
    
    Usage:
        async with MCPClient() as client:
            # Core MCP operations
            await client.health_check()
            await client.list_tools()
            
            # Direct tool calls (generic)
            response = await client.call_tool("find_people_by_skill", {"skill": "python"})
            
            # Typed tool access (recommended)
            response = await client.tools.find_people_by_skill("python")
            response = await client.tools.natural_language_search("Who are Python experts?")
            
            if response.success:
                print(f"Success: {response.data}")
    """
    
    def __init__(
        self,
        base_url: str = "https://connect-vxll.onrender.com",
        api_key: str = "f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            api_key: X-API-Key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        # Create configuration
        self.config = MCPClientConfig(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        # Initialize modular components
        self.base_client = MCPBaseClient(self.config)
        self.tool_client = MCPToolClient(self.base_client)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.base_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.base_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def close(self):
        """Close the client and cleanup resources"""
        await self.base_client.close()
    
    # =================================================================
    # CORE MCP METHODS
    # =================================================================
    
    async def health_check(self) -> MCPResponse:
        """Check server health status"""
        return await self.tool_client.health_check()
    
    async def list_tools(self) -> MCPResponse:
        """List all available MCP tools"""
        return await self.tool_client.list_tools()
    
    async def call_tool(self, tool_name: str, arguments: dict) -> MCPResponse:
        """Call a specific MCP tool by name"""
        tool_call = ToolCall(tool_name, arguments)
        return await self.tool_client.call_tool(tool_call)
    
    # =================================================================
    # DYNAMIC TOOL ACCESS
    # All 24 MCP tools are accessible via the tool_client property
    # This eliminates redundancy while maintaining clean access patterns
    # =================================================================
    
    @property
    def tools(self) -> MCPToolClient:
        """
        Access to all 24 MCP tools via the tool client.
        
        Usage:
            # Instead of client.find_people_by_skill("python")
            response = await client.tools.find_people_by_skill("python")
            
            # Natural language search
            response = await client.tools.natural_language_search("Who are Python experts?")
            
            # Any of the 24 available tools
            response = await client.tools.find_domain_experts(["AI", "ML"])
        """
        return self.tool_client

# Only export the main client class
__all__ = [
    'MCPClient'
]