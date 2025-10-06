"""
Plan Generator Module

Generates detailed execution plans from selected tools and analysis results.
This module focuses solely on creating structured execution plans.
"""

import uuid
from typing import Dict, Any, List
from agent.state import ExecutionPlan, PlanStep


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