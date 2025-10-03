# --- mcp/utils/error_handling.py ---
import logging
from typing import Dict, Any, Optional
from mcp.models.mcp_models import MCPErrorCodes

logger = logging.getLogger(__name__)

class MCPErrorHandler:
    """Centralized error handling for MCP server operations"""
    
    @staticmethod
    def log_and_format_error(
        error: Exception,
        context: str,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an error and format it for MCP response
        
        Args:
            error: The exception that occurred
            context: Context description of where the error occurred
            request_id: Optional request ID for tracking
            
        Returns:
            Formatted error dictionary
        """
        error_msg = f"{context}: {str(error)}"
        
        if request_id:
            error_msg = f"Request {request_id} - {error_msg}"
        
        logger.error(error_msg, exc_info=True)
        
        return {
            "code": MCPErrorCodes.INTERNAL_ERROR,
            "message": error_msg,
            "data": {
                "error_type": type(error).__name__,
                "context": context
            }
        }
    
    @staticmethod
    def format_validation_error(field: str, message: str) -> Dict[str, Any]:
        """Format a validation error"""
        return {
            "code": MCPErrorCodes.INVALID_PARAMS,
            "message": f"Validation error for field '{field}': {message}",
            "data": {
                "field": field,
                "validation_error": message
            }
        }
    
    @staticmethod
    def format_authentication_error(message: str = "Authentication required") -> Dict[str, Any]:
        """Format an authentication error"""
        return {
            "code": MCPErrorCodes.AUTHENTICATION_ERROR,
            "message": message,
            "data": {
                "error_type": "authentication_error"
            }
        }
    
    @staticmethod
    def format_authorization_error(message: str = "Access denied") -> Dict[str, Any]:
        """Format an authorization error"""
        return {
            "code": MCPErrorCodes.AUTHORIZATION_ERROR,
            "message": message,
            "data": {
                "error_type": "authorization_error"
            }
        }
    
    @staticmethod
    def format_tool_error(tool_name: str, error: Exception) -> Dict[str, Any]:
        """Format a tool execution error"""
        error_msg = f"Tool '{tool_name}' execution failed: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "code": MCPErrorCodes.TOOL_EXECUTION_ERROR,
            "message": error_msg,
            "data": {
                "tool_name": tool_name,
                "error_type": type(error).__name__
            }
        }
    
    @staticmethod
    def format_database_error(operation: str, error: Exception) -> Dict[str, Any]:
        """Format a database operation error"""
        error_msg = f"Database operation '{operation}' failed: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "code": MCPErrorCodes.INTERNAL_ERROR,
            "message": error_msg,
            "data": {
                "operation": operation,
                "error_type": type(error).__name__,
                "category": "database_error"
            }
        }