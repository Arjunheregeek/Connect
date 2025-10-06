"""
Synthesizer Node Implementation

The Synthesizer node is responsible for combining results from multiple tool executions
into a coherent, comprehensive final response for the user.

Key Functions:
1. Data Analysis - Understanding and structuring collected data
2. Response Generation - Creating human-readable responses
3. Quality Assessment - Ensuring response completeness and accuracy
4. Final Output - Formatting and presenting the final answer

Workflow:
AgentState → Data Analysis → Response Generation → Quality Check → Final Response
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from agent.state import AgentState, WorkflowStatus, StateManager


class DataAnalyzer:
    """
    Analyzes accumulated data from tool executions to understand patterns,
    extract key information, and prepare for response generation.
    """
    
    @classmethod
    def analyze_accumulated_data(cls, state: AgentState) -> Dict[str, Any]:
        """
        Analyze all accumulated data from tool executions.
        
        Args:
            state: Current agent state with accumulated data
            
        Returns:
            Analysis results with structured data, patterns, and insights
        """
        
        accumulated_data = state.get('accumulated_data', [])
        tool_results = state.get('tool_results', [])
        
        if not accumulated_data and not tool_results:
            return {
                'data_available': False,
                'error': 'No data available for analysis'
            }
        
        # Combine data from different sources
        all_data = cls._combine_data_sources(accumulated_data, tool_results)
        
        # Extract different types of information
        people_data = cls._extract_people_data(all_data)
        skills_data = cls._extract_skills_data(all_data)
        companies_data = cls._extract_companies_data(all_data)
        insights_data = cls._extract_insights_data(all_data)
        
        # Calculate data statistics
        stats = cls._calculate_data_statistics(all_data)
        
        return {
            'data_available': True,
            'people': people_data,
            'skills': skills_data,
            'companies': companies_data,
            'insights': insights_data,
            'statistics': stats,
            'raw_data_count': len(all_data),
            'data_quality_score': cls._assess_data_quality(all_data)
        }
    
    @classmethod
    def _combine_data_sources(cls, accumulated_data: List[Any], tool_results: List[Dict]) -> List[Any]:
        """Combine data from accumulated_data and tool_results."""
        all_data = []
        
        # Add accumulated data
        for data in accumulated_data:
            if isinstance(data, (list, tuple)):
                all_data.extend(data)
            else:
                all_data.append(data)
        
        # Add data from tool results
        for result in tool_results:
            if 'result' in result and result['result']:
                data = result['result']
                if isinstance(data, (list, tuple)):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        
        return all_data
    
    @classmethod
    def _extract_people_data(cls, all_data: List[Any]) -> List[Dict[str, Any]]:
        """Extract and structure people-related data."""
        people = []
        
        for item in all_data:
            if isinstance(item, dict):
                # Check if this looks like person data
                if any(key in item for key in ['name', 'Name', 'person_name', 'full_name']):
                    person_info = {
                        'name': item.get('name') or item.get('Name') or item.get('person_name') or item.get('full_name'),
                        'skills': item.get('skills', []),
                        'company': item.get('company') or item.get('Company'),
                        'title': item.get('title') or item.get('job_title'),
                        'location': item.get('location'),
                        'experience': item.get('experience'),
                        'education': item.get('education'),
                        'raw_data': item
                    }
                    people.append(person_info)
            elif isinstance(item, str):
                # Handle string responses that might contain person info
                if 'name' in item.lower() or 'person' in item.lower():
                    people.append({
                        'name': 'Unknown',
                        'description': item,
                        'raw_data': item
                    })
        
        return people
    
    @classmethod
    def _extract_skills_data(cls, all_data: List[Any]) -> List[str]:
        """Extract skills mentioned in the data."""
        skills = set()
        
        for item in all_data:
            if isinstance(item, dict):
                # Extract from skills field
                if 'skills' in item and isinstance(item['skills'], list):
                    skills.update(item['skills'])
                
                # Extract from text fields
                for key in ['description', 'bio', 'summary']:
                    if key in item and isinstance(item[key], str):
                        # Simple skill extraction (could be enhanced with NLP)
                        text = item[key].lower()
                        common_skills = ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes', 'machine learning', 'ai', 'data science']
                        for skill in common_skills:
                            if skill in text:
                                skills.add(skill)
        
        return list(skills)
    
    @classmethod
    def _extract_companies_data(cls, all_data: List[Any]) -> List[str]:
        """Extract company information from the data."""
        companies = set()
        
        for item in all_data:
            if isinstance(item, dict):
                company_fields = ['company', 'Company', 'employer', 'organization']
                for field in company_fields:
                    if field in item and item[field]:
                        companies.add(item[field])
        
        return list(companies)
    
    @classmethod
    def _extract_insights_data(cls, all_data: List[Any]) -> List[str]:
        """Extract insights and patterns from the data."""
        insights = []
        
        # Count different data types
        person_count = len([item for item in all_data if isinstance(item, dict) and any(key in item for key in ['name', 'Name'])])
        
        if person_count > 0:
            insights.append(f"Found {person_count} people in the search results")
        
        # Check for skill diversity
        skills = cls._extract_skills_data(all_data)
        if len(skills) > 5:
            insights.append(f"Diverse skill set identified with {len(skills)} different technologies/skills")
        
        # Check for company diversity
        companies = cls._extract_companies_data(all_data)
        if len(companies) > 3:
            insights.append(f"Results span across {len(companies)} different organizations")
        
        return insights
    
    @classmethod
    def _calculate_data_statistics(cls, all_data: List[Any]) -> Dict[str, Any]:
        """Calculate statistical information about the data."""
        return {
            'total_items': len(all_data),
            'dict_items': len([item for item in all_data if isinstance(item, dict)]),
            'string_items': len([item for item in all_data if isinstance(item, str)]),
            'list_items': len([item for item in all_data if isinstance(item, list)])
        }
    
    @classmethod
    def _assess_data_quality(cls, all_data: List[Any]) -> float:
        """Assess the quality of the collected data (0.0-1.0)."""
        if not all_data:
            return 0.0
        
        quality_score = 0.5  # Base score
        
        # Boost score for structured data
        structured_items = len([item for item in all_data if isinstance(item, dict)])
        if structured_items > 0:
            quality_score += 0.3 * min(1.0, structured_items / len(all_data))
        
        # Boost score for diverse data
        if len(all_data) > 5:
            quality_score += 0.2
        
        return min(1.0, quality_score)


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


class QualityAssessor:
    """
    Assesses the quality and completeness of generated responses.
    
    Evaluates responses against various criteria to ensure they meet
    quality standards and provide value to the user.
    """
    
    @classmethod
    def assess_response_quality(cls, response: str, state: AgentState, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of the generated response.
        
        Args:
            response: Generated response string
            state: Current agent state
            analysis: Data analysis results
            
        Returns:
            Quality assessment with scores and recommendations
        """
        
        assessment = {
            'overall_score': 0.0,
            'completeness_score': 0.0,
            'relevance_score': 0.0,
            'clarity_score': 0.0,
            'data_utilization_score': 0.0,
            'recommendations': []
        }
        
        # Assess completeness
        assessment['completeness_score'] = cls._assess_completeness(response, state, analysis)
        
        # Assess relevance
        assessment['relevance_score'] = cls._assess_relevance(response, state)
        
        # Assess clarity
        assessment['clarity_score'] = cls._assess_clarity(response)
        
        # Assess data utilization
        assessment['data_utilization_score'] = cls._assess_data_utilization(response, analysis)
        
        # Calculate overall score
        assessment['overall_score'] = (
            assessment['completeness_score'] * 0.3 +
            assessment['relevance_score'] * 0.3 +
            assessment['clarity_score'] * 0.2 +
            assessment['data_utilization_score'] * 0.2
        )
        
        # Generate recommendations
        assessment['recommendations'] = cls._generate_recommendations(assessment, response)
        
        return assessment
    
    @classmethod
    def _assess_completeness(cls, response: str, state: AgentState, analysis: Dict[str, Any]) -> float:
        """Assess how complete the response is."""
        score = 0.5  # Base score
        
        # Check if response addresses the query
        if state['user_query'].lower() in response.lower():
            score += 0.2
        
        # Check if response has substantial content
        if len(response) > 100:
            score += 0.2
        
        # Check if response utilizes available data
        if analysis.get('data_available', False) and len(analysis.get('people', [])) > 0:
            if any(person.get('name', '') in response for person in analysis['people'][:5]):
                score += 0.1
        
        return min(1.0, score)
    
    @classmethod
    def _assess_relevance(cls, response: str, state: AgentState) -> float:
        """Assess how relevant the response is to the user query."""
        query_words = state['user_query'].lower().split()
        response_lower = response.lower()
        
        # Count how many query words appear in response
        matches = sum(1 for word in query_words if word in response_lower)
        relevance_ratio = matches / len(query_words) if query_words else 0
        
        return min(1.0, relevance_ratio * 1.2)  # Boost good matches
    
    @classmethod
    def _assess_clarity(cls, response: str) -> float:
        """Assess how clear and well-structured the response is."""
        score = 0.5  # Base score
        
        # Check for structure indicators
        if '**' in response or '•' in response or '\n' in response:
            score += 0.2  # Has formatting
        
        # Check length appropriateness
        if 50 <= len(response) <= 2000:
            score += 0.2  # Appropriate length
        
        # Check for complete sentences
        if response.endswith('.') or response.endswith('!') or response.endswith('?'):
            score += 0.1  # Proper ending
        
        return min(1.0, score)
    
    @classmethod
    def _assess_data_utilization(cls, response: str, analysis: Dict[str, Any]) -> float:
        """Assess how well the response utilizes available data."""
        if not analysis.get('data_available', False):
            return 1.0  # Can't utilize data that doesn't exist
        
        score = 0.0
        
        # Check if people data is used
        people = analysis.get('people', [])
        if people:
            people_mentioned = sum(1 for person in people[:10] if person.get('name', '') in response)
            score += 0.4 * min(1.0, people_mentioned / min(len(people), 5))
        
        # Check if insights are used
        insights = analysis.get('insights', [])
        if insights:
            insights_used = sum(1 for insight in insights if any(word in response.lower() for word in insight.lower().split()[:3]))
            score += 0.3 * min(1.0, insights_used / len(insights))
        
        # Check if statistics are mentioned
        stats = analysis.get('statistics', {})
        if stats.get('total_items', 0) > 0:
            if str(stats['total_items']) in response or 'found' in response.lower():
                score += 0.3
        
        return min(1.0, score)
    
    @classmethod
    def _generate_recommendations(cls, assessment: Dict[str, Any], response: str) -> List[str]:
        """Generate recommendations for improving response quality."""
        recommendations = []
        
        if assessment['completeness_score'] < 0.7:
            recommendations.append("Consider including more comprehensive information to better address the user's query")
        
        if assessment['relevance_score'] < 0.7:
            recommendations.append("Ensure the response more directly addresses the specific terms and intent in the user's query")
        
        if assessment['clarity_score'] < 0.7:
            recommendations.append("Improve response structure and formatting for better readability")
        
        if assessment['data_utilization_score'] < 0.7:
            recommendations.append("Better utilize the available data by including more specific details and insights")
        
        if len(response) < 50:
            recommendations.append("Response may be too brief - consider expanding with more details")
        
        if len(response) > 2000:
            recommendations.append("Response may be too verbose - consider summarizing key points")
        
        return recommendations


async def synthesizer_node(state: AgentState) -> AgentState:
    """
    Main Synthesizer node function for LangGraph workflow.
    
    This is the entry point for the Synthesizer node that processes tool execution results,
    analyzes the collected data, and generates a comprehensive final response.
    
    Args:
        state: Current AgentState with tool execution results
        
    Returns:
        Updated AgentState with final response and completion status
    """
    
    # Update status to indicate synthesis has started
    updated_state = StateManager.update_status(state, WorkflowStatus.SYNTHESIZING)
    
    try:
        # Step 1: Analyze accumulated data
        analysis = DataAnalyzer.analyze_accumulated_data(state)
        
        # Step 2: Generate response
        response = ResponseGenerator.generate_response(state, analysis)
        
        # Step 3: Assess response quality
        quality_assessment = QualityAssessor.assess_response_quality(response, state, analysis)
        
        # Step 4: Update state with final response
        updated_state['final_response'] = response
        updated_state['response_metadata'] = {
            'analysis_summary': {
                'data_available': analysis.get('data_available', False),
                'people_found': len(analysis.get('people', [])),
                'skills_identified': len(analysis.get('skills', [])),
                'companies_found': len(analysis.get('companies', [])),
                'data_quality_score': analysis.get('data_quality_score', 0.0)
            },
            'quality_assessment': quality_assessment,
            'synthesis_timestamp': datetime.now(),
            'response_length': len(response),
            'response_type': 'comprehensive' if len(response) > 200 else 'concise'
        }
        
        # Add synthesis debug info
        if 'debug_info' not in updated_state:
            updated_state['debug_info'] = {}
        
        updated_state['debug_info']['synthesizer'] = {
            'analysis_results': analysis,
            'quality_scores': {
                'overall': quality_assessment['overall_score'],
                'completeness': quality_assessment['completeness_score'],
                'relevance': quality_assessment['relevance_score'],
                'clarity': quality_assessment['clarity_score']
            },
            'recommendations': quality_assessment['recommendations']
        }
        
        # Update status to completed
        updated_state = StateManager.update_status(updated_state, WorkflowStatus.COMPLETED)
        
        return updated_state
        
    except Exception as e:
        # Handle synthesis errors
        error_state = StateManager.add_error(
            updated_state,
            'synthesis_error',
            f"Failed to synthesize final response: {str(e)}",
            {'query': state['user_query']}
        )
        
        # Generate fallback response
        fallback_response = f"I encountered an issue while preparing your response for the query: '{state['user_query']}'. However, I was able to gather some information during the search process. Please check the intermediate results or try rephrasing your question."
        
        error_state['final_response'] = fallback_response
        error_state['response_metadata'] = {
            'response_type': 'fallback',
            'synthesis_timestamp': datetime.now(),
            'error_recovery': True
        }
        
        return StateManager.update_status(error_state, WorkflowStatus.ERROR)