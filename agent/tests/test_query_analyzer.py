"""
Simple test script for QueryAnalyzer with GPT-5 Mini
Run this to verify the query analyzer is working correctly.
"""

import os
import sys
import json

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agent.nodes.planner.query_analyzer import QueryAnalyzer


def test_query(analyzer, query, description):
    """Test a single query and print results."""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    
    result = analyzer.analyze_query(query)
    
    # Print formatted result
    print(f"\nModel: {result.get('meta', {}).get('model', 'unknown')}")
    print(f"Complexity: {result.get('breakdown', {}).get('complexity', 'unknown')}")
    print(f"Intent: {result.get('breakdown', {}).get('intent', 'unknown')}")
    print(f"Execution Strategy: {result.get('execution_strategy', 'unknown')}")
    
    print(f"\nTools Selected ({len(result.get('tools_to_call', []))}):")
    for i, tool in enumerate(result.get('tools_to_call', []), 1):
        print(f"  {i}. {tool.get('tool', 'unknown')}")
        print(f"     Params: {tool.get('params', {})}")
        print(f"     Reason: {tool.get('reason', 'N/A')}")
    
    print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
    
    # Check for errors
    if 'error' in result:
        print(f"\n⚠️  ERROR: {result['error']}")
    
    # Full JSON
    print(f"\nFull Response:")
    print(json.dumps(result, indent=2))
    
    return result


def main():
    """Run test suite."""
    print("=" * 70)
    print("QUERY ANALYZER TEST SUITE - GPT-5 Mini")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = QueryAnalyzer(model="gpt-5-mini")
    
    # Test cases - reduced to key scenarios for faster execution
    test_cases = [
        # Simple skill searches
        ("Find Python developers", "Simple skill search"),
        
        # Compound searches
        ("Python developers at Google", "Skill + Company"),
        ("Java engineers in San Francisco", "Skill + Location"),
        
        # Aggregations
        ("What are the most common skills?", "Skill aggregation"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for query, description in test_cases:
        try:
            result = test_query(analyzer, query, description)
            
            # Basic validation
            if result.get('tools_to_call'):
                # Check no natural_language_search
                has_forbidden = any(
                    t.get('tool') == 'natural_language_search' 
                    for t in result.get('tools_to_call', [])
                )
                if has_forbidden:
                    print("❌ FAILED: Used forbidden natural_language_search")
                    failed += 1
                else:
                    print("✅ PASSED")
                    passed += 1
            else:
                print("⚠️  WARNING: No tools selected")
                
            results.append({
                "query": query,
                "description": description,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(test_cases)*100:.1f}%")
    
    return results


if __name__ == "__main__":
    main()
