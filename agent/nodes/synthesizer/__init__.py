"""
Synthesizer Package - ENHANCED VERSION

Exports the enhanced synthesizer:
- enhanced_synthesizer_node: Complete profile fetching + GPT-4o response generation
"""

from .enhanced_synthesizer_node import enhanced_synthesizer_node

# Export as default
synthesizer_node = enhanced_synthesizer_node

__all__ = [
    'enhanced_synthesizer_node',
    'synthesizer_node'  # Backward compatibility
]
