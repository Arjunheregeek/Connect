# --- mcp/utils/security.py ---
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from mcp.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Define API key header security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the X-API-Key header.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("Request made without API key")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Missing API Key",
                "message": "X-API-Key header is required",
                "type": "authentication_error"
            }
        )
    
    if api_key != settings.mcp_api_key:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Invalid API Key", 
                "message": "The provided API key is not valid",
                "type": "authorization_error"
            }
        )
    
    logger.info("API key validated successfully")
    return api_key

class SecurityManager:
    """Centralized security management for the MCP server"""
    
    @staticmethod
    def validate_settings():
        """Validate security-related settings on startup"""
        if not settings.mcp_api_key:
            raise ValueError("MCP_API_KEY must be set in environment variables")
        
        if len(settings.mcp_api_key) < 32:
            logger.warning("API key should be at least 32 characters long for security")
        
        logger.info("Security settings validated successfully")
    
    @staticmethod
    def get_security_headers():
        """Get recommended security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }