# --- mcp/services/bridge_service.py ---
import sys
import os
from typing import Optional, List, Dict, Any

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.graph_db import GraphDB
from src.query import QueryManager
from mcp.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ConnectBridgeService:
    """
    Bridge service that connects MCP handlers with existing Connect components.
    This service maintains the connection to existing functionality while providing
    a clean interface for MCP operations.
    
    Updated to support exactly 19 tools matching tool_schemas.py
    """
    
    def __init__(self):
        """Initialize the bridge service with existing Connect components"""
        self._db: Optional[GraphDB] = None
        self._query_manager: Optional[QueryManager] = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """
        Initialize all components asynchronously.
        This allows for proper error handling during startup.
        """
        try:
            logger.info("Initializing Connect Bridge Service...")
            
            # Validate settings
            settings.validate_required_settings()
            
            # Initialize GraphDB connection
            logger.info("Connecting to Neo4j database...")
            self._db = GraphDB(
                uri=settings.neo4j_uri,
                user=settings.neo_username, 
                password=settings.neo_password
            )
            
            # Initialize Query Manager
            logger.info("Initializing Query Manager...")
            self._query_manager = QueryManager(self._db)
            
            self._initialized = True
            logger.info("Connect Bridge Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bridge service: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self._db:
                self._db.close()
            self._initialized = False
            logger.info("Bridge service cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _ensure_initialized(self):
        """Ensure the service is initialized before use"""
        if not self._initialized:
            raise RuntimeError("Bridge service not initialized. Call initialize() first.")
    
    # ============================================================================
    # Query Methods - 19 tools matching tool_schemas.py
    # ============================================================================
    
    async def get_person_complete_profile(self, person_id: Optional[int] = None, person_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get complete profile for a person including ALL 35 properties, work history, and education"""
        self._ensure_initialized()
        return self._query_manager.get_person_complete_profile(person_id=person_id, person_name=person_name)
    
    async def find_person_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find a person by their name - lightweight profile"""
        self._ensure_initialized()
        return self._query_manager.find_person_by_name(name)
    
    async def find_people_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Find all people who have a specific skill"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_skill(skill)
    
    async def find_people_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Find all people who have worked at a specific company"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_company(company_name)
    
    async def find_colleagues_at_company(self, person_id: int, company_name: str) -> List[Dict[str, Any]]:
        """Find colleagues of a specific person at a given company"""
        self._ensure_initialized()
        return self._query_manager.find_colleagues_at_company(person_id, company_name)
    
    async def find_people_by_institution(self, institution_name: str) -> List[Dict[str, Any]]:
        """Find all people who studied at a specific institution"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_institution(institution_name)
    
    async def find_people_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Find all people in a specific location"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_location(location)
    
    async def get_person_skills(self, person_id: Optional[int] = None, person_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all skills for a specific person"""
        self._ensure_initialized()
        return self._query_manager.get_person_skills(person_id=person_id, person_name=person_name)
    
    async def find_people_with_multiple_skills(self, skills_list: List[str], match_type: str = "any") -> List[Dict[str, Any]]:
        """Find people who have multiple specific skills"""
        self._ensure_initialized()
        return self._query_manager.find_people_with_multiple_skills(skills_list, match_type)
    
    async def get_person_colleagues(self, person_id: Optional[int] = None, person_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all colleagues of a person across all companies"""
        self._ensure_initialized()
        return self._query_manager.get_person_colleagues(person_id=person_id, person_name=person_name)
    
    async def find_people_by_experience_level(self, min_months: Optional[int] = None, max_months: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find people based on their total work experience"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_experience_level(min_months, max_months)
    
    async def get_company_employees(self, company_name: str) -> List[Dict[str, Any]]:
        """Get all employees (past and present) of a company"""
        self._ensure_initialized()
        return self._query_manager.get_company_employees(company_name)
    
    async def get_person_details(self, person_id: Optional[int] = None, person_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get comprehensive details about a person - summary view"""
        self._ensure_initialized()
        return self._query_manager.get_person_details(person_id=person_id, person_name=person_name)

    async def get_person_job_descriptions(self, person_id: Optional[int] = None, person_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all job descriptions for a person with company and role details"""
        self._ensure_initialized()
        return self._query_manager.get_person_job_descriptions(person_id=person_id, person_name=person_name)

    async def search_job_descriptions_by_keywords(self, keywords: List[str], match_type: str = "any") -> List[Dict[str, Any]]:
        """Search for people based on keywords in their job descriptions"""
        self._ensure_initialized()
        return self._query_manager.search_job_descriptions_by_keywords(keywords, match_type)

    async def find_technical_skills_in_descriptions(self, tech_keywords: List[str]) -> List[Dict[str, Any]]:
        """Find people who mention specific technical skills in their job descriptions"""
        self._ensure_initialized()
        return self._query_manager.find_technical_skills_in_descriptions(tech_keywords)

    async def find_leadership_indicators(self) -> List[Dict[str, Any]]:
        """Find people with leadership indicators in their job descriptions"""
        self._ensure_initialized()
        return self._query_manager.find_leadership_indicators()

    async def find_domain_experts(self, domain_keywords: List[str]) -> List[Dict[str, Any]]:
        """Find people with deep domain expertise based on job description analysis"""
        self._ensure_initialized()
        return self._query_manager.find_domain_experts(domain_keywords)

    # ============================================================================
    # Health Check Method
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of all components"""
        try:
            self._ensure_initialized()
            
            # Test database connection
            test_query = "MATCH (n) RETURN count(n) as node_count LIMIT 1"
            result = self._db.execute_query(test_query)
            node_count = result[0]["node_count"] if result else 0
            
            return {
                "status": "healthy",
                "database_connected": True,
                "node_count": node_count,
                "query_manager_ready": self._query_manager is not None,
                "total_tools": 19
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_connected": False
            }

# Global bridge service instance
bridge_service = ConnectBridgeService()
