import subprocess
from typing import Tuple
from pathlib import Path
from typing import Tuple, List, Optional
from .types import MermaidBlock


class SystemValidator:
    """Validates system requirements and dependencies."""

    @staticmethod
    def validate_node_js() -> Tuple[bool, str]:
        """Check if Node.js is available and meets version requirements."""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return False, "Node.js not found or not executable"

            version_str = result.stdout.strip()
            # Extract version numbers (v14.0.0 -> [14, 0, 0])
            version_parts = version_str.lstrip("v").split(".")
            major_version = int(version_parts[0])

            if major_version < 14:
                return False, f"Node.js version {version_str} is too old. Required: 14+"

            return True, f"Node.js {version_str} detected"

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Node.js check failed: {str(e)}"

    @staticmethod
    def validate_mermaid_cli() -> Tuple[bool, str]:
        """Check if Mermaid CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["mmdc", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, "Mermaid CLI detected"
            else:
                return False, "Mermaid CLI not properly installed"

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Mermaid CLI check failed: {str(e)}"

    @staticmethod
    def validate_file_permissions(temp_dir: Path) -> Tuple[bool, str]:
        """Validate write permissions in temporary directory."""
        try:
            test_file = temp_dir / "permission_test.txt"
            test_file.write_text("test")
            test_file.unlink()
            return True, "Write permissions verified"
        except (OSError, IOError) as e:
            return False, f"Insufficient permissions: {str(e)}"


class MermaidCodeValidator:
    """Validates Mermaid diagram syntax and content."""

    SUPPORTED_DIAGRAM_TYPES = {
        "graph",
        "flowchart",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "stateDiagram-v2",
        "erDiagram",
        "journey",
        "gantt",
        "pie",
        "quadrantChart",
        "requirementDiagram",
    }

    @classmethod
    def validate_syntax(cls, mermaid_code: str) -> Tuple[bool, str]:
        """
        Perform basic Mermaid syntax validation.
        """
        if not mermaid_code or not mermaid_code.strip():
            return False, "Mermaid code is empty"

        code = mermaid_code.strip()

        # Check for minimum length
        if len(code) < 10:
            return False, "Mermaid code appears too short to be valid"

        # Check for diagram type declaration
        first_line = code.split("\n")[0].strip().lower()
        has_diagram_type = any(
            first_line.lower().startswith(diagram_type.lower())
            for diagram_type in cls.SUPPORTED_DIAGRAM_TYPES
        )

        if not has_diagram_type:
            return False, (
                f"Missing or unsupported diagram type. "
                f"Supported types: {', '.join(sorted(cls.SUPPORTED_DIAGRAM_TYPES))}"
                f"Got: \033[1;93m{first_line}\033[0m"
            )

        # Check for basic structure (at least some content)
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        if len(lines) < 2:
            return False, "Insufficient diagram content"

        return True, "Syntax appears valid"

    @staticmethod
    def sanitize_input(mermaid_code: str) -> str:
        """Remove potential harmful characters and normalize line endings."""
        # Normalize line endings
        normalized = mermaid_code.replace("\r\n", "\n").replace("\r", "\n")

        # Remove null characters and other problematic sequences
        sanitized = "".join(
            char for char in normalized if ord(char) >= 32 or char == "\n"
        )

        return sanitized

    @classmethod
    def validate_block(cls, block: MermaidBlock) -> List[str]:
        """Validate a Mermaid block and return list of warnings."""
        warnings = []

        # Validate code syntax
        is_valid, message = cls.validate_syntax(block.code)
        if not is_valid:
            warnings.append(f"Syntax warning: {message}")

        # Validate metadata
        if block.metadata:
            warnings.extend(cls._validate_metadata(block.metadata))

        return warnings

    @staticmethod
    def _validate_metadata(metadata: dict) -> List[str]:
        """Validate metadata and return warnings."""
        warnings = []

        valid_keys = {"title", "width", "height", "theme", "bgcolor", "background"}
        for key in metadata:
            if key not in valid_keys:
                warnings.append(f"Unknown metadata key: {key}")

        # Validate numeric values
        for key in ["width", "height"]:
            if key in metadata:
                try:
                    value = int(metadata[key])
                    if value <= 0:
                        warnings.append(f"{key} should be positive, got {value}")
                except (ValueError, TypeError):
                    warnings.append(f"{key} should be numeric, got {metadata[key]}")

        return warnings
