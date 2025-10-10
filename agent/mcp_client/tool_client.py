"""
MCP Tool Client

This module provides high-level interfaces for all 19 MCP tools available in the
Connect server. Each method corresponds to a specific tool and handles parameter
formatting and response processing.
"""

from typing import Dict, Any, List, Optional
from .base_client import MCPBaseClient
from .types import MCPResponse, ToolCall

class MCPToolClient:
    """
    High-level client for MCP tools.
    
    Provides clean Python interfaces for all 19 Connect MCP tools,
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
    # CORE PERSON PROFILE TOOLS (13 tools)
    # =================================================================
    
    async def get_person_complete_profile(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get complete profile for a person including ALL 35 properties, work history, and education"""
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
    
    async def find_people_by_company(self, company_name: str) -> MCPResponse:
        """Find people who worked at a specific company (current or past)"""
        tool_call = ToolCall("find_people_by_company", {"company_name": company_name})
        return await self.call_tool(tool_call)
    
    async def find_colleagues_at_company(self, person_id: int, company_name: str) -> MCPResponse:
        """Find colleagues of a person at a specific company"""
        tool_call = ToolCall("find_colleagues_at_company", {
            "person_id": person_id,
            "company_name": company_name
        })
        return await self.call_tool(tool_call)
    
    async def find_people_by_institution(self, institution_name: str) -> MCPResponse:
        """Find people who studied at a specific institution or university"""
        tool_call = ToolCall("find_people_by_institution", {"institution_name": institution_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_location(self, location: str) -> MCPResponse:
        """Find people in a specific location or city"""
        tool_call = ToolCall("find_people_by_location", {"location": location})
        return await self.call_tool(tool_call)
    
    async def get_person_skills(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get all skills for a specific person from their skill arrays"""
        params = {}
        if person_id is not None:
            params["person_id"] = person_id
        if person_name is not None:
            params["person_name"] = person_name
        tool_call = ToolCall("get_person_skills", params)
        return await self.call_tool(tool_call)
    
    async def find_people_with_multiple_skills(
        self, 
        skills_list: List[str], 
        match_type: str = "any"
    ) -> MCPResponse:
        """Find people with multiple skills (AND/OR logic)"""
        tool_call = ToolCall("find_people_with_multiple_skills", {
            "skills_list": skills_list,
            "match_type": match_type
        })
        return await self.call_tool(tool_call)
    
    async def get_person_colleagues(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get all colleagues of a person across all companies they worked at"""
        params = {}
        if person_id is not None:
            params["person_id"] = person_id
        if person_name is not None:
            params["person_name"] = person_name
        tool_call = ToolCall("get_person_colleagues", params)
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
    
    async def get_company_employees(self, company_name: str) -> MCPResponse:
        """Get all employees (past and present) of a specific company"""
        tool_call = ToolCall("get_company_employees", {"company_name": company_name})
        return await self.call_tool(tool_call)
    
    async def get_person_details(
        self, 
        person_id: Optional[int] = None, 
        person_name: Optional[str] = None
    ) -> MCPResponse:
        """Get comprehensive details about a person - summary view"""
        params = {}
        if person_id is not None:
            params["person_id"] = person_id
        if person_name is not None:
            params["person_name"] = person_name
        tool_call = ToolCall("get_person_details", params)
        return await self.call_tool(tool_call)
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (5 tools)
    # =================================================================
    
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
    
    async def find_technical_skills_in_descriptions(self, tech_keywords: List[str]) -> MCPResponse:
        """Find people who mention specific technical skills in their job descriptions"""
        tool_call = ToolCall("find_technical_skills_in_descriptions", {"tech_keywords": tech_keywords})
        return await self.call_tool(tool_call)
    
    async def find_leadership_indicators(self) -> MCPResponse:
        """Find people with leadership indicators in their job descriptions"""
        tool_call = ToolCall("find_leadership_indicators", {})
        return await self.call_tool(tool_call)
    
    async def find_domain_experts(self, domain_keywords: List[str]) -> MCPResponse:
        """Find people with deep domain expertise (requires at least 2 jobs in the domain)"""
        tool_call = ToolCall("find_domain_experts", {"domain_keywords": domain_keywords})
        return await self.call_tool(tool_call)