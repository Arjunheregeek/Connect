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

from typing import List, Optional

from .types import MCPClientConfig, MCPResponse, MCPClientError, ToolCall
from .base_client import MCPBaseClient
from .tool_client import MCPToolClient

class MCPClient:
    """
    Main MCP client facade that provides access to all Connect MCP server functionality.
    
    This class combines the base client and tool client to provide a clean,
    high-level interface while maintaining modularity and testability.
    
    Usage:
        async with MCPClient() as client:
            response = await client.find_people_by_skill("python")
            if response.success:
                print(f"Found {len(response.data)} people")
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
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
    # CORE SEARCH TOOLS (15 tools)
    # Delegated to tool_client for clean separation of concerns
    # =================================================================
    
    async def find_person_by_name(self, name: str) -> MCPResponse:
        """Find a person by their name (partial matching supported)"""
        return await self.tool_client.find_person_by_name(name)
    
    async def find_people_by_skill(self, skill: str) -> MCPResponse:
        """Find people with a specific skill"""
        return await self.tool_client.find_people_by_skill(skill)
    
    async def find_people_by_company(self, company_name: str) -> MCPResponse:
        """Find people who worked at a specific company"""
        return await self.tool_client.find_people_by_company(company_name)
    
    async def find_colleagues_at_company(self, person_id: int, company_name: str) -> MCPResponse:
        """Find colleagues of a person at a specific company"""
        return await self.tool_client.find_colleagues_at_company(person_id, company_name)
    
    async def find_people_by_institution(self, institution_name: str) -> MCPResponse:
        """Find people who studied at a specific institution"""
        return await self.tool_client.find_people_by_institution(institution_name)
    
    async def find_people_by_location(self, location: str) -> MCPResponse:
        """Find people in a specific location"""
        return await self.tool_client.find_people_by_location(location)
    
    async def get_person_skills(self, person_name: str) -> MCPResponse:
        """Get all skills for a specific person"""
        return await self.tool_client.get_person_skills(person_name)
    
    async def find_people_with_multiple_skills(
        self, 
        skills_list: List[str], 
        match_type: str = "any"
    ) -> MCPResponse:
        """Find people with multiple skills (AND/OR logic)"""
        return await self.tool_client.find_people_with_multiple_skills(skills_list, match_type)
    
    async def get_person_colleagues(self, person_name: str) -> MCPResponse:
        """Get all colleagues of a person across all companies"""
        return await self.tool_client.get_person_colleagues(person_name)
    
    async def find_people_by_experience_level(
        self, 
        min_months: Optional[int] = None, 
        max_months: Optional[int] = None
    ) -> MCPResponse:
        """Find people based on experience level in months"""
        return await self.tool_client.find_people_by_experience_level(min_months, max_months)
    
    async def get_company_employees(self, company_name: str) -> MCPResponse:
        """Get all employees of a specific company"""
        return await self.tool_client.get_company_employees(company_name)
    
    async def get_skill_popularity(self, limit: int = 20) -> MCPResponse:
        """Get most popular skills"""
        return await self.tool_client.get_skill_popularity(limit)
    
    async def get_person_details(self, person_name: str) -> MCPResponse:
        """Get comprehensive details for a person"""
        return await self.tool_client.get_person_details(person_name)
    
    async def natural_language_search(self, question: str) -> MCPResponse:
        """
        Perform natural language search - the most powerful tool for complex queries.
        
        This tool uses AI to interpret natural language questions and convert them
        into appropriate Neo4j queries, making it ideal for complex, multi-faceted searches.
        """
        return await self.tool_client.natural_language_search(question)
    
    # =================================================================
    # JOB DESCRIPTION ANALYSIS TOOLS (9 tools)
    # =================================================================
    
    async def get_person_job_descriptions(self, person_name: str) -> MCPResponse:
        """Get all job descriptions for a person"""
        return await self.tool_client.get_person_job_descriptions(person_name)
    
    async def search_job_descriptions_by_keywords(
        self, 
        keywords: List[str], 
        match_type: str = "any"
    ) -> MCPResponse:
        """Search job descriptions by keywords"""
        return await self.tool_client.search_job_descriptions_by_keywords(keywords, match_type)
    
    async def find_technical_skills_in_descriptions(self, tech_keywords: List[str]) -> MCPResponse:
        """Find people with technical skills mentioned in job descriptions"""
        return await self.tool_client.find_technical_skills_in_descriptions(tech_keywords)
    
    async def find_leadership_indicators(self) -> MCPResponse:
        """Find people with leadership indicators in job descriptions"""
        return await self.tool_client.find_leadership_indicators()
    
    async def find_achievement_patterns(self) -> MCPResponse:
        """Find people with quantifiable achievements"""
        return await self.tool_client.find_achievement_patterns()
    
    async def analyze_career_progression(self, person_name: str) -> MCPResponse:
        """Analyze a person's career progression"""
        return await self.tool_client.analyze_career_progression(person_name)
    
    async def find_domain_experts(self, domain_keywords: List[str]) -> MCPResponse:
        """Find people with deep domain expertise"""
        return await self.tool_client.find_domain_experts(domain_keywords)
    
    async def find_similar_career_paths(
        self, 
        reference_person_name: str, 
        similarity_threshold: int = 2
    ) -> MCPResponse:
        """Find people with similar career paths"""
        return await self.tool_client.find_similar_career_paths(reference_person_name, similarity_threshold)
    
    async def find_role_transition_patterns(
        self, 
        from_role_keywords: List[str], 
        to_role_keywords: List[str]
    ) -> MCPResponse:
        """Find people who transitioned between role types"""
        return await self.tool_client.find_role_transition_patterns(from_role_keywords, to_role_keywords)

# Re-export key types for convenience
__all__ = [
    'MCPClient',
    'MCPResponse', 
    'MCPClientError',
    'MCPClientConfig',
    'ToolCall'
]