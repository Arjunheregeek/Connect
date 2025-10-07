#!/usr/bin/env python3
"""
Connect Agent Main Runner

Main entry point for the simplified Connect Agent system.
Provides both CLI and programmatic interfaces for querying the people knowledge graph.
"""

import asyncio
import sys
import time
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.workflow.graph_builder import WorkflowGraphBuilder


class ConnectAgent:
    """
    Main Connect Agent using simplified LangGraph workflow.
    
    This is the primary interface for the Connect Agent system,
    providing both sync and async methods for querying the knowledge graph.
    """
    
    def __init__(self):
        """Initialize the Connect Agent."""
        self.workflow = WorkflowGraphBuilder.build_graph()
        self.session_history: List[Dict[str, Any]] = []
    
    async def ask(self, question: str, conversation_id: str = None) -> str:
        """
        Ask a question and get a simple response.
        
        Args:
            question: The user's question
            conversation_id: Optional conversation ID for context
            
        Returns:
            String response from the agent
        """
        result = await self.ask_detailed(question, conversation_id)
        return result['response']
    
    async def ask_detailed(self, question: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Ask a question and get detailed response with metadata.
        
        Args:
            question: The user's question
            conversation_id: Optional conversation ID for context
            
        Returns:
            Detailed response dictionary with metadata
        """
        
        start_time = time.time()
        conversation_id = conversation_id or f"conv-{int(time.time())}"
        
        # Create initial state
        initial_state = {
            'user_query': question,
            'conversation_id': conversation_id,
            'workflow_status': 'initialized',
            'messages': [],
            'accumulated_data': [],
            'tool_results': [],
            'errors': [],
            'session_id': f"session-{int(time.time())}",
            'tools_used': []
        }
        
        try:
            # Execute the simplified workflow
            result = await self.workflow.ainvoke(initial_state)
            execution_time = time.time() - start_time
            
            # Extract the final response
            response = result.get('final_response', f"I processed your question '{question}' but didn't generate a final response.")
            
            # Build detailed response
            detailed_result = {
                'response': response,
                'success': True,
                'metadata': {
                    'conversation_id': conversation_id,
                    'execution_time': execution_time,
                    'tools_used': result.get('tools_used', []),
                    'data_found': len(result.get('accumulated_data', [])),
                    'workflow_status': result.get('workflow_status', 'unknown')
                }
            }
            
            # Add to session history
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
            error_response = f"I encountered an error while processing your question: {str(e)}"
            
            # Add error to session history
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
                    'conversation_id': conversation_id,
                    'execution_time': execution_time,
                    'tools_used': [],
                    'data_found': 0,
                    'workflow_status': 'error',
                    'error': str(e)
                }
            }
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get session history."""
        return self.session_history.copy()
    
    def clear_history(self):
        """Clear session history."""
        self.session_history.clear()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary statistics."""
        if not self.session_history:
            return {
                'total_questions': 0,
                'success_rate': 0.0,
                'average_execution_time': 0.0,
                'successful_queries': 0,
                'failed_queries': 0
            }
        
        successful = [h for h in self.session_history if h['success']]
        total_time = sum(h['execution_time'] for h in self.session_history)
        
        return {
            'total_questions': len(self.session_history),
            'success_rate': len(successful) / len(self.session_history),
            'average_execution_time': total_time / len(self.session_history),
            'successful_queries': len(successful),
            'failed_queries': len(self.session_history) - len(successful)
        }


# Global agent instance
_agent_instance = None


def get_agent() -> ConnectAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ConnectAgent()
    return _agent_instance


# Synchronous wrapper functions for easy use
def ask_sync(question: str, conversation_id: str = None) -> str:
    """
    Synchronous wrapper for asking questions.
    
    Args:
        question: The user's question
        conversation_id: Optional conversation ID
        
    Returns:
        String response
    """
    agent = get_agent()
    return asyncio.run(agent.ask(question, conversation_id))


def ask_detailed_sync(question: str, conversation_id: str = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for detailed questions.
    
    Args:
        question: The user's question
        conversation_id: Optional conversation ID
        
    Returns:
        Detailed response dictionary
    """
    agent = get_agent()
    return asyncio.run(agent.ask_detailed(question, conversation_id))


def batch_ask(questions: List[str], conversation_id: str = None) -> List[str]:
    """
    Ask multiple questions in batch.
    
    Args:
        questions: List of questions to ask
        conversation_id: Optional conversation ID
        
    Returns:
        List of responses
    """
    agent = get_agent()
    
    async def _batch_ask():
        tasks = [agent.ask(q, conversation_id) for q in questions]
        return await asyncio.gather(*tasks)
    
    return asyncio.run(_batch_ask())


def get_session_summary() -> Dict[str, Any]:
    """Get session summary statistics."""
    agent = get_agent()
    return agent.get_session_summary()


def clear_session():
    """Clear session history."""
    agent = get_agent()
    agent.clear_history()


def get_agent_info() -> Dict[str, Any]:
    """Get agent information and capabilities."""
    return {
        'agent_type': 'SimplifiedConnectAgent',
        'version': '1.0.0',
        'capabilities': [
            'Natural language people search',
            'Skill-based queries',
            'Company and location search', 
            'Role-based search',
            'Complex multi-criteria queries'
        ],
        'workflow': 'Linear LangGraph (Planning → Execution → Synthesis)',
        'tools': '24+ MCP tools for Neo4j knowledge graph',
        'data_size': '1,992+ professional profiles'
    }


def print_usage():
    """Print usage information."""
    print("""
Connect Agent - People Knowledge Graph Assistant

Usage:
    python app/agent_run.py                     # Interactive mode
    python app/agent_run.py "your question"    # Single query
    python app/agent_run.py --help             # Show this help

Examples:
    python app/agent_run.py "Find Python developers"
    python app/agent_run.py "Who works at Google?"
    python app/agent_run.py "Find React experts in tech companies"

Interactive mode commands:
    - Type your questions naturally
    - 'summary' - Show session statistics
    - 'clear' - Clear session history  
    - 'quit' or 'exit' - Exit the program
""")


async def interactive_mode():
    """Run interactive mode."""
    agent = get_agent()
    
    print("\n" + "="*60)
    print("🤖 CONNECT AGENT - Interactive Mode")
    print("Ask questions about people in the knowledge graph")
    print("Type 'quit' to exit, 'summary' for stats, 'clear' to reset")
    print("="*60)
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            elif question.lower() == 'summary':
                summary = agent.get_session_summary()
                print(f"\n📊 Session Summary:")
                print(f"   Questions asked: {summary['total_questions']}")
                print(f"   Success rate: {summary['success_rate']:.1%}")
                print(f"   Average time: {summary['average_execution_time']:.2f}s")
                continue
            elif question.lower() == 'clear':
                agent.clear_history()
                print("🧹 Session history cleared")
                continue
            elif not question:
                continue
            
            print("🤖 Thinking...")
            start_time = time.time()
            
            response = await agent.ask(question)
            duration = time.time() - start_time
            
            # Display response
            if len(response) > 300:
                print(f"💬 Response: {response[:300]}...")
                print(f"📄 ({len(response)} characters total)")
            else:
                print(f"💬 Response: {response}")
            
            print(f"⏱️  {duration:.2f}s")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Interactive mode
        asyncio.run(interactive_mode())
    
    elif '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
    
    else:
        # Single query mode
        question = ' '.join(sys.argv[1:])
        
        print(f"🤔 Question: {question}")
        print("🤖 Processing...")
        
        try:
            start_time = time.time()
            response = ask_sync(question)
            duration = time.time() - start_time
            
            print(f"\n💬 Response: {response}")
            print(f"⏱️  Execution time: {duration:.2f}s")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure the MCP server is running: python -m mcp.server")


if __name__ == "__main__":
    main()