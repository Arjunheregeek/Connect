"""
Response Generator Module

Generates human-readable responses from analyzed data.
This module focuses solely on creating comprehensive user responses.
"""

from typing import Dict, Any
from agent.state import AgentState


class ResponseGenerator:
    """
    Generates human-readable responses from analyzed data.
    
    Creates comprehensive, well-structured responses that address the user's
    original query using the collected and analyzed data.
    """
    
    @classmethod
    def generate_response(cls, state: AgentState, analysis: Dict[str, Any]) -> str:
        """
        Generate a comprehensive response based on data analysis.
        
        Args:
            state: Current agent state
            analysis: Data analysis results
            
        Returns:
            Human-readable response string
        """
        
        if not analysis.get('data_available', False):
            return cls._generate_no_data_response(state)
        
        # Determine response type based on original query and available data
        query = state['user_query'].lower()
        
        if cls._is_person_search_query(query):
            return cls._generate_person_search_response(state, analysis)
        elif cls._is_skill_search_query(query):
            return cls._generate_skill_search_response(state, analysis)
        elif cls._is_company_search_query(query):
            return cls._generate_company_search_response(state, analysis)
        else:
            return cls._generate_general_response(state, analysis)
    
    @classmethod
    def _is_person_search_query(cls, query: str) -> bool:
        """Check if query is asking for specific person information."""
        person_indicators = ['who is', 'find person', 'tell me about', 'profile of']
        return any(indicator in query for indicator in person_indicators)
    
    @classmethod
    def _is_skill_search_query(cls, query: str) -> bool:
        """Check if query is asking for skill-based search."""
        skill_indicators = ['skill', 'expert', 'developer', 'engineer', 'specialist', 'knows']
        return any(indicator in query for indicator in skill_indicators)
    
    @classmethod
    def _is_company_search_query(cls, query: str) -> bool:
        """Check if query is asking for company-related information."""
        company_indicators = ['company', 'works at', 'employees', 'team', 'organization']
        return any(indicator in query for indicator in company_indicators)
    
    @classmethod
    def _generate_person_search_response(cls, state: AgentState, analysis: Dict[str, Any]) -> str:
        """Generate response for person-specific queries."""
        people = analysis.get('people', [])
        
        if not people:
            return f"I couldn't find specific information about the person you're looking for in the query: '{state['user_query']}'. The search didn't return any matching profiles."
        
        response_parts = []
        response_parts.append(f"Here's what I found regarding your query: '{state['user_query']}':\n")
        
        for i, person in enumerate(people[:5], 1):  # Limit to top 5 results
            name = person.get('name', 'Unknown')
            company = person.get('company', 'Unknown company')
            title = person.get('title', 'Unknown position')
            skills = person.get('skills', [])
            
            person_info = f"{i}. **{name}**"
            if title != 'Unknown position':
                person_info += f" - {title}"
            if company != 'Unknown company':
                person_info += f" at {company}"
            
            if skills:
                person_info += f"\n   Skills: {', '.join(skills[:5])}"  # Show top 5 skills
            
            response_parts.append(person_info)
        
        if len(people) > 5:
            response_parts.append(f"\n... and {len(people) - 5} more results found.")
        
        return '\n\n'.join(response_parts)
    
    @classmethod
    def _generate_skill_search_response(cls, state: AgentState, analysis: Dict[str, Any]) -> str:
        """Generate response for skill-based queries."""
        people = analysis.get('people', [])
        skills = analysis.get('skills', [])
        
        response_parts = []
        response_parts.append(f"Here are the results for your skill-based query: '{state['user_query']}':\n")
        
        if people:
            response_parts.append(f"**Found {len(people)} professionals:**")
            
            for i, person in enumerate(people[:7], 1):  # Show more for skill searches
                name = person.get('name', 'Unknown')
                company = person.get('company', '')
                title = person.get('title', '')
                
                person_line = f"{i}. {name}"
                if title:
                    person_line += f" ({title})"
                if company:
                    person_line += f" at {company}"
                
                response_parts.append(person_line)
            
            if len(people) > 7:
                response_parts.append(f"... and {len(people) - 7} more professionals found.")
        
        if skills:
            response_parts.append(f"\n**Related skills identified:** {', '.join(skills[:10])}")
        
        # Add insights if available
        insights = analysis.get('insights', [])
        if insights:
            response_parts.append(f"\n**Key insights:**")
            for insight in insights:
                response_parts.append(f"• {insight}")
        
        return '\n'.join(response_parts)
    
    @classmethod
    def _generate_company_search_response(cls, state: AgentState, analysis: Dict[str, Any]) -> str:
        """Generate response for company-related queries."""
        people = analysis.get('people', [])
        companies = analysis.get('companies', [])
        
        response_parts = []
        response_parts.append(f"Here's what I found for your company-related query: '{state['user_query']}':\n")
        
        if companies:
            response_parts.append(f"**Organizations found:** {', '.join(companies)}")
        
        if people:
            response_parts.append(f"\n**{len(people)} professionals found:**")
            
            # Group by company if possible
            company_groups = {}
            for person in people:
                company = person.get('company', 'Other')
                if company not in company_groups:
                    company_groups[company] = []
                company_groups[company].append(person)
            
            for company, company_people in company_groups.items():
                if company != 'Other':
                    response_parts.append(f"\n**At {company}:**")
                    for person in company_people[:5]:
                        name = person.get('name', 'Unknown')
                        title = person.get('title', '')
                        person_line = f"• {name}"
                        if title:
                            person_line += f" - {title}"
                        response_parts.append(person_line)
        
        return '\n'.join(response_parts)
    
    @classmethod
    def _generate_general_response(cls, state: AgentState, analysis: Dict[str, Any]) -> str:
        """Generate general response for other types of queries."""
        people = analysis.get('people', [])
        stats = analysis.get('statistics', {})
        insights = analysis.get('insights', [])
        
        response_parts = []
        response_parts.append(f"Based on your query '{state['user_query']}', here's what I found:\n")
        
        if people:
            response_parts.append(f"**Found {len(people)} relevant results:**")
            
            for i, person in enumerate(people[:5], 1):
                name = person.get('name', 'Unknown')
                description = person.get('description', '')
                
                if description:
                    response_parts.append(f"{i}. {name}: {description}")
                else:
                    company = person.get('company', '')
                    title = person.get('title', '')
                    person_line = f"{i}. {name}"
                    if title:
                        person_line += f" - {title}"
                    if company:
                        person_line += f" at {company}"
                    response_parts.append(person_line)
        
        if insights:
            response_parts.append(f"\n**Key insights:**")
            for insight in insights:
                response_parts.append(f"• {insight}")
        
        # Add execution summary if available
        execution_metrics = state.get('execution_metrics', {})
        if execution_metrics.get('total_tools', 0) > 0:
            response_parts.append(f"\n*Search completed using {execution_metrics['total_tools']} different tools in {execution_metrics.get('total_execution_time', 0):.1f} seconds.*")
        
        return '\n'.join(response_parts)
    
    @classmethod
    def _generate_no_data_response(cls, state: AgentState) -> str:
        """Generate response when no data is available."""
        return f"I apologize, but I couldn't find any relevant information for your query: '{state['user_query']}'. This could be due to:\n\n• No matching results in the database\n• Technical issues with the search tools\n• The query might need to be more specific\n\nPlease try rephrasing your question or providing more specific details."