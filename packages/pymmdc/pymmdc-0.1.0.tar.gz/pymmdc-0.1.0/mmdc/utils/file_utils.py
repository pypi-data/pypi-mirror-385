"""
File utility functions for PyMMDC.
"""

import tempfile
import shutil
from pathlib import Path
from typing import Iterator
from ..core.exceptions import FileSystemError
from ..utils.simple import logger


class TemporaryFileManager:
    """Manages temporary files with proper cleanup."""

    def __init__(self, prefix: str = "pymmdc_"):
        self.temp_files = []
        self.temp_dirs = []
        self.prefix = prefix

    def create_temp_file(self, suffix: str, content: str = "") -> Path:
        """Create a temporary file with the given suffix and content."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=suffix,
                prefix=self.prefix,
                encoding="utf-8",
                delete=False,
            ) as f:
                if content:
                    f.write(content)
                temp_path = Path(f.name)

            self.temp_files.append(temp_path)
            return temp_path

        except (OSError, IOError) as e:
            raise FileSystemError(f"Failed to create temporary file: {str(e)}")

    def create_temp_dir(self) -> Path:
        """Create a temporary directory."""
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix=self.prefix))
            self.temp_dirs.append(temp_dir)
            return temp_dir
        except OSError as e:
            raise FileSystemError(f"Failed to create temporary directory: {str(e)}")

    def cleanup(self):
        """Clean up all temporary files and directories."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError as e:
                logger.warning(f"Failed to delete temporary file {temp_file}: {e}")

        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except OSError as e:
                logger.warning(f"Failed to delete temporary directory {temp_dir}: {e}")

        self.temp_files.clear()
        self.temp_dirs.clear()


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise FileSystemError(f"Failed to create directory {path}: {str(e)}")


def safe_filename(name: str, max_length: int = 255) -> str:
    """Convert string to safe filename."""
    # Replace unsafe characters
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in name)

    # Remove extra spaces and underscores
    safe_name = "_".join(filter(None, safe_name.split()))

    # Trim to max length
    if len(safe_name) > max_length:
        name_hash = str(hash(safe_name))[-8:]
        safe_name = safe_name[: max_length - 9] + "_" + name_hash

    return safe_name


def find_files(pattern: str, recursive: bool = True) -> Iterator[Path]:
    """Find files matching pattern."""
    path = Path(pattern)

    if path.exists() and path.is_file():
        yield path
        return

    # Handle glob patterns
    if recursive:
        yield from Path(".").rglob(pattern)
    else:
        yield from Path(".").glob(pattern)
