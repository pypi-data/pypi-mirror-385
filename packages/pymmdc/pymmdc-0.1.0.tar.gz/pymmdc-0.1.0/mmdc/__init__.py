"""
PyMMDC - Pure Python Mermaid Diagram Converter

A robust, local-only Mermaid to PNG converter with Markdown processing support.
"""

__version__ = "0.1.0"
__author__ = "PyMMDC Team"
__description__ = "Pure Python Mermaid Diagram Converter with robust error handling"

from .core.converter import LocalMermaidConverter, EnhancedMermaidConverter
from .processors.markdown import MarkdownMermaidProcessor
from .core.exceptions import ConversionError, MermaidCLIError, ConfigurationError
from .cli import main

__all__ = [
    "LocalMermaidConverter",
    "EnhancedMermaidConverter",
    "MarkdownMermaidProcessor",
    "ConversionError",
    "MermaidCLIError",
    "ConfigurationError",
]
