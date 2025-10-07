"""
Enhanced Workflow Nodes

Wrapper nodes that add retry logic, quality assessment, and feedback
to the base workflow nodes for intelligent cyclical execution.
"""

from typing import Dict, Any
from agent.state import AgentState, WorkflowStatus, StateManager
from agent.nodes import planner_node, tool_executor_node, synthesizer_node
from .quality_assessor import WorkflowQualityAssessor
from .retry_manager import RetryManager


class EnhancedWorkflowNodes:
    """
    Enhanced versions of workflow nodes with retry logic and quality assessment.
    """
    
    @staticmethod
    async def enhanced_planner_node(state: AgentState) -> AgentState:
        """
        Enhanced planner that considers previous failures for smarter re-planning.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution plan and retry context
        """
        
        # Initialize retry tracking
        state = RetryManager.initialize_retry_info(state)
        
        # Create planning context based on retry history
        planning_context = RetryManager.create_planning_context(state)
        state['planning_context'] = planning_context
        
        # Call the original planner node
        updated_state = await planner_node(state)
        
        # Record what we're planning to try
        updated_state = RetryManager.record_planning_attempt(updated_state)
        
        return updated_state
    
    @staticmethod
    async def enhanced_executor_node(state: AgentState) -> AgentState:
        """
        Enhanced executor that includes quality assessment of results.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution results and quality assessment
        """
        
        # Execute the tools
        updated_state = await tool_executor_node(state)
        
        # Assess result quality
        quality_assessment = WorkflowQualityAssessor.assess_result_quality(updated_state)
        updated_state['quality_assessment'] = quality_assessment
        
        # Add quality info to debug
        if 'debug_info' not in updated_state:
            updated_state['debug_info'] = {}
        
        updated_state['debug_info']['quality_assessment'] = quality_assessment
        
        return updated_state
    
    @staticmethod
    async def enhanced_synthesizer_node(state: AgentState) -> AgentState:
        """
        Enhanced synthesizer that includes retry summary in metadata.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final response and retry metadata
        """
        
        # Call the original synthesizer node
        updated_state = await synthesizer_node(state)
        
        # Add retry summary to response metadata
        retry_summary = RetryManager.get_retry_summary(updated_state)
        
        if 'response_metadata' not in updated_state:
            updated_state['response_metadata'] = {}
        
        updated_state['response_metadata']['retry_summary'] = retry_summary
        
        # Add retry info to debug
        if 'debug_info' not in updated_state:
            updated_state['debug_info'] = {}
        
        updated_state['debug_info']['retry_summary'] = retry_summary
        
        return updated_state
    
    @staticmethod
    async def re_planner_node(state: AgentState) -> AgentState:
        """
        Handle re-planning by recording failure and updating context.
        
        Args:
            state: Current agent state with failure information
            
        Returns:
            Updated state ready for re-planning
        """
        
        # Record the failure
        state = RetryManager.record_failure(state)
        
        # Update workflow status to indicate re-planning
        state = StateManager.update_status(state, WorkflowStatus.PLANNING)
        
        # Call enhanced planner with updated failure context
        return await EnhancedWorkflowNodes.enhanced_planner_node(state)
    
    @staticmethod
    def quality_check_node(state: AgentState) -> str:
        """
        Quality check decision node for LangGraph conditional routing.
        
        Args:
            state: Current agent state with quality assessment
            
        Returns:
            Next node to route to: "re_plan", "synthesize", or "end"
        """
        
        return WorkflowQualityAssessor.should_re_plan(state, max_attempts=3)
    
    @staticmethod
    async def fallback_response_node(state: AgentState) -> AgentState:
        """
        Generate a fallback response when all retry attempts are exhausted.
        
        Args:
            state: Current agent state after failed attempts
            
        Returns:
            Updated state with fallback response
        """
        
        retry_info = state.get('retry_info', {})
        failures = retry_info.get('previous_failures', [])
        
        # Create fallback response based on failure analysis
        if failures:
            last_failure = failures[-1]
            failure_reason = last_failure.get('reason', 'unknown')
            
            if failure_reason == 'empty_results':
                fallback_message = f"I searched extensively but couldn't find any results for your query: '{state['user_query']}'. The database might not contain information matching your specific request."
            elif failure_reason == 'no_useful_data':
                fallback_message = f"I found some data related to your query: '{state['user_query']}', but it wasn't substantial enough to provide a meaningful response. Please try rephrasing your question or being more specific."
            elif failure_reason == 'low_success_rate':
                fallback_message = f"I encountered technical difficulties while searching for information about: '{state['user_query']}'. Please try again in a moment, or rephrase your question."
            else:
                fallback_message = f"I apologize, but I wasn't able to find satisfactory results for your query: '{state['user_query']}' after multiple search attempts. Please try rephrasing your question or providing more specific details."
        else:
            fallback_message = f"I apologize, but I encountered difficulties processing your query: '{state['user_query']}'. Please try again or rephrase your question."
        
        # Update state with fallback response
        state['final_response'] = fallback_message
        state = StateManager.update_status(state, WorkflowStatus.COMPLETED)
        
        # Add fallback metadata
        if 'response_metadata' not in state:
            state['response_metadata'] = {}
        
        state['response_metadata']['response_type'] = 'fallback'
        state['response_metadata']['retry_exhausted'] = True
        state['response_metadata']['retry_summary'] = RetryManager.get_retry_summary(state)
        
        return state