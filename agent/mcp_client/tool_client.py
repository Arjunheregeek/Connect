"""
MCP Tool Client

This module provides high-level interfaces for all 24 MCP tools available in the
Connect server. Each method corresponds to a specific tool and handles parameter
formatting and response processing.
"""

from typing import Dict, Any, List, Optional
from .base_client import MCPBaseClient
from .types import MCPResponse, ToolCall

class MCPToolClient:
    """
    High-level client for MCP tools.
    
    Provides clean Python interfaces for all 24 Connect MCP tools,
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
    # CORE SEARCH TOOLS (15 tools)
    # =================================================================
    
    async def find_person_by_name(self, name: str) -> MCPResponse:
        """Find a person by their name (partial matching supported)"""
        tool_call = ToolCall("find_person_by_name", {"name": name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_skill(self, skill: str) -> MCPResponse:
        """Find people with a specific skill"""
        tool_call = ToolCall("find_people_by_skill", {"skill": skill})
        return await self.call_tool(tool_call)
    
    async def find_people_by_company(self, company_name: str) -> MCPResponse:
        """Find people who worked at a specific company"""
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
        """Find people who studied at a specific institution"""
        tool_call = ToolCall("find_people_by_institution", {"institution_name": institution_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_location(self, location: str) -> MCPResponse:
        """Find people in a specific location"""
        tool_call = ToolCall("find_people_by_location", {"location": location})
        return await self.call_tool(tool_call)
    
    async def get_person_skills(self, person_name: str) -> MCPResponse:
        """Get all skills for a specific person"""
        tool_call = ToolCall("get_person_skills", {"person_name": person_name})
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
    
    async def get_person_colleagues(self, person_name: str) -> MCPResponse:
        """Get all colleagues of a person across all companies"""
        tool_call = ToolCall("get_person_colleagues", {"person_name": person_name})
        return await self.call_tool(tool_call)
    
    async def find_people_by_experience_level(
        self, 
        min_months: Optional[int] = None, 
        max_months: Optional[int] = None
    ) -> MCPResponse:
        """Find people based on experience level in months"""
        params = {}
        if min_months is not None:
            params["min_months"] = min_months
        if max_months is not None:
            params["max_months"] = max_months
        
        tool_call = ToolCall("find_people_by_experience_level", params)
        return await self.call_tool(tool_call)
    
    async def get_company_employees(self, company_name: str) -> MCPResponse:
        """Get all employees of a specific company"""
        tool_call = ToolCall("get_company_employees", {"company_name": company_name})
        return await self.call_tool(tool_call)
    
    async def get_skill_popularity(self, limit: int = 20) -> MCPResponse:
        """Get most popular skills"""
        tool_call = ToolCall("get_skill_popularity", {"limit": limit})
        return await self.call_tool(tool_call)
    
    async def get_person_details(self, person_name: str) -> MCPResponse:
        """Get comprehensive details for a person"""
        tool_call = ToolCall("get_person_details", {"person_name": person_name})
        return await self.call_tool(tool_call)
    
    async def natural_language_search(self, question: str) -> MCPResponse:
        """
        Perform natural language search - the most powerful tool for complex queries.
        
        This tool uses AI to interpret natural language questions and convert them
        into appropriate Neo4j queries, making it ideal for complex, multi-faceted searches.
        """
        tool_call = ToolCall("natural_language_search", {"question": question})
        return await self.call_tool(tool_call)
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (9 tools)
    # =================================================================
    
    async def get_person_job_descriptions(self, person_name: str) -> MCPResponse:
        """Get all job descriptions for a person"""
        tool_call = ToolCall("get_person_job_descriptions", {"person_name": person_name})
        return await self.call_tool(tool_call)
    
    async def search_job_descriptions_by_keywords(
        self, 
        keywords: List[str], 
        match_type: str = "any"
    ) -> MCPResponse:
        """Search job descriptions by keywords"""
        tool_call = ToolCall("search_job_descriptions_by_keywords", {
            "keywords": keywords,
            "match_type": match_type
        })
        return await self.call_tool(tool_call)
    
    async def find_technical_skills_in_descriptions(self, tech_keywords: List[str]) -> MCPResponse:
        """Find people with technical skills mentioned in job descriptions"""
        tool_call = ToolCall("find_technical_skills_in_descriptions", {"tech_keywords": tech_keywords})
        return await self.call_tool(tool_call)
    
    async def find_leadership_indicators(self) -> MCPResponse:
        """Find people with leadership indicators in job descriptions"""
        tool_call = ToolCall("find_leadership_indicators", {})
        return await self.call_tool(tool_call)
    
    async def find_achievement_patterns(self) -> MCPResponse:
        """Find people with quantifiable achievements"""
        tool_call = ToolCall("find_achievement_patterns", {})
        return await self.call_tool(tool_call)
    
    async def analyze_career_progression(self, person_name: str) -> MCPResponse:
        """Analyze a person's career progression"""
        tool_call = ToolCall("analyze_career_progression", {"person_name": person_name})
        return await self.call_tool(tool_call)
    
    async def find_domain_experts(self, domain_keywords: List[str]) -> MCPResponse:
        """Find people with deep domain expertise"""
        tool_call = ToolCall("find_domain_experts", {"domain_keywords": domain_keywords})
        return await self.call_tool(tool_call)
    
    async def find_similar_career_paths(
        self, 
        reference_person_name: str, 
        similarity_threshold: int = 2
    ) -> MCPResponse:
        """Find people with similar career paths"""
        tool_call = ToolCall("find_similar_career_paths", {
            "reference_person_name": reference_person_name,
            "similarity_threshold": similarity_threshold
        })
        return await self.call_tool(tool_call)
    
    async def find_role_transition_patterns(
        self, 
        from_role_keywords: List[str], 
        to_role_keywords: List[str]
    ) -> MCPResponse:
        """Find people who transitioned between role types"""
        tool_call = ToolCall("find_role_transition_patterns", {
            "from_role_keywords": from_role_keywords,
            "to_role_keywords": to_role_keywords
        })
        return await self.call_tool(tool_call)