"""
End-to-End Test for Complete Enhanced Workflow

Tests the full pipeline:
Start → Enhanced Planner → Enhanced Executor → Enhanced Synthesizer → End

This validates:
1. Query decomposition and sub-query generation
2. Multi-tool execution with person ID extraction
3. Complete profile fetching
4. GPT-4o response generation
5. Natural language output

Requirements:
- MCP server running on port 8000
- Neo4j database with person data
- OpenAI API key configured
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agent.workflow.graph_builder import WorkflowGraphBuilder
from agent.state.types import AgentState


async def test_enhanced_workflow():
    """
    Test the complete enhanced workflow end-to-end.
    """
    print("="*70)
    print("END-TO-END ENHANCED WORKFLOW TEST")
    print("="*70)
    print("\nThis test runs the complete pipeline from query to response:")
    print("1. Enhanced Planner (QueryDecomposer + SubQueryGenerator)")
    print("2. Enhanced Executor (Multi-tool execution)")
    print("3. Enhanced Synthesizer (Profile fetching + GPT-4o)")
    print("="*70)
    
    # Create the workflow
    print("\n📦 Building LangGraph workflow...")
    workflow = WorkflowGraphBuilder.build_graph()
    print("✅ Workflow built successfully\n")
    
    # Test queries
    test_queries = [
        "Find Machine Learning experts with experience in Python",
        "Find people who graduated from IIT Bombay with AI skills",
        "Find senior software engineers in San Francisco"
    ]
    
    print(f"\n📝 Testing {len(test_queries)} queries:\n")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    print("\n" + "="*70)
    
    # Test each query
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST QUERY {i}/{len(test_queries)}")
        print(f"{'='*70}")
        print(f"Query: {query}\n")
        
        # Create initial state
        initial_state: AgentState = {
            'user_query': query,
            'workflow_status': 'started'
        }
        
        try:
            # Run the workflow
            print("▶️  Running workflow...\n")
            final_state = await workflow.ainvoke(initial_state)
            
            # Display results
            print(f"\n{'='*70}")
            print(f"WORKFLOW COMPLETED - QUERY {i}")
            print(f"{'='*70}")
            
            print(f"\n📊 Final Status: {final_state.get('workflow_status', 'unknown')}")
            
            # Show planning metadata
            if 'planning_metadata' in final_state:
                metadata = final_state['planning_metadata']
                print(f"\n🧠 Planning Metadata:")
                print(f"   - Filters extracted: {len(final_state.get('filters', {}))} types")
                print(f"   - Sub-queries generated: {len(final_state.get('sub_queries', []))}")
                print(f"   - Execution strategy: {final_state.get('execution_strategy', 'N/A')}")
                print(f"   - Total tokens used: {metadata.get('total_tokens', 0)}")
            
            # Show execution results
            if 'tool_results' in final_state:
                print(f"\n⚡ Execution Results:")
                print(f"   - Tools executed: {len(final_state['tool_results'])}")
                print(f"   - Total person IDs found: {len(final_state.get('accumulated_data', []))}")
            
            # Show synthesis metadata
            if 'synthesizer_metadata' in final_state:
                synth_meta = final_state['synthesizer_metadata']
                print(f"\n📝 Synthesis Metadata:")
                print(f"   - Total matches: {synth_meta.get('total_person_ids', 0)}")
                print(f"   - Profiles fetched: {synth_meta.get('profiles_fetched', 0)}")
                print(f"   - GPT-4o tokens: {synth_meta.get('token_usage', 0)}")
            
            # Display the final response
            print(f"\n{'='*70}")
            print("FINAL RESPONSE TO USER:")
            print(f"{'='*70}")
            response = final_state.get('response', 'No response generated')
            print(response)
            print(f"{'='*70}")
            
            # Check for errors
            if 'errors' in final_state and final_state['errors']:
                print(f"\n⚠️  Errors encountered:")
                for error in final_state['errors']:
                    print(f"   - {error}")
            
        except Exception as e:
            print(f"\n❌ Error running workflow for query {i}:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*70}\n")
    
    print("\n" + "="*70)
    print("END-TO-END TEST COMPLETE")
    print("="*70)


async def test_single_query():
    """
    Test a single query for debugging.
    """
    print("="*70)
    print("SINGLE QUERY TEST - ENHANCED WORKFLOW")
    print("="*70)
    
    # Build workflow
    print("\n📦 Building workflow...")
    workflow = WorkflowGraphBuilder.build_graph()
    print("✅ Workflow built\n")
    
    # Test query
    query = "Find Machine Learning experts"
    print(f"Query: {query}\n")
    
    # Create initial state
    initial_state: AgentState = {
        'user_query': query,
        'workflow_status': 'started'
    }
    
    # Run workflow
    print("▶️  Running workflow...\n")
    final_state = await workflow.ainvoke(initial_state)
    
    # Display results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"\nStatus: {final_state.get('workflow_status')}")
    print(f"Person IDs found: {len(final_state.get('accumulated_data', []))}")
    
    if 'synthesizer_metadata' in final_state:
        print(f"\nProfiles fetched: {final_state['synthesizer_metadata'].get('profiles_fetched', 0)}")
    
    print(f"\n{'='*70}")
    print("RESPONSE:")
    print(f"{'='*70}")
    print(final_state.get('response', 'No response'))
    print(f"{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    # Choose test mode
    if len(sys.argv) > 1 and sys.argv[1] == "single":
        # Single query test for quick debugging
        asyncio.run(test_single_query())
    else:
        # Full end-to-end test with multiple queries
        asyncio.run(test_enhanced_workflow())
