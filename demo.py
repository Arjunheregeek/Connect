#!/usr/bin/env python3
"""
Connect Agent Demo

Interactive demo script showcasing the agent's capabilities
with the people knowledge graph.
"""

import asyncio
import time
from typing import Dict, Any
from agent import (
    ask_sync, 
    ask_detailed_sync, 
    batch_ask,
    get_agent_info, 
    get_session_summary,
    clear_session
)


def print_banner():
    """Print welcome banner."""
    
    print("\n" + "="*60)
    print("🤖 CONNECT AGENT DEMO")
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
        response = ask_sync(query)
        duration = time.time() - start_time
        
        print(f"{response[:100]}..." if len(response) > 100 else response)
        print(f"   ⏱️  Execution time: {duration:.2f}s")


def demo_detailed_query():
    """Demonstrate detailed query with metadata."""
    
    print_section("DETAILED QUERY")
    
    query = "Find software engineers at Google who know JavaScript"
    print(f"Question: {query}")
    
    result = ask_detailed_sync(query)
    
    print(f"\n📝 Response: {result['response'][:150]}...")
    print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
    print(f"🔄 Retry Count: {result['retry_count']}")
    print(f"⏱️  Execution Time: {result['execution_time']:.2f}s")
    print(f"✅ Success: {result['success']}")
    
    if result.get('quality_score'):
        print(f"📊 Quality Score: {result['quality_score']:.2f}")


def demo_batch_queries():
    """Demonstrate batch processing."""
    
    print_section("BATCH QUERIES")
    
    questions = [
        "Find data scientists",
        "Who works at Microsoft?",
        "Find people with machine learning skills"
    ]
    
    print(f"Processing {len(questions)} queries in batch...")
    start_time = time.time()
    
    responses = batch_ask(questions)
    duration = time.time() - start_time
    
    print(f"⏱️  Total execution time: {duration:.2f}s")
    print(f"📊 Average time per query: {duration/len(questions):.2f}s")
    
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. {question}")
        print(f"   → {response[:80]}..." if len(response) > 80 else f"   → {response}")


def demo_agent_info():
    """Display agent information and capabilities."""
    
    print_section("AGENT INFORMATION")
    
    info = get_agent_info()
    
    print(f"🤖 Agent: {info['agent_type']} v{info['version']}")
    print(f"📋 Description: {info['description']}")
    
    print("\n🛠️  Capabilities:")
    for capability in info['capabilities']:
        print(f"   • {capability}")
    
    if info['session_stats']['total_questions'] > 0:
        stats = info['session_stats']
        print(f"\n📈 Session Statistics:")
        print(f"   • Total queries: {stats['total_questions']}")
        print(f"   • Success rate: {stats['successful_queries']}/{stats['total_questions']}")
        print(f"   • Avg execution time: {stats['average_execution_time']:.2f}s")
        
        if stats['most_used_tools']:
            print("   • Most used tools:")
            for tool_info in stats['most_used_tools'][:3]:
                print(f"     - {tool_info['tool']}: {tool_info['usage_count']} times")


def demo_session_summary():
    """Display session summary."""
    
    print_section("SESSION SUMMARY")
    
    summary = get_session_summary()
    
    if summary['total_questions'] == 0:
        print("No queries in current session.")
        return
    
    print(f"📊 Session Overview:")
    print(f"   • Total Questions: {summary['total_questions']}")
    print(f"   • Success Rate: {summary['success_rate']:.1%}")
    print(f"   • Average Execution Time: {summary['average_execution_time']:.2f}s")
    print(f"   • Unique Tools Used: {summary['unique_tools_used']}")
    
    retry_stats = summary['retry_statistics']
    print(f"\n🔄 Retry Statistics:")
    print(f"   • Queries with retries: {retry_stats['queries_with_retries']}")
    print(f"   • Average retry count: {retry_stats['average_retry_count']:.1f}")
    print(f"   • Max retries used: {retry_stats['max_retries_used']}")


def interactive_mode():
    """Run interactive demo mode."""
    
    print_section("INTERACTIVE MODE")
    print("Ask any question about people in the knowledge graph.")
    print("Type 'quit' to exit, 'info' for agent info, 'summary' for session summary.")
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            elif question.lower() == 'info':
                demo_agent_info()
                continue
            elif question.lower() == 'summary':
                demo_session_summary()
                continue
            elif not question:
                continue
            
            print("🤖 Agent is thinking...")
            start_time = time.time()
            
            response = ask_sync(question)
            duration = time.time() - start_time
            
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
        clear_session()
        
        # Run demo sections
        demo_basic_queries()
        demo_detailed_query()
        demo_batch_queries()
        demo_agent_info()
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