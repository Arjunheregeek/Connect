"""
Enhanced Planner Node for LangGraph - Integrates QueryDecomposer + SubQueryGenerator

This node replaces simple_planner_node with the intelligent two-step pipeline:
1. QueryDecomposer: Natural language → Structured filters
2. SubQueryGenerator: Filters → Sub-queries with tool mappings

Workflow Integration:
User Query → [THIS NODE] → Enhanced Plan with Sub-queries → Enhanced Executor → Synthesizer
"""

from typing import Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import AgentState
try:
    from agent.state import AgentState
except ImportError:
    # Fallback for standalone execution
    from typing import TypedDict, List
    class AgentState(TypedDict, total=False):
        user_query: str
        conversation_id: str
        workflow_status: str
        messages: List[Dict[str, str]]
        session_id: str
        tools_used: List[str]
        tool_results: List[Dict[str, Any]]
        accumulated_data: List[Any]
        final_response: str
        errors: List[str]
        filters: Dict[str, Any]
        sub_queries: List[Dict[str, Any]]
        execution_strategy: str
        planning_metadata: Dict[str, Any]

# Import the pipeline components
try:
    from agent.nodes.planner.query_decomposer import QueryDecomposer
    from agent.nodes.planner.subquery_generator import SubQueryGenerator
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import pipeline components: {e}")
    PIPELINE_AVAILABLE = False
    QueryDecomposer = None
    SubQueryGenerator = None


async def enhanced_planner_node(state: AgentState) -> AgentState:
    """
    Enhanced Planner node using QueryDecomposer + SubQueryGenerator pipeline.
    
    Pipeline Flow:
    1. Extract user_query from state
    2. QueryDecomposer.decompose(query) → filters dict
    3. SubQueryGenerator.generate(filters) → sub_queries list
    4. Store filters, sub_queries, execution_strategy in state
    5. Pass enhanced state to executor
    
    State Input (from user):
        - user_query: str (natural language query)
    
    State Output (to executor):
        - filters: Dict (extracted filters from query)
        - sub_queries: List[Dict] (sub-queries with tool mappings)
        - execution_strategy: str (parallel_intersect/parallel_union/sequential)
        - workflow_status: str (updated to 'planning_complete')
    
    Args:
        state: Current AgentState with user_query
        
    Returns:
        Updated AgentState with enhanced planning results
    """
    
    # Update status
    state['workflow_status'] = 'planning'
    
    # Check if pipeline components are available
    if not PIPELINE_AVAILABLE or not QueryDecomposer or not SubQueryGenerator:
        # Fallback to simple planning
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append("Enhanced pipeline not available, using fallback")
        state['workflow_status'] = 'error'
        return state
    
    try:
        user_query = state.get('user_query', '')
        
        if not user_query or not user_query.strip():
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append("Empty user query provided")
            state['workflow_status'] = 'error'
            return state
        
        # STEP 1: Decompose query into filters
        decomposer = QueryDecomposer()
        filters_result = decomposer.decompose(user_query)
        
        # Check for decomposition errors
        if 'error' in filters_result.get('meta', {}):
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Query decomposition failed: {filters_result['meta']['error']}")
            state['workflow_status'] = 'error'
            return state
        
        # STEP 2: Generate sub-queries from filters
        generator = SubQueryGenerator()
        subquery_result = generator.generate(filters_result)
        
        # Check for generation errors
        if 'error' in subquery_result.get('meta', {}):
            if 'errors' not in state:
                state['errors'] = []
            state['errors'].append(f"Sub-query generation failed: {subquery_result['meta']['error']}")
            state['workflow_status'] = 'error'
            return state
        
        # Store results in state for executor
        state['filters'] = filters_result
        state['sub_queries'] = subquery_result.get('sub_queries', [])
        state['execution_strategy'] = subquery_result.get('execution_strategy', 'parallel_union')
        
        # Store metadata for debugging/monitoring
        if 'planning_metadata' not in state:
            state['planning_metadata'] = {}
        
        state['planning_metadata'] = {
            'decomposer_tokens': filters_result.get('meta', {}).get('tokens_used', 0),
            'generator_tokens': subquery_result.get('meta', {}).get('tokens_used', 0),
            'total_sub_queries': subquery_result.get('total_sub_queries', 0),
            'filters_extracted': len([k for k, v in filters_result.items() 
                                     if k.endswith('_filters') and v]),
            'original_query': user_query
        }
        
        # Update workflow status
        state['workflow_status'] = 'planning_complete'
        
        # Log success (for debugging)
        print(f"✓ Enhanced Planning Complete:")
        print(f"  - Filters: {state['planning_metadata']['filters_extracted']} categories")
        print(f"  - Sub-queries: {state['planning_metadata']['total_sub_queries']}")
        print(f"  - Strategy: {state['execution_strategy']}")
        print(f"  - Total tokens: {state['planning_metadata']['decomposer_tokens'] + state['planning_metadata']['generator_tokens']}")
        
    except Exception as e:
        # Handle unexpected errors
        if 'errors' not in state:
            state['errors'] = []
        state['errors'].append(f"Enhanced planning error: {str(e)}")
        state['workflow_status'] = 'error'
        
        # Add debug info
        import traceback
        print(f"❌ Enhanced Planning Error: {str(e)}")
        print(traceback.format_exc())
    
    return state


# Convenience function for testing the node standalone
async def test_enhanced_planner():
    """Test the enhanced planner node with sample queries."""
    
    test_queries = [
        "Find Python developers at Google",
        "AI experts in Bangalore with 5+ years experience",
        "Find startup founders"
    ]
    
    print("="*70)
    print("ENHANCED PLANNER NODE - STANDALONE TEST")
    print("="*70)
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        
        # Create test state
        test_state: AgentState = {
            'user_query': query,
            'conversation_id': 'test-123',
            'workflow_status': 'initialized',
            'messages': [],
            'session_id': 'test-session',
            'tools_used': [],
            'tool_results': [],
            'accumulated_data': [],
            'final_response': '',
            'errors': []
        }
        
        # Run the planner node
        result_state = await enhanced_planner_node(test_state)
        
        # Display results
        print(f"\nStatus: {result_state['workflow_status']}")
        
        if result_state.get('errors'):
            print(f"Errors: {result_state['errors']}")
        else:
            print(f"\n✓ Filters Extracted:")
            filters = result_state.get('filters', {})
            for key, value in filters.items():
                if key.endswith('_filters') and value:
                    print(f"  - {key}: {value}")
                elif key == 'other_criteria' and value:
                    print(f"  - {key}: {value}")
            
            print(f"\n✓ Sub-Queries Generated: {len(result_state.get('sub_queries', []))}")
            for i, sq in enumerate(result_state.get('sub_queries', []), 1):
                print(f"  {i}. [P{sq.get('priority')}] {sq.get('tool')} - {sq.get('sub_query', '')[:60]}...")
            
            print(f"\n✓ Execution Strategy: {result_state.get('execution_strategy')}")
            
            if 'planning_metadata' in result_state:
                meta = result_state['planning_metadata']
                total_tokens = meta.get('decomposer_tokens', 0) + meta.get('generator_tokens', 0)
                print(f"\n✓ Metadata:")
                print(f"  - Total Tokens: {total_tokens}")
                print(f"  - Filters: {meta.get('filters_extracted', 0)} categories")
                print(f"  - Sub-queries: {meta.get('total_sub_queries', 0)}")
        
        print("="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_planner())
