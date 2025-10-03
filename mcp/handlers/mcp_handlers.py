# --- mcp/handlers/mcp_handlers.py ---
import logging
from typing import Dict, Any, List
from mcp.models.mcp_models import (
    MCPRequest, MCPResponse, ListToolsRequest, CallToolRequest,
    create_error_response, create_success_response, create_tool_call_response,
    MCPErrorCodes, ToolDefinition
)
from mcp.schemas.tool_schemas import MCP_TOOLS, validate_tool_input
from mcp.services.bridge_service import bridge_service

logger = logging.getLogger(__name__)

class MCPHandler:
    """Handles MCP protocol requests and routes them to appropriate handlers"""
    
    def __init__(self):
        self.tool_handlers = {
            "find_person_by_name": self._handle_find_person_by_name,
            "find_people_by_skill": self._handle_find_people_by_skill,
            "find_people_by_company": self._handle_find_people_by_company,
            "find_colleagues_at_company": self._handle_find_colleagues_at_company,
            "natural_language_search": self._handle_natural_language_search,
            "health_check": self._handle_health_check
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Main entry point for handling MCP requests
        
        Args:
            request: The MCP request to handle
            
        Returns:
            MCPResponse with the result or error
        """
        try:
            if request.method == "tools/list":
                return await self._handle_list_tools(request)
            elif request.method == "tools/call":
                return await self._handle_call_tool(request)
            else:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.METHOD_NOT_FOUND,
                    f"Method '{request.method}' not found"
                )
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return create_error_response(
                request.id,
                MCPErrorCodes.INTERNAL_ERROR,
                f"Internal server error: {str(e)}"
            )
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        try:
            tools = [
                ToolDefinition(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"]
                )
                for tool in MCP_TOOLS
            ]
            
            return create_success_response(
                request.id,
                {"tools": [tool.dict() for tool in tools]}
            )
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return create_error_response(
                request.id,
                MCPErrorCodes.INTERNAL_ERROR,
                f"Failed to list tools: {str(e)}"
            )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request"""
        try:
            if not request.params:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.INVALID_PARAMS,
                    "Missing parameters for tool call"
                )
            
            tool_name = request.params.get("name")
            tool_arguments = request.params.get("arguments", {})
            
            if not tool_name:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.INVALID_PARAMS,
                    "Missing 'name' parameter"
                )
            
            if tool_name not in self.tool_handlers:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.TOOL_NOT_FOUND,
                    f"Tool '{tool_name}' not found"
                )
            
            # Validate input
            try:
                validate_tool_input(tool_name, tool_arguments)
            except ValueError as e:
                return create_error_response(
                    request.id,
                    MCPErrorCodes.INVALID_PARAMS,
                    str(e)
                )
            
            # Execute tool
            handler = self.tool_handlers[tool_name]
            result = await handler(tool_arguments)
            
            return create_tool_call_response(request.id, result)
            
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            return create_error_response(
                request.id,
                MCPErrorCodes.TOOL_EXECUTION_ERROR,
                f"Tool execution failed: {str(e)}"
            )
    
    # Tool handler methods
    async def _handle_find_person_by_name(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_person_by_name tool"""
        name = arguments["name"]
        results = await bridge_service.find_person_by_name(name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people matching '{name}':" + 
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})" 
                       for person in results
                   ]) if results else f"No people found matching '{name}'"
        }]
    
    async def _handle_find_people_by_skill(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_skill tool"""
        skill = arguments["skill"]
        results = await bridge_service.find_people_by_skill(skill)
        
        return [{
            "type": "text", 
            "text": f"Found {len(results)} people with '{skill}' skills:" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results
                   ]) if results else f"No people found with '{skill}' skills"
        }]
    
    async def _handle_find_people_by_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_people_by_company tool"""
        company_name = arguments["company_name"]
        results = await bridge_service.find_people_by_company(company_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} people who worked at '{company_name}':" +
                   "\n" + "\n".join([
                       f"- {person['name']} ({person['headline']})"
                       for person in results  
                   ]) if results else f"No people found who worked at '{company_name}'"
        }]
    
    async def _handle_find_colleagues_at_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle find_colleagues_at_company tool"""
        person_id = arguments["person_id"]
        company_name = arguments["company_name"]
        results = await bridge_service.find_colleagues_at_company(person_id, company_name)
        
        return [{
            "type": "text",
            "text": f"Found {len(results)} colleagues of person ID {person_id} at '{company_name}':" +
                   "\n" + "\n".join([
                       f"- {colleague['colleague_name']} ({colleague['colleague_headline']})"
                       for colleague in results
                   ]) if results else f"No colleagues found for person ID {person_id} at '{company_name}'"
        }]
    
    async def _handle_natural_language_search(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle natural_language_search tool"""
        question = arguments["question"]
        result = await bridge_service.natural_language_search(question)
        
        return [{
            "type": "text",
            "text": result
        }]
    
    async def _handle_health_check(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle health_check tool"""
        health_status = await bridge_service.health_check()
        
        return [{
            "type": "text",
            "text": f"Health Status: {health_status['status']}\n" +
                   f"Database Connected: {health_status.get('database_connected', False)}\n" +
                   f"Node Count: {health_status.get('node_count', 'Unknown')}\n" +
                   f"Query Manager Ready: {health_status.get('query_manager_ready', False)}\n" +
                   f"NL Search Ready: {health_status.get('nl_search_ready', False)}"
        }]

# Global handler instance
mcp_handler = MCPHandler()