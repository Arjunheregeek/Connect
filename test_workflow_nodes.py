#!/usr/bin/env python3
"""
Test Workflow Nodes Directly

Test the workflow nodes individually to see what's happening.
"""

import asyncio
from agent.workflow.workflow_nodes import EnhancedWorkflowNodes
from agent.workflow.quality_assessor import WorkflowQualityAssessor
from agent.state import WorkflowStatus

async def test_workflow_nodes():
    """Test workflow nodes directly."""
    
    print("=== TESTING WORKFLOW NODES ===")
    
    # Create initial state similar to what the agent creates
    test_state = {
        'user_query': 'Find Python developers',
        'conversation_id': 'test-123',
        'workflow_status': WorkflowStatus.INITIALIZED,
        'messages': [],
        'accumulated_data': [],
        'tool_results': [],
        'errors': [],
        'retry_info': {
            'attempt_count': 1,
            'max_retries': 2,
            'previous_failures': [],
            'tools_already_tried': [],
            'strategies_tried': []
        },
        'tools_used': [],
        'retry_count': 0,
        'planning_rounds': 0,
        'synthesis_attempts': 0,
        'workflow_version': '1.0.0'
    }
    
    print(f"Initial attempt_count: {test_state['retry_info']['attempt_count']}")
    
    # Test planner
    print("\n🎯 Testing planner...")
    try:
        planned_state = await EnhancedWorkflowNodes.enhanced_planner_node(test_state)
        print(f"Planner success. Has execution_plan: {'execution_plan' in planned_state}")
        
        # Test executor
        print("\n🔧 Testing executor...")
        executed_state = await EnhancedWorkflowNodes.enhanced_executor_node(planned_state)
        print(f"Executor success. Has quality_assessment: {'quality_assessment' in executed_state}")
        
        if 'quality_assessment' in executed_state:
            qa = executed_state['quality_assessment']
            print(f"Quality assessment: {qa}")
            
            # Test quality check decision
            print(f"Current attempt_count: {executed_state['retry_info']['attempt_count']}")
            decision = EnhancedWorkflowNodes.quality_check_node(executed_state)
            print(f"Quality check decision: {decision}")
            
            # If it decides to re-plan, test the re-planner
            if decision == "re_plan":
                print("\n🔄 Testing re-planner...")
                replanned_state = await EnhancedWorkflowNodes.re_planner_node(executed_state)
                print(f"After re-planning attempt_count: {replanned_state['retry_info']['attempt_count']}")
                
                # Test quality check again
                decision2 = EnhancedWorkflowNodes.quality_check_node(replanned_state)
                print(f"Second quality check decision: {decision2}")
                
                # One more time
                if decision2 == "re_plan":
                    print("\n🔄 Testing re-planner again...")
                    replanned_state2 = await EnhancedWorkflowNodes.re_planner_node(replanned_state)
                    print(f"After second re-planning attempt_count: {replanned_state2['retry_info']['attempt_count']}")
                    
                    decision3 = EnhancedWorkflowNodes.quality_check_node(replanned_state2)
                    print(f"Third quality check decision: {decision3}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow_nodes())