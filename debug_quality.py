#!/usr/bin/env python3
"""
Debug Quality Check Logic

Test script to debug the quality assessment logic.
"""

from agent.workflow.quality_assessor import WorkflowQualityAssessor

def test_quality_assessment():
    """Test the quality assessment logic with sample data."""
    
    print("=== TESTING QUALITY ASSESSMENT ===")
    
    # Test case 1: Empty results
    empty_state = {
        'accumulated_data': [],
        'tool_results': [],
        'execution_metrics': {}
    }
    
    result1 = WorkflowQualityAssessor.assess_result_quality(empty_state)
    print(f"Empty state assessment: {result1}")
    
    # Test case 2: State with data
    data_state = {
        'accumulated_data': ['some', 'data'],
        'tool_results': [
            {'result': 'tool output 1'},
            {'result': 'tool output 2'}
        ],
        'execution_metrics': {'success_rate': 1.0}
    }
    
    result2 = WorkflowQualityAssessor.assess_result_quality(data_state)
    print(f"Data state assessment: {result2}")
    
    # Test case 3: Should re-plan logic
    print("\n=== TESTING SHOULD RE-PLAN LOGIC ===")
    
    # Test with useful results
    useful_state = {
        'quality_assessment': {'is_useful': True},
        'retry_info': {'attempt_count': 1}
    }
    
    decision1 = WorkflowQualityAssessor.should_re_plan(useful_state, max_attempts=3)
    print(f"Useful results decision: {decision1}")
    
    # Test with not useful, attempt 1
    not_useful_state1 = {
        'quality_assessment': {'is_useful': False},
        'retry_info': {'attempt_count': 1}
    }
    
    decision2 = WorkflowQualityAssessor.should_re_plan(not_useful_state1, max_attempts=3)
    print(f"Not useful, attempt 1 decision: {decision2}")
    
    # Test with not useful, attempt 3 (max)
    not_useful_state3 = {
        'quality_assessment': {'is_useful': False},
        'retry_info': {'attempt_count': 3}
    }
    
    decision3 = WorkflowQualityAssessor.should_re_plan(not_useful_state3, max_attempts=3)
    print(f"Not useful, attempt 3 decision: {decision3}")
    
    # Test missing fields
    missing_state = {}
    
    decision4 = WorkflowQualityAssessor.should_re_plan(missing_state, max_attempts=3)
    print(f"Missing fields decision: {decision4}")

if __name__ == "__main__":
    test_quality_assessment()