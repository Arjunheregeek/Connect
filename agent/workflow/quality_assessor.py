"""
Quality Assessor for Workflow Results

Evaluates the quality and usefulness of execution results to determine
if re-planning is needed or if we can proceed to synthesis.
"""

from typing import Dict, Any, List
from agent.state import AgentState


class WorkflowQualityAssessor:
    """
    Assesses the quality and usefulness of workflow execution results.
    
    Determines if results are:
    1. Empty (no data returned)
    2. Unuseful (data returned but not relevant/useful)
    3. Useful (good data that can be synthesized)
    """
    
    @staticmethod
    def assess_result_quality(state: AgentState) -> Dict[str, Any]:
        """
        Assess the quality and usefulness of execution results.
        
        Args:
            state: Current agent state with execution results
            
        Returns:
            Quality assessment with usefulness determination and metrics
        """
        
        accumulated_data = state.get('accumulated_data', [])
        tool_results = state.get('tool_results', [])
        execution_metrics = state.get('execution_metrics', {})
        
        # Check 1: Completely empty results
        if not accumulated_data and not tool_results:
            return {
                'is_useful': False,
                'reason': 'empty_results',
                'description': 'No data returned from any tools',
                'data_count': 0,
                'useful_data_count': 0,
                'confidence': 1.0
            }
        
        # Check 2: Data returned but success rate too low
        success_rate = execution_metrics.get('success_rate', 0)
        if success_rate < 0.1:  # Less than 10% success rate
            return {
                'is_useful': False,
                'reason': 'low_success_rate',
                'description': f'Tool execution success rate too low: {success_rate:.1%}',
                'data_count': len(accumulated_data) + len(tool_results),
                'useful_data_count': 0,
                'confidence': 0.9
            }
        
        # Check 3: Count useful data items
        total_data_items = len(accumulated_data) + len(tool_results)
        useful_items = WorkflowQualityAssessor._count_useful_items(accumulated_data, tool_results)
        
        # Determine usefulness based on data quality
        if useful_items == 0:
            return {
                'is_useful': False,
                'reason': 'no_useful_data',
                'description': 'Data returned but none is useful or substantial',
                'data_count': total_data_items,
                'useful_data_count': useful_items,
                'confidence': 0.8
            }
        elif useful_items < 2 and total_data_items > 0:
            return {
                'is_useful': False,
                'reason': 'insufficient_useful_data',
                'description': f'Only {useful_items} useful items found, need more substantial results',
                'data_count': total_data_items,
                'useful_data_count': useful_items,
                'confidence': 0.7
            }
        else:
            return {
                'is_useful': True,
                'reason': 'sufficient_useful_data',
                'description': f'Found {useful_items} useful data items',
                'data_count': total_data_items,
                'useful_data_count': useful_items,
                'confidence': min(0.9, 0.5 + (useful_items * 0.1))
            }
    
    @staticmethod
    def _count_useful_items(accumulated_data: List[Any], tool_results: List[Dict]) -> int:
        """Count the number of useful data items."""
        useful_items = 0
        
        # Count useful data from accumulated_data
        for data in accumulated_data:
            if isinstance(data, (list, tuple)) and len(data) > 0:
                useful_items += len(data)
            elif isinstance(data, dict) and data:
                useful_items += 1
            elif isinstance(data, str) and len(data.strip()) > 2:  # More reasonable threshold
                useful_items += 1
        
        # Count useful data from tool_results
        for result in tool_results:
            result_data = result.get('result')
            if result_data:  # Simplified - just check if there's any result data
                if isinstance(result_data, (list, tuple)):
                    useful_items += len(result_data)
                elif isinstance(result_data, dict) and result_data:
                    useful_items += 1
                elif isinstance(result_data, str) and len(result_data.strip()) > 2:  # More reasonable threshold
                    useful_items += 1
        
        return useful_items
    
    @staticmethod
    def should_re_plan(state: AgentState, max_attempts: int = 3) -> str:
        """
        Determine the next action based on quality assessment and retry state.
        
        Args:
            state: Current agent state
            max_attempts: Maximum number of attempts allowed
            
        Returns:
            Action to take: "re_plan", "synthesize", or "end"
        """
        
        quality_assessment = state.get('quality_assessment', {})
        retry_info = state.get('retry_info', {})
        
        # If results are useful, proceed to synthesis
        if quality_assessment.get('is_useful', False):
            return "synthesize"
        
        # If we've exhausted our retries, end with error
        current_attempt = retry_info.get('attempt_count', 1)
        
        if current_attempt >= max_attempts:
            return "end"
        
        # Otherwise, try re-planning
        return "re_plan"