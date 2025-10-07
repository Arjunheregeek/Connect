# --- mcp/config/settings.py ---
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Configuration settings for the MCP server.
    All settings can be overridden by environment variables.
    """
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")  # Bind to all interfaces for Railway
    port: int = int(os.getenv("PORT", "8000"))  # Use Railway's assigned port
    debug: bool = False
    
    # Security Configuration
    mcp_api_key: str = os.getenv("MCP_API_KEY", "")
    
    # Neo4j Database Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo_username: str = os.getenv("NEO_USERNAME", "")
    neo_password: str = os.getenv("NEO_PASSWORD", "")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # MCP Server Configuration
    server_name: str = "Connect Knowledge Graph MCP Server"
    server_version: str = "1.0.0"
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
        
    def validate_required_settings(self) -> None:
        """Validate that all required settings are present"""
        required_settings = [
            ("mcp_api_key", "MCP_API_KEY"),
            ("neo4j_uri", "NEO4J_URI"), 
            ("neo_username", "NEO_USERNAME"),
            ("neo_password", "NEO_PASSWORD"),
            ("openai_api_key", "OPENAI_API_KEY")
        ]
        
        missing_settings = []
        for setting_name, env_var in required_settings:
            if not getattr(self, setting_name):
                missing_settings.append(env_var)
        
        if missing_settings:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_settings)}"
            )

# Global settings instance
settings = Settings()