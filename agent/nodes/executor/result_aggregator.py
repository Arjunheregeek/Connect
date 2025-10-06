"""
Result Aggregator Module

Aggregates and processes results from multiple tool executions.
This module focuses solely on combining and analyzing execution results.
"""

from typing import Dict, Any, List


class ResultAggregator:
    """
    Aggregates and processes results from multiple tool executions.
    
    Combines data from different tools, identifies patterns, and prepares
    comprehensive results for the Synthesizer node.
    """
    
    @classmethod
    def aggregate_results(cls, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple tool executions.
        
        Args:
            execution_results: List of execution results from ToolExecutor
            
        Returns:
            Aggregated results with combined data and insights
        """
        
        successful_results = [r for r in execution_results if r['success']]
        failed_results = [r for r in execution_results if not r['success']]
        
        # Combine all successful data
        combined_data = []
        data_sources = []
        
        for result in successful_results:
            if result.get('data'):
                combined_data.append(result['data'])
                data_sources.append(result['tool_name'])
        
        # Extract insights
        insights = cls._extract_insights(successful_results)
        
        # Calculate execution metrics
        total_time = sum(r.get('execution_time', 0) for r in execution_results)
        success_rate = len(successful_results) / len(execution_results) if execution_results else 0
        
        return {
            'combined_data': combined_data,
            'data_sources': data_sources,
            'insights': insights,
            'execution_summary': {
                'total_tools': len(execution_results),
                'successful_tools': len(successful_results),
                'failed_tools': len(failed_results),
                'success_rate': success_rate,
                'total_execution_time': total_time
            },
            'errors': [r.get('error') for r in failed_results if r.get('error')]
        }
    
    @classmethod
    def _extract_insights(cls, results: List[Dict[str, Any]]) -> List[str]:
        """Extract insights from successful tool executions."""
        insights = []
        
        # Count different types of results
        tool_types = {}
        for result in results:
            tool_name = result['tool_name']
            tool_types[tool_name] = tool_types.get(tool_name, 0) + 1
        
        # Generate insights based on tool usage
        if 'find_people_by_skill' in tool_types:
            insights.append("Skill-based search was performed to find relevant professionals")
        
        if 'find_person_by_name' in tool_types:
            insights.append("Direct person search was conducted for specific individuals")
        
        if 'natural_language_search' in tool_types:
            insights.append("Natural language processing was used for comprehensive analysis")
        
        if len(results) > 1:
            insights.append(f"Multiple search strategies were employed using {len(results)} different tools")
        
        return insights