"""
CodeComplexity - A Python library for analyzing code complexity metrics
"""

__version__ = "0.1.1"

from .analyzer import (
    analyze_code,
    analyze_file,
    format_report,
    ComplexityMetrics,
    ComplexityAnalyzer,
)

__all__ = [
    "analyze_code",
    "analyze_file",
    "format_report",
    "ComplexityMetrics",
    "ComplexityAnalyzer",
]