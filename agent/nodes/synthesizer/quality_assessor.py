"""
Quality Assessor Module

Assesses the quality and completeness of generated responses.
This module focuses solely on response quality evaluation and improvement recommendations.
"""

from typing import Dict, Any, List
from agent.state import AgentState


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