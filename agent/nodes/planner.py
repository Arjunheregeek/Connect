"""
Planner Node Implementation

The Planner node is responsible for analyzing user queries and creating detailed
execution plans that specify which MCP tools to use and in what order.

Key Functions:
1. Query Analysis - Understanding user intent and requirements
2. Tool Selection - Choosing appropriate MCP tools from 24 available options
3. Plan Creation - Building structured execution plans with dependencies
4. Confidence Assessment - Evaluating plan quality and success probability

Workflow:
User Query → Intent Analysis → Tool Mapping → Plan Generation → Validation → AgentState
"""

import uuid
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from agent.state import AgentState, WorkflowStatus, StateManager, PlanStep, ExecutionPlan
from agent.mcp_client import MCPClient


class QueryAnalyzer:
    """
    Analyzes user queries to extract intent, entities, and requirements.
    
    This class uses pattern matching and keyword analysis to understand
    what the user is looking for and what kind of search strategy to use.
    """
    
    # Define query intent patterns
    INTENT_PATTERNS = {
        'find_person': [
            r'find.*person.*named?.*(\w+)',
            r'who is (\w+)',
            r'tell me about (\w+)',
            r'(\w+\s+\w+).*profile'
        ],
        'find_by_skill': [
            r'find.*people.*with.*skill[s]?.*(\w+)',
            r'who.*knows?.*(\w+)',
            r'experts?.*in.*(\w+)',
            r'developers?.*(\w+)',
            r'specialists?.*(\w+)'
        ],
        'find_by_company': [
            r'find.*people.*at.*(\w+)',
            r'who.*works?.*at.*(\w+)',
            r'employees?.*at.*(\w+)',
            r'(\w+).*team.*members?'
        ],
        'find_colleagues': [
            r'(\w+).*colleagues?',
            r'who.*works?.*with.*(\w+)',
            r'(\w+).*team.*mates?'
        ],
        'natural_language': [
            r'.*\?$',  # Questions ending with ?
            r'tell me.*',
            r'show me.*',
            r'i.*want.*to.*know'
        ]
    }
    
    @classmethod
    def analyze_query(cls, query: str) -> Dict[str, Any]:
        """
        Analyze user query to extract intent and entities.
        
        Args:
            query: User's input query string
            
        Returns:
            Dictionary containing:
            - intent: Primary intent category
            - entities: Extracted entities (names, skills, companies)
            - confidence: Analysis confidence (0.0-1.0)
            - keywords: Important keywords from query
        """
        query_lower = query.lower().strip()
        
        # Extract intent
        intent, entities, confidence = cls._extract_intent_and_entities(query_lower)
        
        # Extract keywords
        keywords = cls._extract_keywords(query_lower)
        
        return {
            'intent': intent,
            'entities': entities,
            'confidence': confidence,
            'keywords': keywords,
            'original_query': query
        }
    
    @classmethod
    def _extract_intent_and_entities(cls, query: str) -> Tuple[str, Dict[str, Any], float]:
        """Extract primary intent and associated entities from query."""
        
        # Check each intent pattern
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    entities = {}
                    confidence = 0.8
                    
                    # Extract entities based on intent
                    if intent == 'find_person':
                        entities['person_name'] = match.group(1)
                    elif intent == 'find_by_skill':
                        entities['skill'] = match.group(1)
                        confidence = 0.9  # High confidence for skill searches
                    elif intent == 'find_by_company':
                        entities['company'] = match.group(1)
                    elif intent == 'find_colleagues':
                        entities['person_name'] = match.group(1)
                    
                    return intent, entities, confidence
        
        # Default to natural language search
        return 'natural_language', {}, 0.6
    
    @classmethod
    def _extract_keywords(cls, query: str) -> List[str]:
        """Extract important keywords from the query."""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'find', 'who', 'what', 'where', 'when', 'why', 'how'}
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords


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


class PlanGenerator:
    """
    Generates detailed execution plans from selected tools and analysis results.
    
    Creates structured plans with step dependencies, timing estimates,
    and fallback strategies.
    """
    
    @classmethod
    def create_execution_plan(
        cls, 
        analysis: Dict[str, Any], 
        selected_tools: List[Dict[str, Any]]
    ) -> ExecutionPlan:
        """
        Create a complete execution plan from analysis and tool selection.
        
        Args:
            analysis: Query analysis results
            selected_tools: List of selected tools with configurations
            
        Returns:
            ExecutionPlan with structured steps and metadata
        """
        
        # Create plan steps
        steps = []
        for i, tool_config in enumerate(selected_tools):
            step = PlanStep(
                id=f"step-{i+1}-{tool_config['tool_name']}",
                tool_name=tool_config['tool_name'],
                arguments=tool_config['arguments'],
                rationale=f"Execute {tool_config['description']} to address user query",
                expected_output=cls._estimate_output(tool_config),
                critical=(tool_config['priority'] <= 2)  # High priority tools are critical
            )
            steps.append(step)
        
        # Estimate total execution time
        estimated_time = len(steps) * 2.0  # Rough estimate: 2 seconds per tool
        
        # Calculate confidence based on analysis and tool selection
        confidence = cls._calculate_plan_confidence(analysis, selected_tools)
        
        # Create strategy description
        strategy = cls._create_strategy_description(analysis, selected_tools)
        
        # Create fallback strategy
        fallback_strategy = "If primary tools fail, use natural_language_search as fallback"
        
        return ExecutionPlan(
            strategy=strategy,
            steps=steps,
            estimated_time=estimated_time,
            confidence=confidence,
            fallback_strategy=fallback_strategy
        )
    
    @classmethod
    def _estimate_output(cls, tool_config: Dict[str, Any]) -> str:
        """Estimate what output to expect from a tool."""
        tool_name = tool_config['tool_name']
        
        if 'find_people' in tool_name or 'find_person' in tool_name:
            return "List of people matching the search criteria with their profiles"
        elif 'get_company' in tool_name:
            return "Employee information for the specified company"
        elif 'natural_language' in tool_name:
            return "AI-generated response based on natural language understanding"
        elif 'skill' in tool_name:
            return "Skills-related information and statistics"
        else:
            return "Relevant data matching the query parameters"
    
    @classmethod
    def _calculate_plan_confidence(cls, analysis: Dict[str, Any], tools: List[Dict[str, Any]]) -> float:
        """Calculate overall plan confidence score."""
        
        # Base confidence from query analysis
        base_confidence = analysis['confidence']
        
        # Boost confidence if we have high-priority tools
        high_priority_tools = [t for t in tools if t['priority'] <= 2]
        if high_priority_tools:
            base_confidence = min(0.95, base_confidence + 0.1)
        
        # Reduce confidence if we only have natural language search
        if len(tools) == 1 and tools[0]['tool_name'] == 'natural_language_search':
            base_confidence = max(0.5, base_confidence - 0.2)
        
        return round(base_confidence, 2)
    
    @classmethod
    def _create_strategy_description(cls, analysis: Dict[str, Any], tools: List[Dict[str, Any]]) -> str:
        """Create human-readable strategy description."""
        
        intent = analysis['intent']
        tool_names = [t['tool_name'] for t in tools]
        
        if intent == 'find_person':
            return f"Direct person search using {', '.join(tool_names)}"
        elif intent == 'find_by_skill':
            return f"Skill-based search strategy using {', '.join(tool_names)}"
        elif intent == 'find_by_company':
            return f"Company-focused search using {', '.join(tool_names)}"
        elif intent == 'find_colleagues':
            return f"Colleague discovery using {', '.join(tool_names)}"
        else:
            return f"Natural language analysis using {', '.join(tool_names)}"


async def planner_node(state: AgentState) -> AgentState:
    """
    Main Planner node function for LangGraph workflow.
    
    This is the entry point for the Planner node that processes the current state,
    analyzes the user query, selects appropriate tools, and creates an execution plan.
    
    Args:
        state: Current AgentState from the workflow
        
    Returns:
        Updated AgentState with execution plan and status
    """
    
    # Update status to indicate planning has started
    updated_state = StateManager.update_status(state, WorkflowStatus.PLANNING)
    
    try:
        # Step 1: Analyze the user query
        query_analysis = QueryAnalyzer.analyze_query(state['user_query'])
        
        # Step 2: Select appropriate MCP tools
        selected_tools = ToolMapper.select_tools(query_analysis)
        
        # Step 3: Generate execution plan
        execution_plan = PlanGenerator.create_execution_plan(query_analysis, selected_tools)
        
        # Step 4: Add plan to state
        updated_state['execution_plan'] = execution_plan
        updated_state = StateManager.update_status(updated_state, WorkflowStatus.PLAN_READY)
        
        # Add debug information
        if 'debug_info' not in updated_state:
            updated_state['debug_info'] = {}
        
        updated_state['debug_info']['planner'] = {
            'query_analysis': query_analysis,
            'selected_tools': selected_tools,
            'plan_confidence': execution_plan.confidence,
            'estimated_time': execution_plan.estimated_time
        }
        
        return updated_state
        
    except Exception as e:
        # Handle planning errors
        error_state = StateManager.add_error(
            updated_state,
            'planning_error',
            f"Failed to create execution plan: {str(e)}",
            {'query': state['user_query']}
        )
        
        return StateManager.update_status(error_state, WorkflowStatus.ERROR)