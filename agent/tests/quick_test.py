"""
Quick single-query test for QueryAnalyzer - for rapid testing during development
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.nodes.planner.query_analyzer import QueryAnalyzer


def quick_test(query=None):
    """Run a single quick test."""
    
    if query is None:
        query = "Find Python developers at Google"
    
    print(f"Testing Query: {query}")
    print("=" * 70)
    
    analyzer = QueryAnalyzer(model="gpt-5-mini")
    result = analyzer.analyze_query(query)
    
    # Compact output
    print(f"\n✓ Model: {result.get('meta', {}).get('model', 'unknown')}")
    print(f"✓ Intent: {result.get('breakdown', {}).get('intent', 'unknown')}")
    print(f"✓ Strategy: {result.get('execution_strategy', 'unknown')}")
    
    print(f"\n✓ Tools ({len(result.get('tools_to_call', []))}):")
    for tool in result.get('tools_to_call', []):
        print(f"  - {tool.get('tool', 'unknown')}: {tool.get('params', {})}")
    
    # Check for forbidden tool
    has_forbidden = any(
        t.get('tool') == 'natural_language_search' 
        for t in result.get('tools_to_call', [])
    )
    
    if has_forbidden:
        print("\n❌ FAILED: Used forbidden natural_language_search")
    elif 'error' in result:
        print(f"\n⚠️  ERROR: {result['error']}")
    else:
        print("\n✅ PASSED")
    
    print("\nFull JSON:")
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    # Allow custom query from command line
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        quick_test(query)
    else:
        print("Usage: python quick_test.py [query]")
        print("\nRunning default test...\n")
        quick_test()
