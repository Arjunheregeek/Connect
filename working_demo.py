#!/usr/bin/env python3
"""
Working Connect Agent Demo

Interactive demo script showcasing the working agent's capabilities
with the people knowledge graph.
"""

import time
from simple_agent import ask_simple, ask_simple_detailed, simple_agent


def print_banner():
    """Print welcome banner."""
    
    print("\n" + "="*60)
    print("🤖 CONNECT AGENT DEMO (WORKING VERSION)")
    print("Intelligent People Knowledge Graph Assistant")
    print("="*60)


def print_section(title: str):
    """Print section header."""
    
    print(f"\n{'─'*20} {title} {'─'*20}")


def demo_basic_queries():
    """Demonstrate basic agent queries."""
    
    print_section("BASIC QUERIES")
    
    queries = [
        "Find people named John Smith",
        "Who are the Python developers?", 
        "Find React experts at tech companies"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Question: {query}")
        print("   Answer:", end=" ")
        
        start_time = time.time()
        response = ask_simple(query)
        duration = time.time() - start_time
        
        # Show first 200 characters of response
        display_response = response[:200] + "..." if len(response) > 200 else response
        print(display_response)
        print(f"   ⏱️  Execution time: {duration:.2f}s")


def demo_detailed_query():
    """Demonstrate detailed query with metadata."""
    
    print_section("DETAILED QUERY")
    
    query = "Find software engineers at Google who know JavaScript"
    print(f"Question: {query}")
    
    result = ask_simple_detailed(query)
    
    print(f"\n📝 Response: {result['response'][:200]}...")
    print(f"🔧 Tools Used: {', '.join(result['metadata']['tools_used']) if result['metadata']['tools_used'] else 'Node-level tools'}")
    print(f"🔄 Retry Count: {result['metadata']['retry_count']}")
    print(f"⏱️  Execution Time: {result['metadata']['execution_time']:.2f}s")
    print(f"✅ Success: {result['success']}")
    print(f"📊 Data Found: {result['metadata']['data_found']} items")
    
    if result['metadata'].get('quality_assessment'):
        qa = result['metadata']['quality_assessment']
        print(f"🎯 Quality: {qa.get('reason', 'N/A')} (confidence: {qa.get('confidence', 0):.2f})")


def demo_session_summary():
    """Display session summary."""
    
    print_section("SESSION SUMMARY")
    
    history = simple_agent.get_session_history()
    
    if not history:
        print("No queries in current session.")
        return
    
    print(f"📊 Session Overview:")
    print(f"   • Total Questions: {len(history)}")
    
    successful = [h for h in history if h['success']]
    print(f"   • Success Rate: {len(successful)}/{len(history)} ({len(successful)/len(history):.1%})")
    
    avg_time = sum(h['execution_time'] for h in history) / len(history)
    print(f"   • Average Execution Time: {avg_time:.2f}s")
    
    total_retries = sum(h['retry_count'] for h in history)
    print(f"   • Total Retries: {total_retries}")


def interactive_mode():
    """Run interactive demo mode."""
    
    print_section("INTERACTIVE MODE")
    print("Ask any question about people in the knowledge graph.")
    print("Type 'quit' to exit, 'summary' for session summary, 'clear' to clear history.")
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            elif question.lower() == 'summary':
                demo_session_summary()
                continue
            elif question.lower() == 'clear':
                simple_agent.clear_history()
                print("🧹 Session history cleared")
                continue
            elif not question:
                continue
            
            print("🤖 Agent is thinking...")
            start_time = time.time()
            
            response = ask_simple(question)
            duration = time.time() - start_time
            
            # Display response with nice formatting
            if len(response) > 300:
                print(f"💬 Response: {response[:300]}...")
                print(f"📄 Full response available - {len(response)} characters total")
            else:
                print(f"💬 Response: {response}")
            
            print(f"⏱️  Time: {duration:.2f}s")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Run the complete demo."""
    
    print_banner()
    
    try:
        # Clear previous session
        simple_agent.clear_history()
        
        # Run demo sections
        demo_basic_queries()
        demo_detailed_query()
        demo_session_summary()
        
        # Interactive session
        print("\n" + "="*60)
        print("Demo completed! Starting interactive mode...")
        interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure the MCP server is running and accessible.")
    
    print("\n" + "="*60)
    print("Thank you for trying Connect Agent!")
    print("="*60)


if __name__ == "__main__":
    main()