#!/usr/bin/env python3
"""
Debug Agent Issues

Simple test script to debug what's happening with the agent.
"""

import asyncio
import traceback
from agent.main_agent import ConnectAgent
from agent.workflow.quality_assessor import WorkflowQualityAssessor

async def debug_agent():
    """Debug the agent directly."""
    
    print("=== DEBUGGING CONNECT AGENT ===")
    
    try:
        # Create agent instance
        agent = ConnectAgent()
        print("✅ Agent created successfully")
        
        # Test simple query
        print("\n🔍 Testing simple query...")
        result = await agent.ask("Find Python developers")
        print(f"Result type: {type(result)}")
        print(f"Result: {result[:100]}..." if len(str(result)) > 100 else f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()

async def debug_detailed():
    """Debug detailed response."""
    
    print("\n=== DEBUGGING DETAILED RESPONSE ===")
    
    try:
        agent = ConnectAgent()
        
        # Test detailed query
        print("\n🔍 Testing detailed query...")
        result = await agent.ask_with_details("Find React developers")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Show the metadata content to understand the state
        if isinstance(result, dict) and 'metadata' in result:
            metadata = result['metadata']
            print(f"\n📋 Metadata details:")
            for key, value in metadata.items():
                if key == 'retry_info':
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {str(value)[:100]}...")
        
        print(f"\nFull result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()

async def debug_quality_on_real_data():
    """Test quality assessment on what looks like real data."""
    
    print("\n=== TESTING QUALITY ASSESSMENT ON SIMULATED REAL DATA ===")
    
    # Simulate what the real state might look like with 48 data items
    real_state = {
        'accumulated_data': [f"Person {i}" for i in range(48)],  # 48 items like in the debug output
        'tool_results': [
            {'tool_name': 'natural_language_search', 'result': [f"Result {i}" for i in range(48)]}
        ],
        'execution_metrics': {'success_rate': 1.0}
    }
    
    assessment = WorkflowQualityAssessor.assess_result_quality(real_state)
    print(f"Real data assessment: {assessment}")

def main():
    """Run debug tests."""
    asyncio.run(debug_agent())
    asyncio.run(debug_detailed())
    asyncio.run(debug_quality_on_real_data())

if __name__ == "__main__":
    main()