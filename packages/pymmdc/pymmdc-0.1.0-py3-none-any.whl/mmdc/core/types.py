"""
Type definitions and data classes for PyMMDC.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class ConversionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ConversionResult:
    """Container for conversion results."""

    status: ConversionStatus
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    file_size: int = 0
    execution_time: float = 0.0
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class MermaidBlock:
    """Represents a Mermaid code block found in Markdown."""

    code: str
    line_number: int
    block_index: int
    language: str = "mermaid"
    metadata: Optional[Dict[str, Any]] = None
    source_file: Optional[Path] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessingSummary:
    """Summary of markdown file processing."""

    input_file: Path
    blocks_found: int = 0
    blocks_converted: int = 0
    output_files: List[Path] = None
    total_time: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.errors is None:
            self.errors = []

    @property
    def success_rate(self) -> float:
        if self.blocks_found == 0:
            return 0.0
        return (self.blocks_converted / self.blocks_found) * 100
