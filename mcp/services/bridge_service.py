# --- mcp/services/bridge_service.py ---
import sys
import os
from typing import Optional, List, Dict, Any

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.graph_db import GraphDB
from src.query import QueryManager
from src.natural_language_search import NaturalLanguageSearch
from mcp.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ConnectBridgeService:
    """
    Bridge service that connects MCP handlers with existing Connect components.
    This service maintains the connection to existing functionality while providing
    a clean interface for MCP operations.
    """
    
    def __init__(self):
        """Initialize the bridge service with existing Connect components"""
        self._db: Optional[GraphDB] = None
        self._query_manager: Optional[QueryManager] = None
        self._nl_search: Optional[NaturalLanguageSearch] = None
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
            
            # Initialize QueryManager
            logger.info("Initializing QueryManager...")
            self._query_manager = QueryManager(self._db)
            
            # Initialize Natural Language Search
            logger.info("Initializing Natural Language Search...")
            self._nl_search = NaturalLanguageSearch(
                self._db, 
                settings.openai_api_key
            )
            
            self._initialized = True
            logger.info("Connect Bridge Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Connect Bridge Service: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        if self._db:
            self._db.close()
            logger.info("Database connection closed")
    
    def _ensure_initialized(self) -> None:
        """Ensure the service is initialized before use"""
        if not self._initialized:
            raise RuntimeError("Bridge service not initialized. Call initialize() first.")
    
    # Query Manager Methods
    async def find_person_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find a person by their name"""
        self._ensure_initialized()
        return self._query_manager.find_person_by_name(name)
    
    async def find_people_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Find people with a specific skill"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_skill(skill)
    
    async def find_people_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Find people who worked at a specific company"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_company(company_name)
    
    async def find_colleagues_at_company(self, person_id: int, company_name: str) -> List[Dict[str, Any]]:
        """Find colleagues of a person at a specific company"""
        self._ensure_initialized()
        return self._query_manager.find_colleagues_at_company(person_id, company_name)
    
    # Additional Query Manager Methods
    async def find_people_by_institution(self, institution_name: str) -> List[Dict[str, Any]]:
        """Find people who studied at a specific institution"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_institution(institution_name)
    
    async def find_people_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Find people in a specific location"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_location(location)
    
    async def get_person_skills(self, person_name: str) -> List[Dict[str, Any]]:
        """Get all skills for a specific person"""
        self._ensure_initialized()
        return self._query_manager.get_person_skills(person_name)
    
    async def find_people_with_multiple_skills(self, skills_list: List[str], match_type: str = "any") -> List[Dict[str, Any]]:
        """Find people with multiple skills"""
        self._ensure_initialized()
        return self._query_manager.find_people_with_multiple_skills(skills_list, match_type)
    
    async def get_person_colleagues(self, person_name: str) -> List[Dict[str, Any]]:
        """Get all colleagues of a person"""
        self._ensure_initialized()
        return self._query_manager.get_person_colleagues(person_name)
    
    async def find_people_by_experience_level(self, min_months: Optional[int] = None, max_months: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find people by experience level"""
        self._ensure_initialized()
        return self._query_manager.find_people_by_experience_level(min_months, max_months)
    
    async def get_company_employees(self, company_name: str) -> List[Dict[str, Any]]:
        """Get all employees of a company"""
        self._ensure_initialized()
        return self._query_manager.get_company_employees(company_name)
    
    async def get_skill_popularity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular skills"""
        self._ensure_initialized()
        return self._query_manager.get_skill_popularity(limit)
    
    async def get_person_details(self, person_name: str) -> List[Dict[str, Any]]:
        """Get comprehensive person details"""
        self._ensure_initialized()
        return self._query_manager.get_person_details(person_name)

    # Natural Language Search Methods
    async def natural_language_search(self, question: str) -> str:
        """Perform natural language search"""
        self._ensure_initialized()
        return self._nl_search.search(question)
    
    # Health Check Methods
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
                "nl_search_ready": self._nl_search is not None
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