# --- mcp/handlers/mcp_handlers.py ---
import logging
from typing import Dict, Any, List
from mcp.models.mcp_models import (
    MCPRequest, MCPResponse, ListToolsRequest, CallToolRequest,
    create_error_response, create_success_response, create_tool_call_response,
    MCPErrorCodes, ToolDefinition
)
from mcp.schemas.tool_schemas import MCP_TOOLS
from mcp.utils.input_validation import InputValidator
from mcp.utils.caching import cache_manager
from mcp.services.bridge_service import bridge_service

logger = logging.getLogger(__name__)

class MCPHandler:
    """Handles MCP protocol requests and routes them to appropriate handlers - 19 tools"""
    
    def __init__(self):
        self.tool_handlers = {
            "get_person_complete_profile": self._handle_get_person_complete_profile,
            "find_person_by_name": self._handle_find_person_by_name,
            "find_people_by_skill": self._handle_find_people_by_skill,
            "find_people_by_company": self._handle_find_people_by_company,
            "find_colleagues_at_company": self._handle_find_colleagues_at_company,
            "find_people_by_institution": self._handle_find_people_by_institution,
            "find_people_by_location": self._handle_find_people_by_location,
            "get_person_skills": self._handle_get_person_skills,
            "find_people_with_multiple_skills": self._handle_find_people_with_multiple_skills,
            "get_person_colleagues": self._handle_get_person_colleagues,
            "find_people_by_experience_level": self._handle_find_people_by_experience_level,
            "get_company_employees": self._handle_get_company_employees,
            "get_person_details": self._handle_get_person_details,
            "get_person_job_descriptions": self._handle_get_person_job_descriptions,
            "search_job_descriptions_by_keywords": self._handle_search_job_descriptions_by_keywords,
            "find_technical_skills_in_descriptions": self._handle_find_technical_skills_in_descriptions,
            "find_leadership_indicators": self._handle_find_leadership_indicators,
            "find_domain_experts": self._handle_find_domain_experts,
            "health_check": self._handle_health_check
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Main entry point for handling MCP requests
        
        Args:
            request: The MCP request to handle
            
        Returns:
            MCPResponse: The response to send back to the client
        """
        try:
            method = request.method
            
            if method == "tools/list":
                return await self._handle_list_tools(request)
            elif method == "tools/call":
                return await self._handle_call_tool(request)
            else:
                logger.warning(f"Unknown method: {method}")
                return create_error_response(
                    request_id=request.id,
                    code=MCPErrorCodes.METHOD_NOT_FOUND,
                    message=f"Unknown method: {method}"
                )
                
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return create_error_response(
                request_id=request.id,
                code=MCPErrorCodes.INTERNAL_ERROR,
                message=f"Internal error: {str(e)}"
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
                request_id=request.id,
                result={"tools": [tool.dict() for tool in tools]}
            )
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return create_error_response(
                request_id=request.id,
                code=MCPErrorCodes.INTERNAL_ERROR,
                message=str(e)
            )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request"""
        try:
            params = request.params or {}
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return create_error_response(
                    request_id=request.id,
                    code=MCPErrorCodes.INVALID_PARAMS,
                    message="Missing tool name"
                )
            
            # Check if tool exists
            if tool_name not in self.tool_handlers:
                return create_error_response(
                    request_id=request.id,
                    code=MCPErrorCodes.METHOD_NOT_FOUND,
                    message=f"Unknown tool: {tool_name}"
                )
            
            # Validate input
            try:
                InputValidator.validate_tool_input(tool_name, arguments)
            except ValueError as e:
                return create_error_response(
                    request_id=request.id,
                    code=MCPErrorCodes.INVALID_PARAMS,
                    message=f"Invalid arguments: {str(e)}"
                )
            
            # Check cache
            cached_result = await cache_manager.get_cached_result(tool_name, arguments)
            
            if cached_result is not None:
                logger.info(f"Cache hit for {tool_name}")
                return create_tool_call_response(
                    request_id=request.id,
                    content=[{
                        "type": "text",
                        "text": str(cached_result)
                    }]
                )
            
            # Execute tool
            handler = self.tool_handlers[tool_name]
            result = await handler(arguments)
            
            # Cache result
            await cache_manager.cache_result(tool_name, arguments, result)
            
            # Return response
            return create_tool_call_response(
                request_id=request.id,
                content=[{
                    "type": "text",
                    "text": str(result)
                }]
            )
            
        except Exception as e:
            logger.error(f"Error calling tool: {e}", exc_info=True)
            return create_error_response(
                request_id=request.id,
                code=MCPErrorCodes.INTERNAL_ERROR,
                message=str(e)
            )
    
    # ============================================================================
    # Tool Handler Methods - 19 handlers matching tool_schemas.py
    # ============================================================================
    
    async def _handle_get_person_complete_profile(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get complete profile for a person including ALL properties"""
        person_id = arguments.get("person_id")
        person_name = arguments.get("person_name")
        
        if not person_id and not person_name:
            raise ValueError("Must provide either person_id or person_name")
        
        result = await bridge_service.get_person_complete_profile(
            person_id=person_id,
            person_name=person_name
        )
        
        logger.info(f"Retrieved complete profile: {len(result)} records")
        return result
    
    async def _handle_find_person_by_name(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find a person by name"""
        name = arguments.get("name")
        
        if not name:
            raise ValueError("Name is required")
        
        result = await bridge_service.find_person_by_name(name)
        
        logger.info(f"Found {len(result)} people matching name: {name}")
        return result
    
    async def _handle_find_people_by_skill(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people by skill"""
        skill = arguments.get("skill")
        
        if not skill:
            raise ValueError("Skill is required")
        
        result = await bridge_service.find_people_by_skill(skill)
        
        logger.info(f"Found {len(result)} people with skill: {skill}")
        return result
    
    async def _handle_find_people_by_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people by company"""
        company_name = arguments.get("company_name")
        
        if not company_name:
            raise ValueError("Company name is required")
        
        result = await bridge_service.find_people_by_company(company_name)
        
        logger.info(f"Found {len(result)} people at company: {company_name}")
        return result
    
    async def _handle_find_colleagues_at_company(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find colleagues at a specific company"""
        person_id = arguments.get("person_id")
        company_name = arguments.get("company_name")
        
        if not person_id or not company_name:
            raise ValueError("Both person_id and company_name are required")
        
        result = await bridge_service.find_colleagues_at_company(person_id, company_name)
        
        logger.info(f"Found {len(result)} colleagues at {company_name}")
        return result
    
    async def _handle_find_people_by_institution(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people by institution"""
        institution_name = arguments.get("institution_name")
        
        if not institution_name:
            raise ValueError("Institution name is required")
        
        result = await bridge_service.find_people_by_institution(institution_name)
        
        logger.info(f"Found {len(result)} people from institution: {institution_name}")
        return result
    
    async def _handle_find_people_by_location(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people by location"""
        location = arguments.get("location")
        
        if not location:
            raise ValueError("Location is required")
        
        result = await bridge_service.find_people_by_location(location)
        
        logger.info(f"Found {len(result)} people in location: {location}")
        return result
    
    async def _handle_get_person_skills(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all skills for a person"""
        person_id = arguments.get("person_id")
        person_name = arguments.get("person_name")
        
        if not person_id and not person_name:
            raise ValueError("Must provide either person_id or person_name")
        
        result = await bridge_service.get_person_skills(
            person_id=person_id,
            person_name=person_name
        )
        
        logger.info(f"Retrieved skills for person")
        return result
    
    async def _handle_find_people_with_multiple_skills(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people with multiple skills"""
        skills_list = arguments.get("skills_list", [])
        match_type = arguments.get("match_type", "any")
        
        if not skills_list:
            raise ValueError("Skills list is required")
        
        result = await bridge_service.find_people_with_multiple_skills(skills_list, match_type)
        
        logger.info(f"Found {len(result)} people with skills: {skills_list}")
        return result
    
    async def _handle_get_person_colleagues(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all colleagues of a person"""
        person_id = arguments.get("person_id")
        person_name = arguments.get("person_name")
        
        if not person_id and not person_name:
            raise ValueError("Must provide either person_id or person_name")
        
        result = await bridge_service.get_person_colleagues(
            person_id=person_id,
            person_name=person_name
        )
        
        logger.info(f"Retrieved {len(result)} colleagues")
        return result
    
    async def _handle_find_people_by_experience_level(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people by experience level"""
        min_months = arguments.get("min_months")
        max_months = arguments.get("max_months")
        
        result = await bridge_service.find_people_by_experience_level(min_months, max_months)
        
        logger.info(f"Found {len(result)} people with experience level")
        return result
    
    async def _handle_get_company_employees(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all employees of a company"""
        company_name = arguments.get("company_name")
        
        if not company_name:
            raise ValueError("Company name is required")
        
        result = await bridge_service.get_company_employees(company_name)
        
        logger.info(f"Found {len(result)} employees at {company_name}")
        return result
    
    async def _handle_get_person_details(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get comprehensive person details"""
        person_id = arguments.get("person_id")
        person_name = arguments.get("person_name")
        
        if not person_id and not person_name:
            raise ValueError("Must provide either person_id or person_name")
        
        result = await bridge_service.get_person_details(
            person_id=person_id,
            person_name=person_name
        )
        
        logger.info(f"Retrieved person details")
        return result
    
    async def _handle_get_person_job_descriptions(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all job descriptions for a person"""
        person_id = arguments.get("person_id")
        person_name = arguments.get("person_name")
        
        if not person_id and not person_name:
            raise ValueError("Must provide either person_id or person_name")
        
        result = await bridge_service.get_person_job_descriptions(
            person_id=person_id,
            person_name=person_name
        )
        
        logger.info(f"Retrieved {len(result)} job descriptions")
        return result
    
    async def _handle_search_job_descriptions_by_keywords(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search job descriptions by keywords"""
        keywords = arguments.get("keywords", [])
        match_type = arguments.get("match_type", "any")
        
        if not keywords:
            raise ValueError("Keywords list is required")
        
        result = await bridge_service.search_job_descriptions_by_keywords(keywords, match_type)
        
        logger.info(f"Found {len(result)} people matching keywords: {keywords}")
        return result
    
    async def _handle_find_technical_skills_in_descriptions(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find technical skills in job descriptions"""
        tech_keywords = arguments.get("tech_keywords", [])
        
        if not tech_keywords:
            raise ValueError("Tech keywords list is required")
        
        result = await bridge_service.find_technical_skills_in_descriptions(tech_keywords)
        
        logger.info(f"Found {len(result)} people with tech skills: {tech_keywords}")
        return result
    
    async def _handle_find_leadership_indicators(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find people with leadership indicators"""
        result = await bridge_service.find_leadership_indicators()
        
        logger.info(f"Found {len(result)} people with leadership indicators")
        return result
    
    async def _handle_find_domain_experts(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find domain experts"""
        domain_keywords = arguments.get("domain_keywords", [])
        
        if not domain_keywords:
            raise ValueError("Domain keywords list is required")
        
        result = await bridge_service.find_domain_experts(domain_keywords)
        
        logger.info(f"Found {len(result)} domain experts in: {domain_keywords}")
        return result
    
    async def _handle_health_check(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform health check"""
        result = await bridge_service.health_check()
        
        logger.info(f"Health check status: {result.get('status')}")
        return result

# Global handler instance
mcp_handler = MCPHandler()
