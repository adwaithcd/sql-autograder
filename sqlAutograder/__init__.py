"""
SQL Autograder - LLM-based SQL grading system using Google Gemini API.
"""

from .config import get_gemini_config, get_grading_config, get_ollama_config
from .grader import GeminiGrader
from .ollama_grader import OllamaGrader
from .data_loader import SubmissionLoader
from .results import ResultsProcessor
from .statistics import GradingStatistics
from .visualizations import GradingVisualizer

__version__ = "1.0.0"

__all__ = [
    'get_gemini_config',
    'get_grading_config',
    'get_ollama_config',
    'GeminiGrader',
    'OllamaGrader',
    'SubmissionLoader',
    'ResultsProcessor',
    'GradingStatistics',
    'GradingVisualizer'
]