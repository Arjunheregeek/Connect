# --- mcp/utils/input_validation.py ---
import logging
from typing import Dict, Any, Optional
import re
from mcp.utils.error_handling import MCPErrorHandler
from mcp.schemas.tool_schemas import get_tool_by_name

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation for all 19 MCP tools"""
    
    # Match types for multiple skills
    VALID_MATCH_TYPES = {'any', 'all'}
    
    @classmethod
    def validate_tool_input(cls, tool_name: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Comprehensive validation for tool inputs
        
        Args:
            tool_name: Name of the tool being called
            input_data: Input parameters for the tool
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get tool schema
            tool = get_tool_by_name(tool_name)
            if not tool:
                return MCPErrorHandler.format_validation_error(
                    "tool_name", f"Unknown tool: {tool_name}"
                )
            
            # Validate based on specific tool
            validator_method = getattr(cls, f'_validate_{tool_name}', None)
            if validator_method:
                return validator_method(input_data)
            else:
                # Fallback to basic schema validation
                return cls._validate_basic_schema(tool, input_data)
                
        except Exception as e:
            logger.error(f"Validation error for tool {tool_name}: {str(e)}")
            return MCPErrorHandler.format_validation_error("validation", str(e))
    
    @classmethod
    def _validate_basic_schema(cls, tool: Dict[str, Any], input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Basic schema validation for required fields"""
        required_fields = tool["inputSchema"].get("required", [])
        
        for field in required_fields:
            if field not in input_data:
                return MCPErrorHandler.format_validation_error(
                    field, f"Missing required field '{field}' for tool '{tool['name']}'"
                )
        
        return None
    
    # Helper validation methods
    @classmethod
    def _validate_name_string(cls, name: Any, field_name: str = "name") -> Optional[Dict[str, Any]]:
        """Helper to validate name strings"""
        if not isinstance(name, str):
            return MCPErrorHandler.format_validation_error(field_name, f"{field_name} must be a string")
        
        if len(name.strip()) < 2:
            return MCPErrorHandler.format_validation_error(field_name, f"{field_name} must be at least 2 characters long")
        
        if len(name) > 100:
            return MCPErrorHandler.format_validation_error(field_name, f"{field_name} must be less than 100 characters")
        
        return None
    
    @classmethod
    def _validate_company_string(cls, company: Any) -> Optional[Dict[str, Any]]:
        """Helper to validate company name"""
        if not isinstance(company, str):
            return MCPErrorHandler.format_validation_error("company_name", "company_name must be a string")
        
        if len(company.strip()) < 1:
            return MCPErrorHandler.format_validation_error("company_name", "company_name cannot be empty")
        
        if len(company) > 100:
            return MCPErrorHandler.format_validation_error("company_name", "company_name must be less than 100 characters")
        
        return None
