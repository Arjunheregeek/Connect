"""
MCP Client Types and Models

This module defines the data structures, enums, and type hints used throughout
the MCP client implementation. Keeping types separate improves maintainability
and provides clear interfaces.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, Union

class MCPErrorCode(Enum):
    """MCP Error Codes from JSON-RPC specification"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Custom MCP error codes
    TOOL_NOT_FOUND = -32000
    TOOL_EXECUTION_ERROR = -32001
    AUTHENTICATION_ERROR = -32002
    AUTHORIZATION_ERROR = -32003
    RATE_LIMIT_ERROR = -32004

@dataclass
class MCPResponse:
    """Structured MCP response with metadata"""
    success: bool
    data: Any = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    execution_time: Optional[float] = None
    
    @property
    def is_error(self) -> bool:
        """Check if response contains an error"""
        return not self.success
    
    @property
    def has_data(self) -> bool:
        """Check if response contains data"""
        return self.data is not None

@dataclass
class ToolCall:
    """Represents a tool call with its parameters"""
    name: str
    arguments: Dict[str, Any]
    
    def to_mcp_params(self) -> Dict[str, Any]:
        """Convert to MCP tool call parameters"""
        return {
            "name": self.name,
            "arguments": self.arguments
        }

@dataclass
class MCPClientConfig:
    """Configuration for MCP client"""
    base_url: str = "https://connect-vxll.onrender.com"
    api_key: str = "f435d1c3b1c5e66db047585265bbe4535a4b5f3389e134b54abe482b7b637ac3"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_limit: int = 100
    connection_per_host_limit: int = 20

class MCPClientError(Exception):
    """Custom exception for MCP client errors"""
    def __init__(
        self, 
        message: str, 
        error_code: Optional[int] = None, 
        response_data: Optional[Dict] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.response_data = response_data
        
    def __str__(self) -> str:
        if self.error_code:
            return f"MCPClientError({self.error_code}): {super().__str__()}"
        return f"MCPClientError: {super().__str__()}"