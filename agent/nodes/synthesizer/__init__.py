"""
Synthesizer Package

Modular synthesizer implementation broken down into focused components:
- DataAnalyzer: Analyzes accumulated data to extract patterns and insights
- ResponseGenerator: Generates human-readable responses from analysis
- QualityAssessor: Assesses response quality and provides improvement recommendations
- synthesizer_node: Main orchestrator function for LangGraph
"""

from .data_analyzer import DataAnalyzer
from .response_generator import ResponseGenerator
from .quality_assessor import QualityAssessor
from .synthesizer_node import synthesizer_node

__all__ = [
    'DataAnalyzer',
    'ResponseGenerator',
    'QualityAssessor',
    'synthesizer_node'
]