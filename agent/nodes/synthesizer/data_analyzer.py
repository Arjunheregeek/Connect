"""
Data Analyzer Module

Analyzes accumulated data from tool executions to understand patterns.
This module focuses solely on data analysis and pattern recognition.
"""

from typing import Dict, Any, List
from agent.state import AgentState


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