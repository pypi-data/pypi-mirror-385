class ConversionError(Exception):
    """Base exception for Mermaid conversion errors."""

    pass


class MermaidCLIError(ConversionError):
    """Raised when Mermaid CLI execution fails."""

    pass


class ConfigurationError(ConversionError):
    """Raised when system configuration is invalid."""

    pass


"""
Custom exceptions for PyMMDC.
"""


class PyMMDCError(Exception):
    """Base exception for all PyMMDC errors."""

    pass


class ConversionError(PyMMDCError):
    """Base exception for Mermaid conversion errors."""

    pass


class ValidationError(PyMMDCError):
    """Raised when input validation fails."""

    pass


class FileSystemError(PyMMDCError):
    """Raised when file system operations fail."""

    pass


class MarkdownProcessingError(PyMMDCError):
    """Raised when Markdown processing fails."""

    pass


class BlockProcessingError(MarkdownProcessingError):
    """Raised when individual block processing fails."""

    def __init__(self, block_index: int, line_number: int, message: str):
        self.block_index = block_index
        self.line_number = line_number
        super().__init__(f"Block {block_index} (line {line_number}): {message}")
