"""
Synthesizer Node Orchestrator

Main orchestrator that coordinates data analysis, response generation, and quality assessment.
This module brings together all the synthesizer components.
"""

from datetime import datetime
from typing import Dict, Any
from agent.state import AgentState, WorkflowStatus, StateManager
from .data_analyzer import DataAnalyzer
from .response_generator import ResponseGenerator
from .quality_assessor import QualityAssessor


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