"""
Retry Manager for Workflow

Manages retry logic, failure tracking, and provides feedback to the planner
for intelligent re-planning based on previous failures.
"""

from typing import Dict, Any, List
from datetime import datetime
from agent.state import AgentState


class RetryManager:
    """
    Manages retry attempts and tracks failure history for intelligent re-planning.
    """
    
    @staticmethod
    def initialize_retry_info(state: AgentState, max_attempts: int = 3) -> AgentState:
        """
        Initialize retry tracking information in the state.
        
        Args:
            state: Current agent state
            max_attempts: Maximum number of attempts allowed
            
        Returns:
            Updated state with retry information
        """
        
        if 'retry_info' not in state:
            state['retry_info'] = {
                'attempt_count': 1,
                'max_attempts': max_attempts,
                'previous_failures': [],
                'tools_already_tried': [],
                'strategies_tried': []
            }
        
        return state
    
    @staticmethod
    def create_planning_context(state: AgentState) -> Dict[str, Any]:
        """
        Create planning context based on retry history for smarter re-planning.
        
        Args:
            state: Current agent state with retry information
            
        Returns:
            Planning context for the planner to use
        """
        
        retry_info = state.get('retry_info', {})
        previous_failures = retry_info.get('previous_failures', [])
        
        if previous_failures:
            return {
                'is_retry': True,
                'attempt_number': retry_info.get('attempt_count', 1),
                'previous_failures': previous_failures,
                'tools_to_avoid': retry_info.get('tools_already_tried', []),
                'failed_strategies': retry_info.get('strategies_tried', []),
                'failure_patterns': RetryManager._analyze_failure_patterns(previous_failures)
            }
        else:
            return {
                'is_retry': False,
                'attempt_number': 1,
                'previous_failures': [],
                'tools_to_avoid': [],
                'failed_strategies': [],
                'failure_patterns': {}
            }
    
    @staticmethod
    def record_planning_attempt(state: AgentState) -> AgentState:
        """
        Record what tools and strategies are being attempted.
        
        Args:
            state: Current agent state with execution plan
            
        Returns:
            Updated state with recorded attempt information
        """
        
        if 'execution_plan' in state and 'retry_info' in state:
            plan = state['execution_plan']
            retry_info = state['retry_info']
            
            # Track tools being attempted
            tools_in_plan = [step.tool_name for step in plan.steps]
            if 'tools_already_tried' not in retry_info:
                retry_info['tools_already_tried'] = []
            retry_info['tools_already_tried'].extend(tools_in_plan)
            
            # Track strategy being attempted
            if 'strategies_tried' not in retry_info:
                retry_info['strategies_tried'] = []
            retry_info['strategies_tried'].append(plan.strategy)
            
            state['retry_info'] = retry_info
        
        return state
    
    @staticmethod
    def record_failure(state: AgentState) -> AgentState:
        """
        Record a failure attempt with detailed information for future planning.
        
        Args:
            state: Current agent state with failure information
            
        Returns:
            Updated state with recorded failure
        """
        
        retry_info = state.get('retry_info', {})
        quality_assessment = state.get('quality_assessment', {})
        execution_plan = state.get('execution_plan')
        
        # Create failure record
        failure_record = {
            'attempt': retry_info.get('attempt_count', 1),
            'reason': quality_assessment.get('reason', 'unknown'),
            'description': quality_assessment.get('description', 'No description'),
            'data_count': quality_assessment.get('data_count', 0),
            'useful_data_count': quality_assessment.get('useful_data_count', 0),
            'confidence': quality_assessment.get('confidence', 0.0),
            'tools_used': [step.tool_name for step in execution_plan.steps] if execution_plan else [],
            'strategy_used': execution_plan.strategy if execution_plan else 'unknown',
            'timestamp': datetime.now()
        }
        
        # Add to failure history
        if 'previous_failures' not in retry_info:
            retry_info['previous_failures'] = []
        retry_info['previous_failures'].append(failure_record)
        retry_info['attempt_count'] = retry_info.get('attempt_count', 1) + 1
        
        state['retry_info'] = retry_info
        
        return state
    
    @staticmethod
    def _analyze_failure_patterns(failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze failure patterns to provide insights for better re-planning.
        
        Args:
            failures: List of previous failure records
            
        Returns:
            Analysis of failure patterns
        """
        
        if not failures:
            return {}
        
        # Count failure reasons
        failure_reasons = {}
        tools_that_failed = {}
        strategies_that_failed = {}
        
        for failure in failures:
            reason = failure.get('reason', 'unknown')
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            
            for tool in failure.get('tools_used', []):
                tools_that_failed[tool] = tools_that_failed.get(tool, 0) + 1
            
            strategy = failure.get('strategy_used', 'unknown')
            strategies_that_failed[strategy] = strategies_that_failed.get(strategy, 0) + 1
        
        return {
            'most_common_failure_reason': max(failure_reasons.items(), key=lambda x: x[1]) if failure_reasons else None,
            'most_problematic_tool': max(tools_that_failed.items(), key=lambda x: x[1]) if tools_that_failed else None,
            'least_effective_strategy': max(strategies_that_failed.items(), key=lambda x: x[1]) if strategies_that_failed else None,
            'total_failures': len(failures),
            'failure_reasons_distribution': failure_reasons
        }
    
    @staticmethod
    def get_retry_summary(state: AgentState) -> Dict[str, Any]:
        """
        Get a summary of retry attempts for final response metadata.
        
        Args:
            state: Final agent state
            
        Returns:
            Summary of retry attempts and failures
        """
        
        retry_info = state.get('retry_info', {})
        
        return {
            'total_attempts': retry_info.get('attempt_count', 1),
            'max_attempts': retry_info.get('max_attempts', 3),
            'retry_needed': len(retry_info.get('previous_failures', [])) > 0,
            'failure_count': len(retry_info.get('previous_failures', [])),
            'unique_tools_tried': len(set(retry_info.get('tools_already_tried', []))),
            'unique_strategies_tried': len(set(retry_info.get('strategies_tried', []))),
            'failure_patterns': RetryManager._analyze_failure_patterns(retry_info.get('previous_failures', []))
        }