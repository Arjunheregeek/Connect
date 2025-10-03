# --- mcp/utils/input_validation.py ---
import logging
from typing import Dict, Any, List, Optional, Union
import re
from mcp.utils.error_handling import MCPErrorHandler
from mcp.schemas.tool_schemas import get_tool_by_name

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation for all MCP tools"""
    
    # Common validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    NAME_PATTERN = re.compile(r'^[a-zA-Z\s\-\.\']{1,100}$')
    COMPANY_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\.&,()]{1,100}$')
    SKILL_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\.+#]{1,50}$')
    LOCATION_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\.,()]{1,100}$')
    
    # Experience level mappings
    VALID_EXPERIENCE_LEVELS = {
        'entry', 'junior', 'mid', 'senior', 'lead', 'principal', 'director', 'vp', 'c-level',
        'intern', 'associate', 'manager', 'engineer', 'scientist', 'analyst', 'consultant'
    }
    
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
    
    @classmethod
    def _validate_find_person_by_name(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_person_by_name input"""
        if "name" not in input_data:
            return MCPErrorHandler.format_validation_error("name", "Missing required field 'name'")
        
        name = input_data["name"]
        if not isinstance(name, str):
            return MCPErrorHandler.format_validation_error("name", "Name must be a string")
        
        if len(name.strip()) < 2:
            return MCPErrorHandler.format_validation_error("name", "Name must be at least 2 characters long")
        
        if len(name) > 100:
            return MCPErrorHandler.format_validation_error("name", "Name must be less than 100 characters")
        
        # Allow flexible name patterns for international names
        if not re.match(r'^[a-zA-Z\s\-\.\'\u00C0-\u017F\u0100-\u024F]{2,100}$', name):
            return MCPErrorHandler.format_validation_error("name", "Name contains invalid characters")
        
        return None
    
    @classmethod
    def _validate_find_people_by_skill(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_by_skill input"""
        if "skill" not in input_data:
            return MCPErrorHandler.format_validation_error("skill", "Missing required field 'skill'")
        
        skill = input_data["skill"]
        if not isinstance(skill, str):
            return MCPErrorHandler.format_validation_error("skill", "Skill must be a string")
        
        if len(skill.strip()) < 1:
            return MCPErrorHandler.format_validation_error("skill", "Skill cannot be empty")
        
        if len(skill) > 50:
            return MCPErrorHandler.format_validation_error("skill", "Skill must be less than 50 characters")
        
        return None
    
    @classmethod
    def _validate_find_people_by_company(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_by_company input"""
        if "company" not in input_data:
            return MCPErrorHandler.format_validation_error("company", "Missing required field 'company'")
        
        company = input_data["company"]
        if not isinstance(company, str):
            return MCPErrorHandler.format_validation_error("company", "Company must be a string")
        
        if len(company.strip()) < 1:
            return MCPErrorHandler.format_validation_error("company", "Company cannot be empty")
        
        if len(company) > 100:
            return MCPErrorHandler.format_validation_error("company", "Company name must be less than 100 characters")
        
        return None
    
    @classmethod
    def _validate_find_colleagues_at_company(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_colleagues_at_company input"""
        # Validate person_name
        if "person_name" not in input_data:
            return MCPErrorHandler.format_validation_error("person_name", "Missing required field 'person_name'")
        
        error = cls._validate_person_name(input_data["person_name"])
        if error:
            return error
        
        # Validate company_name
        if "company_name" not in input_data:
            return MCPErrorHandler.format_validation_error("company_name", "Missing required field 'company_name'")
        
        return cls._validate_company_name(input_data["company_name"])
    
    @classmethod
    def _validate_find_people_by_institution(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_by_institution input"""
        if "institution_name" not in input_data:
            return MCPErrorHandler.format_validation_error("institution_name", "Missing required field 'institution_name'")
        
        institution = input_data["institution_name"]
        if not isinstance(institution, str):
            return MCPErrorHandler.format_validation_error("institution_name", "Institution name must be a string")
        
        if len(institution.strip()) < 1:
            return MCPErrorHandler.format_validation_error("institution_name", "Institution name cannot be empty")
        
        if len(institution) > 100:
            return MCPErrorHandler.format_validation_error("institution_name", "Institution name must be less than 100 characters")
        
        return None
    
    @classmethod
    def _validate_find_people_by_location(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_by_location input"""
        if "location" not in input_data:
            return MCPErrorHandler.format_validation_error("location", "Missing required field 'location'")
        
        location = input_data["location"]
        if not isinstance(location, str):
            return MCPErrorHandler.format_validation_error("location", "Location must be a string")
        
        if len(location.strip()) < 1:
            return MCPErrorHandler.format_validation_error("location", "Location cannot be empty")
        
        if len(location) > 100:
            return MCPErrorHandler.format_validation_error("location", "Location must be less than 100 characters")
        
        return None
    
    @classmethod
    def _validate_get_person_skills(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate get_person_skills input"""
        if "person_name" not in input_data:
            return MCPErrorHandler.format_validation_error("person_name", "Missing required field 'person_name'")
        
        return cls._validate_person_name(input_data["person_name"])
    
    @classmethod
    def _validate_find_people_with_multiple_skills(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_with_multiple_skills input"""
        if "skills_list" not in input_data:
            return MCPErrorHandler.format_validation_error("skills_list", "Missing required field 'skills_list'")
        
        skills_list = input_data["skills_list"]
        if not isinstance(skills_list, list):
            return MCPErrorHandler.format_validation_error("skills_list", "Skills list must be an array")
        
        if len(skills_list) < 1:
            return MCPErrorHandler.format_validation_error("skills_list", "Skills list cannot be empty")
        
        if len(skills_list) > 10:
            return MCPErrorHandler.format_validation_error("skills_list", "Skills list cannot have more than 10 skills")
        
        # Validate each skill
        for i, skill in enumerate(skills_list):
            if not isinstance(skill, str):
                return MCPErrorHandler.format_validation_error(f"skills_list[{i}]", "Each skill must be a string")
            
            if len(skill.strip()) < 1:
                return MCPErrorHandler.format_validation_error(f"skills_list[{i}]", "Skill cannot be empty")
            
            if len(skill) > 50:
                return MCPErrorHandler.format_validation_error(f"skills_list[{i}]", "Skill must be less than 50 characters")
        
        # Validate match_type if provided
        if "match_type" in input_data:
            match_type = input_data["match_type"]
            if match_type not in cls.VALID_MATCH_TYPES:
                return MCPErrorHandler.format_validation_error("match_type", f"Match type must be one of: {', '.join(cls.VALID_MATCH_TYPES)}")
        
        return None
    
    @classmethod
    def _validate_get_person_colleagues(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate get_person_colleagues input"""
        if "person_name" not in input_data:
            return MCPErrorHandler.format_validation_error("person_name", "Missing required field 'person_name'")
        
        return cls._validate_person_name(input_data["person_name"])
    
    @classmethod
    def _validate_find_people_by_experience_level(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate find_people_by_experience_level input"""
        if "experience_level" not in input_data:
            return MCPErrorHandler.format_validation_error("experience_level", "Missing required field 'experience_level'")
        
        experience_level = input_data["experience_level"].lower()
        if experience_level not in cls.VALID_EXPERIENCE_LEVELS:
            return MCPErrorHandler.format_validation_error(
                "experience_level", 
                f"Experience level must be one of: {', '.join(sorted(cls.VALID_EXPERIENCE_LEVELS))}"
            )
        
        return None
    
    @classmethod
    def _validate_get_company_employees(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate get_company_employees input"""
        if "company_name" not in input_data:
            return MCPErrorHandler.format_validation_error("company_name", "Missing required field 'company_name'")
        
        return cls._validate_company_name(input_data["company_name"])
    
    @classmethod
    def _validate_get_skill_popularity(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate get_skill_popularity input"""
        # Validate limit if provided
        if "limit" in input_data:
            limit = input_data["limit"]
            if not isinstance(limit, int):
                return MCPErrorHandler.format_validation_error("limit", "Limit must be an integer")
            
            if limit < 1:
                return MCPErrorHandler.format_validation_error("limit", "Limit must be at least 1")
            
            if limit > 100:
                return MCPErrorHandler.format_validation_error("limit", "Limit cannot exceed 100")
        
        return None
    
    @classmethod
    def _validate_get_person_details(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate get_person_details input"""
        if "person_name" not in input_data:
            return MCPErrorHandler.format_validation_error("person_name", "Missing required field 'person_name'")
        
        return cls._validate_person_name(input_data["person_name"])
    
    @classmethod
    def _validate_natural_language_search(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate natural_language_search input"""
        if "question" not in input_data:
            return MCPErrorHandler.format_validation_error("question", "Missing required field 'question'")
        
        question = input_data["question"]
        if not isinstance(question, str):
            return MCPErrorHandler.format_validation_error("question", "Question must be a string")
        
        if len(question.strip()) < 3:
            return MCPErrorHandler.format_validation_error("question", "Question must be at least 3 characters long")
        
        if len(question) > 500:
            return MCPErrorHandler.format_validation_error("question", "Question must be less than 500 characters")
        
        return None
    
    @classmethod
    def _validate_health_check(cls, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate health_check input (no parameters required)"""
        return None
    
    # Helper validation methods
    @classmethod
    def _validate_person_name(cls, name: Any) -> Optional[Dict[str, Any]]:
        """Helper to validate person name"""
        if not isinstance(name, str):
            return MCPErrorHandler.format_validation_error("person_name", "Person name must be a string")
        
        if len(name.strip()) < 2:
            return MCPErrorHandler.format_validation_error("person_name", "Person name must be at least 2 characters long")
        
        if len(name) > 100:
            return MCPErrorHandler.format_validation_error("person_name", "Person name must be less than 100 characters")
        
        return None
    
    @classmethod
    def _validate_company_name(cls, company: Any) -> Optional[Dict[str, Any]]:
        """Helper to validate company name"""
        if not isinstance(company, str):
            return MCPErrorHandler.format_validation_error("company_name", "Company name must be a string")
        
        if len(company.strip()) < 1:
            return MCPErrorHandler.format_validation_error("company_name", "Company name cannot be empty")
        
        if len(company) > 100:
            return MCPErrorHandler.format_validation_error("company_name", "Company name must be less than 100 characters")
        
        return None