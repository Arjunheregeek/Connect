"""
Executor Package - SIMPLIFIED VERSION

Uses simplified executor that avoids problematic complexity:
- simple_executor: Basic execution without async context manager issues
"""

# SIMPLIFIED: Import the working simple executor
from .simple_executor import simple_executor_node

# Keep the old imports for backward compatibility but prefer simple version
try:
    from .plan_validator import PlanValidator
    from .tool_executor import ToolExecutor
    from .result_aggregator import ResultAggregator
except ImportError:
    # If complex components fail to import, that's okay
    pass

# Export the simple executor as the main one
# Alias for backward compatibility
tool_executor_node = simple_executor_node

__all__ = [
    'simple_executor_node',
    'tool_executor_node',  # Add this for backward compatibility
    'PlanValidator',
    'ToolExecutor', 
    'ResultAggregator'
]