"""
Shared utilities for workflow nodes.

This module contains common utilities and helper functions used across
multiple workflow nodes to avoid code duplication and ensure consistency.
"""

import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from agent.state import AgentState, WorkflowStatus


class NodeUtils:
    """
    Common utility functions for workflow nodes.
    """
    
    @staticmethod
    def log_node_execution(node_name: str, state: AgentState, execution_time: float = None) -> None:
        """
        Log node execution for debugging and monitoring.
        
        Args:
            node_name: Name of the node being executed
            state: Current agent state
            execution_time: Time taken for execution (optional)
        """
        
        log_entry = {
            'node': node_name,
            'timestamp': datetime.now(),
            'conversation_id': state['conversation_id'],
            'workflow_status': state['workflow_status'],
            'execution_time': execution_time
        }
        
        # Add to debug info if it exists
        if 'debug_info' not in state:
            state['debug_info'] = {}
        
        if 'execution_log' not in state['debug_info']:
            state['debug_info']['execution_log'] = []
        
        state['debug_info']['execution_log'].append(log_entry)
    
    @staticmethod
    def validate_state_requirements(state: AgentState, required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate that the state contains required fields for a node.
        
        Args:
            state: Current agent state
            required_fields: List of required field names
            
        Returns:
            Validation result with status and missing fields
        """
        
        missing_fields = []
        for field in required_fields:
            if field not in state:
                missing_fields.append(field)
        
        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'state_keys': list(state.keys())
        }
    
    @staticmethod
    def extract_query_entities(query: str) -> Dict[str, List[str]]:
        """
        Extract entities from a query string.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with extracted entities by type
        """
        
        entities = {
            'names': [],
            'skills': [],
            'companies': [],
            'locations': []
        }
        
        # Common skill patterns
        skill_patterns = [
            r'\b(python|javascript|java|react|node\.?js|sql|aws|docker|kubernetes)\b',
            r'\b(machine learning|ai|data science|web development|backend|frontend)\b',
            r'\b(angular|vue|flask|django|spring|laravel)\b'
        ]
        
        query_lower = query.lower()
        
        # Extract skills
        for pattern in skill_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            entities['skills'].extend(matches)
        
        # Extract potential names (capitalized words)
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, query)
        entities['names'].extend(potential_names)
        
        # Extract potential companies (look for "at Company" patterns)
        company_pattern = r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        companies = re.findall(company_pattern, query)
        entities['companies'].extend(companies)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    @staticmethod
    def format_execution_time(seconds: float) -> str:
        """
        Format execution time in a human-readable way.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """
        Truncate text to a maximum length with ellipsis.
        
        Args:
            text: Text to truncate
            max_length: Maximum length allowed
            
        Returns:
            Truncated text with ellipsis if needed
        """
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    @staticmethod
    def count_data_items(data: Any) -> int:
        """
        Count the number of data items in various data structures.
        
        Args:
            data: Data to count (can be list, dict, string, etc.)
            
        Returns:
            Number of items
        """
        
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data)
        elif isinstance(data, str):
            return 1 if data.strip() else 0
        elif data is None:
            return 0
        else:
            return 1


class ErrorHandler:
    """
    Common error handling utilities for workflow nodes.
    """
    
    @staticmethod
    def create_error_response(error_type: str, message: str, state: AgentState, context: Dict[str, Any] = None) -> AgentState:
        """
        Create a standardized error response.
        
        Args:
            error_type: Type of error
            message: Error message
            state: Current agent state
            context: Additional error context
            
        Returns:
            Updated state with error information
        """
        
        from agent.state import StateManager
        
        error_state = StateManager.add_error(state, error_type, message, context)
        
        # Add fallback response if no final response exists
        if 'final_response' not in error_state:
            error_state['final_response'] = f"I apologize, but I encountered an error while processing your request: {message}. Please try again or rephrase your question."
        
        return error_state
    
    @staticmethod
    def handle_node_exception(node_name: str, exception: Exception, state: AgentState) -> AgentState:
        """
        Handle exceptions that occur during node execution.
        
        Args:
            node_name: Name of the node where exception occurred
            exception: The exception that was raised
            state: Current agent state
            
        Returns:
            Updated state with error handling
        """
        
        error_context = {
            'node': node_name,
            'exception_type': type(exception).__name__,
            'timestamp': datetime.now(),
            'query': state.get('user_query', 'Unknown')
        }
        
        return ErrorHandler.create_error_response(
            f'{node_name}_exception',
            f"Unexpected error in {node_name}: {str(exception)}",
            state,
            error_context
        )


class PerformanceMonitor:
    """
    Performance monitoring utilities for workflow nodes.
    """
    
    @staticmethod
    def create_timer():
        """Create a simple timer context manager."""
        
        class Timer:
            def __init__(self):
                self.start_time = None
                self.end_time = None
                self.elapsed = None
            
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.end_time = time.time()
                self.elapsed = self.end_time - self.start_time
        
        return Timer()
    
    @staticmethod
    def add_performance_metrics(state: AgentState, node_name: str, metrics: Dict[str, Any]) -> AgentState:
        """
        Add performance metrics to the state.
        
        Args:
            state: Current agent state
            node_name: Name of the node
            metrics: Performance metrics to add
            
        Returns:
            Updated state with performance metrics
        """
        
        if 'execution_metrics' not in state:
            state['execution_metrics'] = {}
        
        if 'node_performance' not in state['execution_metrics']:
            state['execution_metrics']['node_performance'] = {}
        
        state['execution_metrics']['node_performance'][node_name] = {
            'timestamp': datetime.now(),
            **metrics
        }
        
        return state