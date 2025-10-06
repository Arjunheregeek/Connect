# --- mcp/models/mcp_models.py ---
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum

# MCP Protocol Models based on the official MCP specification

class MCPRequestType(str, Enum):
    """MCP request types"""
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    GET_SCHEMA = "schema/get"
    PING = "ping"

class MCPRequest(BaseModel):
    """Base MCP request model"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None

class ListToolsRequest(MCPRequest):
    """Request to list available tools"""
    method: Literal["tools/list"] = "tools/list"

class CallToolRequest(MCPRequest):
    """Request to call a specific tool"""
    method: Literal["tools/call"] = "tools/call"
    params: Dict[str, Any] = Field(..., description="Tool call parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/call",
                "params": {
                    "name": "find_people_by_skill",
                    "arguments": {"skill": "python"}
                }
            }
        }

class MCPError(BaseModel):
    """MCP error model"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """Base MCP response model"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None

class ToolDefinition(BaseModel):
    """Tool definition model"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

class ListToolsResponse(MCPResponse):
    """Response for list tools request"""
    result: Dict[str, List[ToolDefinition]]

class ToolCallResult(BaseModel):
    """Result of a tool call"""
    content: List[Dict[str, Any]]
    isError: bool = False

class CallToolResponse(MCPResponse):
    """Response for tool call request"""
    result: ToolCallResult

# Error codes based on JSON-RPC specification
class MCPErrorCodes:
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

# Request/Response factory functions
def create_error_response(request_id: Union[str, int], code: int, message: str, data: Optional[Dict[str, Any]] = None) -> MCPResponse:
    """Create an error response"""
    return MCPResponse(
        id=request_id,
        error=MCPError(code=code, message=message, data=data)
    )

def create_success_response(request_id: Union[str, int], result: Dict[str, Any]) -> MCPResponse:
    """Create a success response"""
    return MCPResponse(id=request_id, result=result)

def create_tool_call_response(request_id: Union[str, int], content: List[Dict[str, Any]], is_error: bool = False) -> CallToolResponse:
    """Create a tool call response"""
    return CallToolResponse(
        id=request_id,
        result=ToolCallResult(content=content, isError=is_error)
    )