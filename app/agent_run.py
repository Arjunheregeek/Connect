#!/usr/bin/env python3
"""
Connect Agent Main Runner

Main entry point for the Enhanced Connect Agent system.
Provides both CLI and programmatic interfaces for querying the people knowledge graph.
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any, List

# Add parent directory to path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.workflow.graph_builder import WorkflowGraphBuilder
from agent.state.types import AgentState


def format_person_profile(person: Dict[str, Any], index: int = None) -> str:
    """Format a person's profile for display."""
    lines = []
    
    # Header with person number
    if index is not None:
        lines.append(f"\n{'='*80}")
        lines.append(f"👤 PERSON #{index}")
        lines.append(f"{'='*80}")
    else:
        lines.append(f"\n{'='*80}")
    
    # Basic Info
    name = person.get('name', 'N/A')
    person_id = person.get('person_id', 'N/A')
    lines.append(f"📛 Name: {name}")
    lines.append(f"🆔 ID: {person_id}")
    
    # Professional Info
    headline = person.get('headline', 'N/A')
    if headline and headline != 'N/A':
        lines.append(f"💼 Headline: {headline}")
    
    current_company = person.get('current_company', 'N/A')
    current_title = person.get('current_title', 'N/A')
    if current_company and current_company != 'N/A':
        lines.append(f"🏢 Current: {current_title} at {current_company}")
    
    # Experience
    total_exp = person.get('total_experience_months')
    if total_exp:
        years = int(total_exp // 12)
        months = int(total_exp % 12)
        exp_str = f"{years} years" if months == 0 else f"{years} years {months} months"
        lines.append(f"⏳ Experience: {exp_str}")
    
    # Summary
    summary = person.get('summary', 'N/A')
    if summary and summary != 'N/A' and len(summary) > 0:
        # Truncate long summaries
        if len(summary) > 200:
            summary = summary[:200] + "..."
        lines.append(f"📝 Summary: {summary}")
    
    # Technical Skills
    tech_skills = person.get('technical_skills', [])
    if tech_skills and len(tech_skills) > 0:
        skills_str = ", ".join(tech_skills[:10])  # Show first 10 skills
        if len(tech_skills) > 10:
            skills_str += f" ... (+{len(tech_skills) - 10} more)"
        lines.append(f"🔧 Tech Skills: {skills_str}")
    
    # Secondary Skills
    secondary_skills = person.get('secondary_skills', [])
    if secondary_skills and len(secondary_skills) > 0:
        skills_str = ", ".join(secondary_skills[:5])  # Show first 5
        if len(secondary_skills) > 5:
            skills_str += f" ... (+{len(secondary_skills) - 5} more)"
        lines.append(f"💡 Soft Skills: {skills_str}")
    
    # Domain Knowledge
    domains = person.get('domain_knowledge', [])
    if domains and len(domains) > 0:
        domain_str = ", ".join(domains)
        lines.append(f"🎯 Domains: {domain_str}")
    
    lines.append(f"{'='*80}\n")
    
    return "\n".join(lines)


def format_response_with_profiles(response: str, accumulated_data: List[Dict[str, Any]]) -> str:
    """Format response with person profiles extracted from accumulated_data."""
    formatted_parts = []
    
    # Add the GPT-4o generated response first
    formatted_parts.append("="*80)
    formatted_parts.append("📊 QUERY RESULTS")
    formatted_parts.append("="*80)
    formatted_parts.append(response)
    formatted_parts.append("")
    
    # Extract unique person profiles from accumulated_data
    person_profiles = {}
    
    for data_item in accumulated_data:
        # Check if this is a person profile (has person_id and name)
        if isinstance(data_item, dict) and 'person_id' in data_item and 'name' in data_item:
            person_id = data_item['person_id']
            # Avoid duplicates
            if person_id not in person_profiles:
                person_profiles[person_id] = data_item
    
    # Display formatted profiles if any were found
    if person_profiles:
        formatted_parts.append("\n" + "="*80)
        formatted_parts.append(f"👥 DETAILED PROFILES ({len(person_profiles)} people)")
        formatted_parts.append("="*80)
        
        for idx, (person_id, profile) in enumerate(person_profiles.items(), 1):
            formatted_parts.append(format_person_profile(profile, idx))
    
    return "\n".join(formatted_parts)


class ConnectAgent:
    """Enhanced Connect Agent with GPT-4o powered query processing."""
    
    def __init__(self):
        """Initialize the agent."""
        print("🚀 Initializing Enhanced Connect Agent...")
        self.workflow_builder = WorkflowGraphBuilder()
        self.workflow = self.workflow_builder.build_graph()
        self.session_history: List[Dict[str, Any]] = []
        print("✅ Agent ready!")
    
    async def ask(self, question: str, session_id: str = None, formatted: bool = True) -> str:
        """Ask a question and get response."""
        result = await self.ask_detailed(question, session_id, formatted=formatted)
        return result['response']
    
    async def ask_detailed(self, question: str, session_id: str = None, formatted: bool = True) -> Dict[str, Any]:
        """Ask a question with detailed metadata."""
        start_time = time.time()
        session_id = session_id or f"session-{int(time.time())}"
        
        # Create initial state
        initial_state: AgentState = {
            'user_query': question,
            'session_id': session_id,
            'workflow_status': 'initialized',
            'messages': [],
            'accumulated_data': [],
            'tool_results': [],
            'errors': [],
            'tools_used': [],
            'filters': {},
            'sub_queries': [],
            'execution_strategy': 'parallel_union',
            'planning_metadata': {},
            'final_response': ''
        }
        
        try:
            print(f"🔍 Processing: '{question}'")
            result = await self.workflow.ainvoke(initial_state)
            execution_time = time.time() - start_time
            
            # Get response from result
            response = result.get('final_response', 'No response generated.')
            accumulated_data = result.get('accumulated_data', [])
            
            # Format response with person profiles if requested
            if formatted and accumulated_data:
                response = format_response_with_profiles(response, accumulated_data)
            
            detailed_result = {
                'response': response,
                'success': True,
                'metadata': {
                    'session_id': session_id,
                    'execution_time': execution_time,
                    'tools_used': result.get('tools_used', []),
                    'data_found': len(result.get('accumulated_data', [])),
                    'workflow_status': result.get('workflow_status', 'unknown'),
                    'filters': result.get('filters', {}),
                    'sub_queries': len(result.get('sub_queries', []))
                }
            }
            
            self.session_history.append({
                'question': question,
                'response': response,
                'success': True,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            
            return detailed_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_response = f"Error: {str(e)}"
            print(f"❌ {error_response}")
            
            self.session_history.append({
                'question': question,
                'response': error_response,
                'success': False,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            
            return {
                'response': error_response,
                'success': False,
                'metadata': {
                    'session_id': session_id,
                    'execution_time': execution_time,
                    'error': str(e)
                }
            }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.session_history:
            return {'total_questions': 0, 'success_rate': 0.0}
        
        successful = [h for h in self.session_history if h['success']]
        total_time = sum(h['execution_time'] for h in self.session_history)
        
        return {
            'total_questions': len(self.session_history),
            'success_rate': len(successful) / len(self.session_history),
            'average_time': total_time / len(self.session_history),
            'successful': len(successful),
            'failed': len(self.session_history) - len(successful)
        }
    
    def clear_history(self):
        """Clear session history."""
        self.session_history.clear()


# Global instance
_agent = None


def get_agent() -> ConnectAgent:
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        _agent = ConnectAgent()
    return _agent


def ask_sync(question: str) -> str:
    """Synchronous ask wrapper."""
    return asyncio.run(get_agent().ask(question))


async def interactive_mode():
    """Run interactive CLI mode."""
    agent = get_agent()
    
    print("\n" + "="*70)
    print("🤖 ENHANCED CONNECT AGENT - Interactive Mode")
    print("="*70)
    print("Ask questions about professionals in the knowledge graph")
    print("Commands: 'quit' to exit | 'summary' for stats | 'clear' to reset")
    print("="*70)
    
    while True:
        try:
            question = input("\n💬 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            elif question.lower() == 'summary':
                summary = agent.get_session_summary()
                print(f"\n📊 Session Summary:")
                print(f"   Questions: {summary['total_questions']}")
                print(f"   Success: {summary['success_rate']:.1%}")
                print(f"   Avg time: {summary.get('average_time', 0):.2f}s")
                continue
            elif question.lower() == 'clear':
                agent.clear_history()
                print("🧹 History cleared")
                continue
            elif not question:
                continue
            
            start = time.time()
            response = await agent.ask(question)
            duration = time.time() - start
            
            print(f"\n✨ Response:\n{response}")
            print(f"\n⏱️  {duration:.2f}s")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def print_usage():
    """Print usage info."""
    print("""
🤖 Enhanced Connect Agent - People Knowledge Graph Assistant

Usage:
    python app/agent_run.py                  # Interactive mode
    python app/agent_run.py "your question"  # Single query
    python app/agent_run.py --help           # Show help

Examples:
    python app/agent_run.py "Find Python developers at Google"
    python app/agent_run.py "Who are AI experts in Bangalore?"
    python app/agent_run.py "Find IIT Bombay alumni working in startups"

Interactive Commands:
    - Type questions naturally
    - 'summary' - Show session statistics
    - 'clear' - Clear history
    - 'quit' - Exit

Features:
    ✨ GPT-4o powered query understanding
    ✨ Multi-tool parallel execution
    ✨ Professional response generation
    ✨ 1,028+ professional profiles
""")


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # Interactive mode
        asyncio.run(interactive_mode())
    
    elif '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
    
    else:
        # Single query
        question = ' '.join(sys.argv[1:])
        print(f"\n🔍 Question: {question}\n")
        
        try:
            response = ask_sync(question)
            print(f"✨ Response:\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure MCP server is running: python -m mcp.server")


if __name__ == "__main__":
    main()
