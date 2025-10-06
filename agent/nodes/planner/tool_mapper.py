"""
Tool Mapper Module

Maps user intents to appropriate MCP tools and creates execution strategies.
This module focuses solely on selecting the right tools for the job.
"""

from typing import Dict, Any, List


class ToolMapper:
    """
    Maps user intents to appropriate MCP tools and creates execution strategies.
    
    This class knows about all 24 MCP tools and can select the best combination
    of tools to fulfill a user's request.
    """
    
    # Tool capability mapping
    TOOL_CAPABILITIES = {
        # Direct person search tools
        'find_person_by_name': {
            'intents': ['find_person'],
            'entities_required': ['person_name'],
            'description': 'Find specific person by name',
            'priority': 1
        },
        
        # Skill-based search tools
        'find_people_by_skill': {
            'intents': ['find_by_skill'],
            'entities_required': ['skill'],
            'description': 'Find people with specific skills',
            'priority': 1
        },
        'find_people_with_multiple_skills': {
            'intents': ['find_by_skill'],
            'entities_optional': ['skills'],
            'description': 'Find people with multiple skills',
            'priority': 2
        },
        'find_domain_experts': {
            'intents': ['find_by_skill'],
            'entities_optional': ['domains'],
            'description': 'Find domain experts',
            'priority': 2
        },
        
        # Company-based search tools
        'find_people_by_company': {
            'intents': ['find_by_company'],
            'entities_required': ['company'],
            'description': 'Find people by company',
            'priority': 1
        },
        'get_company_employees': {
            'intents': ['find_by_company'],
            'entities_required': ['company'],
            'description': 'Get all company employees',
            'priority': 2
        },
        'find_colleagues_at_company': {
            'intents': ['find_colleagues'],
            'entities_required': ['person_name', 'company'],
            'description': 'Find colleagues at specific company',
            'priority': 1
        },
        
        # Natural language search
        'natural_language_search': {
            'intents': ['natural_language', 'find_person', 'find_by_skill', 'find_by_company'],
            'entities_optional': [],
            'description': 'Natural language search across all data',
            'priority': 3  # Fallback option
        },
        
        # Enhanced search and analysis tools
        'get_skill_popularity': {
            'intents': ['find_by_skill'],
            'entities_optional': [],
            'description': 'Get popular skills for context',
            'priority': 3
        },
        'find_people_by_experience_level': {
            'intents': ['find_by_skill'],
            'entities_optional': ['experience_level'],
            'description': 'Find people by experience level',
            'priority': 2
        }
    }
    
    @classmethod
    def select_tools(cls, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate MCP tools based on query analysis.
        
        Args:
            analysis: Query analysis results from QueryAnalyzer
            
        Returns:
            List of selected tools with their configurations
        """
        intent = analysis['intent']
        entities = analysis['entities']
        
        selected_tools = []
        
        # Find matching tools for the intent
        for tool_name, tool_info in cls.TOOL_CAPABILITIES.items():
            if intent in tool_info['intents']:
                # Check if required entities are available
                required_entities = tool_info.get('entities_required', [])
                if all(entity in entities for entity in required_entities):
                    tool_config = {
                        'tool_name': tool_name,
                        'priority': tool_info['priority'],
                        'description': tool_info['description'],
                        'arguments': cls._build_arguments(tool_name, entities, analysis)
                    }
                    selected_tools.append(tool_config)
        
        # Sort by priority (lower number = higher priority)
        selected_tools.sort(key=lambda x: x['priority'])
        
        # Ensure we have at least one tool (fallback to natural language search)
        if not selected_tools:
            selected_tools.append({
                'tool_name': 'natural_language_search',
                'priority': 3,
                'description': 'Fallback natural language search',
                'arguments': {'question': analysis['original_query']}
            })
        
        return selected_tools
    
    @classmethod
    def _build_arguments(cls, tool_name: str, entities: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build tool arguments based on extracted entities and analysis."""
        
        # Argument mapping for each tool
        if tool_name == 'find_person_by_name':
            return {'name': entities.get('person_name', '')}
        
        elif tool_name == 'find_people_by_skill':
            return {'skill': entities.get('skill', '')}
        
        elif tool_name == 'find_people_by_company':
            return {'company_name': entities.get('company', '')}
        
        elif tool_name == 'find_colleagues_at_company':
            return {
                'person_name': entities.get('person_name', ''),
                'company_name': entities.get('company', '')
            }
        
        elif tool_name == 'natural_language_search':
            return {'question': analysis['original_query']}
        
        elif tool_name == 'get_skill_popularity':
            return {'limit': 10}
        
        elif tool_name == 'find_people_with_multiple_skills':
            # Try to extract multiple skills from keywords
            skills = [kw for kw in analysis['keywords'] if len(kw) > 3][:3]
            return {'skills': skills} if skills else {'skills': [entities.get('skill', '')]}
        
        # Default arguments
        return {}