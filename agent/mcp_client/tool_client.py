"""
MCP Tool Client

This module provides high-level interfaces for all 14 MCP tools (13 query tools + health_check)
available in the Connect server. Each method corresponds to a specific tool and handles parameter
formatting and response processing.
"""

from typing import Dict, Any, List, Optional
from .base_client import MCPBaseClient
from .types import MCPResponse, ToolCall

class MCPToolClient:
    """
    High-level client for MCP tools.
    
    Provides clean Python interfaces for all 14 Connect MCP tools (13 query tools + health_check),
    handling parameter validation and response processing.
    """
    
    def __init__(self, base_client: MCPBaseClient):
        """
        Initialize tool client with base client.
        
        Args:
            base_client: Base MCP client for HTTP communication
        """
        self.base_client = base_client
    
    async def health_check(self) -> MCPResponse:
        """Check server health status"""
        return await self.base_client.make_request(
            "health_check", 
            endpoint="/health", 
            http_method="GET"
        )
    
    async def list_tools(self) -> MCPResponse:
        """List all available MCP tools"""
        return await self.base_client.make_request(
            "list_tools", 
            endpoint="/tools", 
            http_method="GET"
        )
    
    async def call_tool(self, tool_call: ToolCall) -> MCPResponse:
        """
        Call a specific MCP tool.
        
        Args:
            tool_call: Tool call specification
            
        Returns:
            MCPResponse with tool execution results
        """
        return await self.base_client.make_request(
            "tools/call", 
            tool_call.to_mcp_params()
        )
    
    # =================================================================
    # CORE PERSON PROFILE TOOLS (14 tools: 13 query tools + health_check)
    # =================================================================
    
    async def get_person_complete_profile(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get complete profile for a person including 12 essential properties and work history"""
        params = {}
        if person_id is not None:
            params["person_id"] = person_id
        if person_name is not None:
            params["person_name"] = person_name
        tool_call = ToolCall("get_person_complete_profile", params)
        return await self.call_tool(tool_call)
    
    async def find_person_by_name(self, name: str) -> MCPResponse:
        """Find a person by their name (case-insensitive partial matching)"""
        tool_call = ToolCall("find_person_by_name", {"name": name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_skill(self, skill: str) -> MCPResponse:
        """Find people with a specific skill (searches technical_skills, secondary_skills, domain_knowledge)"""
        tool_call = ToolCall("find_people_by_skill", {"skill": skill})
        return await self.call_tool(tool_call)
    
    async def find_people_by_technical_skill(self, skill: str) -> MCPResponse:
        """Find people by technical skills ONLY - searches technical_skills array (Python, AWS, ML, etc.)"""
        tool_call = ToolCall("find_people_by_technical_skill", {"skill": skill})
        return await self.call_tool(tool_call)
    
    async def find_people_by_secondary_skill(self, skill: str) -> MCPResponse:
        """Find people by secondary/soft skills ONLY - searches secondary_skills array (Leadership, Communication, etc.)"""
        tool_call = ToolCall("find_people_by_secondary_skill", {"skill": skill})
        return await self.call_tool(tool_call)
    
    async def find_people_by_current_company(self, company_name: str) -> MCPResponse:
        """Find CURRENT employees of a specific company - fast property-based search"""
        tool_call = ToolCall("find_people_by_current_company", {"company_name": company_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_company_history(self, company_name: str) -> MCPResponse:
        """Find ALL people who have worked at a specific company (current AND past employees)"""
        tool_call = ToolCall("find_people_by_company_history", {"company_name": company_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_institution(self, institution_name: str) -> MCPResponse:
        """Find people who studied at a specific institution or university"""
        tool_call = ToolCall("find_people_by_institution", {"institution_name": institution_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_location(self, location: str) -> MCPResponse:
        """Find people in a specific location or city"""
        tool_call = ToolCall("find_people_by_location", {"location": location})
        return await self.call_tool(tool_call)
    
    async def find_people_by_experience_level(
        self, 
        min_months: Optional[int] = None, 
        max_months: Optional[int] = None
    ) -> MCPResponse:
        """Find people based on total work experience in months"""
        params = {}
        if min_months is not None:
            params["min_months"] = min_months
        if max_months is not None:
            params["max_months"] = max_months
        tool_call = ToolCall("find_people_by_experience_level", params)
        return await self.call_tool(tool_call)
    
    async def get_person_job_descriptions(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get all job descriptions for a person with company and role details"""
        params = {}
        if person_id is not None:
            params["person_id"] = person_id
        if person_name is not None:
            params["person_name"] = person_name
        tool_call = ToolCall("get_person_job_descriptions", params)
        return await self.call_tool(tool_call)
    
    async def search_job_descriptions_by_keywords(
        self, 
        keywords: List[str], 
        match_type: str = "any"
    ) -> MCPResponse:
        """Search for people based on keywords in their job descriptions"""
        tool_call = ToolCall("search_job_descriptions_by_keywords", {
            "keywords": keywords,
            "match_type": match_type
        })
        return await self.call_tool(tool_call)
    
    async def find_domain_experts(self, domain_keywords: List[str]) -> MCPResponse:
        """Find people with deep domain expertise (requires at least 2 jobs in the domain)"""
        tool_call = ToolCall("find_domain_experts", {"domain_keywords": domain_keywords})
        return await self.call_tool(tool_call)