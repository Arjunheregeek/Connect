"""
Synthesizer Package - SIMPLIFIED VERSION

Uses simplified synthesizer that avoids problematic complexity:
- simple_synthesizer: Basic response generation without quality assessment
"""

# SIMPLIFIED: Import the working simple synthesizer
from .simple_synthesizer import simple_synthesizer_node

# Keep the old imports for backward compatibility but prefer simple version
try:
    from .data_analyzer import DataAnalyzer
    from .response_generator import ResponseGenerator
    from .quality_assessor import QualityAssessor
    from .synthesizer_node import synthesizer_node
except ImportError:
    # If complex components fail to import, that's okay
    pass

# Export the simple synthesizer as the main one
synthesizer_node = simple_synthesizer_node

__all__ = [
    'simple_synthesizer_node',
    'synthesizer_node'  # Backward compatibility
]

__all__ = [
    'DataAnalyzer',
    'ResponseGenerator',
    'QualityAssessor',
    'synthesizer_node'
]