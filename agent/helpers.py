"""
Agent Helper Functions

Convenience functions for common agent operations and utilities.
"""

import asyncio
from typing import List, Dict, Any, Optional
from agent.main_agent import agent


def ask_sync(question: str, conversation_id: Optional[str] = None) -> str:
    """
    Synchronous wrapper for asking questions.
    
    Args:
        question: Your question
        conversation_id: Optional conversation ID
        
    Returns:
        The agent's response
        
    Example:
        >>> from agent import ask_sync
        >>> response = ask_sync("Find React developers")
        >>> print(response)
    """
    
    return asyncio.run(agent.ask(question, conversation_id))


def ask_detailed_sync(question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for detailed questions.
    
    Args:
        question: Your question
        conversation_id: Optional conversation ID
        
    Returns:
        Detailed response dictionary
    """
    
    return asyncio.run(agent.ask_with_details(question, conversation_id))


def batch_ask(questions: List[str], conversation_id: Optional[str] = None) -> List[str]:
    """
    Ask multiple questions and get responses.
    
    Args:
        questions: List of questions to ask
        conversation_id: Optional conversation ID
        
    Returns:
        List of responses in the same order
        
    Example:
        >>> questions = [
        ...     "Find Python developers at Google",
        ...     "Who are the React experts?",
        ...     "Find people at Microsoft"
        ... ]
        >>> responses = batch_ask(questions)
    """
    
    async def _batch_ask():
        tasks = [agent.ask(q, conversation_id) for q in questions]
        return await asyncio.gather(*tasks)
    
    return asyncio.run(_batch_ask())


def get_agent_info() -> Dict[str, Any]:
    """Get comprehensive information about the agent and its capabilities."""
    
    workflow_info = agent.get_workflow_info()
    session_history = agent.get_session_history()
    
    return {
        'agent_type': 'Connect Agent',
        'version': '1.0.0',
        'description': 'Intelligent agent for querying people knowledge graph with cyclical retry logic',
        'capabilities': [
            'Person search by name',
            'Skill-based professional search', 
            'Company employee lookup',
            'Natural language queries',
            'Intelligent retry and re-planning',
            'Quality assessment of results'
        ],
        'workflow_info': workflow_info,
        'session_stats': {
            'total_questions': len(session_history),
            'successful_queries': len([h for h in session_history if h['success']]),
            'average_execution_time': sum(h['execution_time'] for h in session_history) / len(session_history) if session_history else 0,
            'most_used_tools': _get_most_used_tools(session_history)
        }
    }


def _get_most_used_tools(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get statistics on most frequently used tools."""
    
    tool_counts = {}
    
    for entry in history:
        for tool in entry.get('tools_used', []):
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    # Sort by usage count
    sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [{'tool': tool, 'usage_count': count} for tool, count in sorted_tools[:10]]


def clear_session() -> None:
    """Clear the current session history."""
    agent.clear_history()


def get_session_summary() -> Dict[str, Any]:
    """Get a summary of the current session."""
    
    history = agent.get_session_history()
    
    if not history:
        return {
            'total_questions': 0,
            'session_started': None,
            'last_activity': None,
            'success_rate': 0.0,
            'average_execution_time': 0.0
        }
    
    successful = [h for h in history if h['success']]
    
    return {
        'total_questions': len(history),
        'session_started': history[0]['timestamp'] if history else None,
        'last_activity': history[-1]['timestamp'] if history else None,
        'success_rate': len(successful) / len(history) if history else 0.0,
        'average_execution_time': sum(h['execution_time'] for h in history) / len(history),
        'unique_tools_used': len(set(tool for h in history for tool in h.get('tools_used', []))),
        'retry_statistics': {
            'queries_with_retries': len([h for h in history if h['retry_count'] > 1]),
            'average_retry_count': sum(h['retry_count'] for h in history) / len(history),
            'max_retries_used': max((h['retry_count'] for h in history), default=1)
        }
    }