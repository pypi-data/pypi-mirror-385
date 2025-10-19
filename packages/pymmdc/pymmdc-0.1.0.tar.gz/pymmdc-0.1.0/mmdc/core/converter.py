import tempfile
import subprocess
from pathlib import Path
from .exceptions import MermaidCLIError, ConfigurationError, ConversionError
from typing import Optional, Dict, Any, List
from ..utils.simple import logger
from ..utils.file_utils import TemporaryFileManager
from ..core.validator import SystemValidator, MermaidCodeValidator
from ..core.types import ConversionResult, ConversionStatus
from ..processors.markdown import MarkdownMermaidProcessor


class LocalMermaidConverter:
    """
    Converts Mermaid diagrams to PNG using local Mermaid CLI only.
    No web requests - purely local operation.
    """

    # MMDC configuration defaults
    DEFAULT_CONFIG = {
        "width": 1200,
        "height": 800,
        "backgroundColor": "transparent",
        "theme": "default",
    }

    SUPPORTED_THEMES = ["default", "forest", "dark", "neutral"]

    def __init__(
        self,
        mmdc_path: str = "mmdc",
        timeout: int = 60,
        temp_dir: Optional[str] = None,
        validate_system: bool = True,
    ):
        self.mmdc_path = mmdc_path
        self.timeout = timeout
        self.temp_manager = TemporaryFileManager()
        self.validator = SystemValidator()
        self.code_validator = MermaidCodeValidator()
        self.config = self.DEFAULT_CONFIG.copy()

        # System validation
        if validate_system:
            self._validate_environment()

        logger.info("LocalMermaidConverter initialized successfully")

    def _validate_environment(self):
        """Validate that all required dependencies are available."""
        logger.info("Validating system environment...")

        # Check Node.js
        node_ok, node_msg = self.validator.validate_node_js()
        if not node_ok:
            raise ConfigurationError(f"Node.js validation failed: {node_msg}")
        logger.info(node_msg)

        # Check Mermaid CLI
        mmdc_ok, mmdc_msg = self.validator.validate_mermaid_cli()
        if not mmdc_ok:
            raise ConfigurationError(f"Mermaid CLI validation failed: {mmdc_msg}")
        logger.info(mmdc_msg)

        # Check file permissions
        test_dir = Path(tempfile.gettempdir())
        perm_ok, perm_msg = self.validator.validate_file_permissions(test_dir)
        if not perm_ok:
            raise ConfigurationError(f"File permission check failed: {perm_msg}")
        logger.info(perm_msg)

    def set_config(self, **kwargs):
        """Update MMDC configuration parameters."""
        valid_keys = set(self.DEFAULT_CONFIG.keys())
        for key, value in kwargs.items():
            if key in valid_keys:
                self.config[key] = value
            else:
                logger.warning(f"Ignoring invalid config key: {key}")

        # Validate theme
        if "theme" in kwargs and kwargs["theme"] not in self.SUPPORTED_THEMES:
            logger.warning(f"Unsupported theme: {kwargs['theme']}. Using default.")
            self.config["theme"] = "default"

    def convert_to_png(self, mermaid_code: str) -> bytes:
        """
        Convert Mermaid diagram code to PNG bytes.

        Args:
            mermaid_code: Valid Mermaid diagram code

        Returns:
            bytes: PNG image data

        Raises:
            ConversionError: If conversion fails
            MermaidCLIError: If Mermaid CLI execution fails
        """
        logger.info("Starting Mermaid to PNG conversion...")

        try:
            # Validate input
            is_valid, validation_msg = self.code_validator.validate_syntax(mermaid_code)
            if not is_valid:
                raise ConversionError(f"Invalid Mermaid code: {validation_msg}")

            # Sanitize input
            sanitized_code = self.code_validator.sanitize_input(mermaid_code)

            # Create temporary files
            input_file = self.temp_manager.create_temp_file(".mmd", sanitized_code)
            output_file = self.temp_manager.create_temp_file(".png")

            # Build MMDC command
            cmd = self._build_mmdc_command(input_file, output_file)

            logger.debug(f"Executing command: {' '.join(cmd)}")

            # Execute conversion
            result = self._execute_mmdc(cmd)

            # Read output file
            if not output_file.exists():
                raise MermaidCLIError("Output file was not created")

            png_data = output_file.read_bytes()

            if len(png_data) == 0:
                raise MermaidCLIError("Output file is empty")

            logger.info(
                f"Successfully converted Mermaid diagram to PNG ({len(png_data)} bytes)"
            )
            return png_data

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise

    def convert_and_save(self, mermaid_code: str, output_path: str) -> ConversionResult:
        """
        Convert Mermaid diagram and save to file with detailed result reporting.

        Args:
            mermaid_code: Valid Mermaid diagram code
            output_path: Path where PNG file should be saved

        Returns:
            ConversionResult: Detailed result of the conversion
        """
        import time

        start_time = time.time()
        output_file = Path(output_path)

        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Perform conversion
            png_data = self.convert_to_png(mermaid_code)

            # Save to file
            output_file.write_bytes(png_data)
            file_size = output_file.stat().st_size

            execution_time = time.time() - start_time

            logger.info(
                f"Diagram saved to {output_path} ({file_size} bytes, {execution_time:.2f}s)"
            )

            return ConversionResult(
                status=ConversionStatus.SUCCESS,
                output_path=output_file,
                file_size=file_size,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Failed to save diagram to {output_path}: {str(e)}")

            return ConversionResult(
                status=ConversionStatus.FAILED,
                error_message=str(e),
                execution_time=execution_time,
            )

    def _build_mmdc_command(self, input_file: Path, output_file: Path) -> list:
        """Build the MMDC command line arguments."""
        cmd = [
            self.mmdc_path,
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--width",
            str(self.config["width"]),
            "--height",
            str(self.config["height"]),
            "--backgroundColor",
            self.config["backgroundColor"],
            "--theme",
            self.config["theme"],
            "--quiet",  # Reduce verbose output
        ]

        return cmd

    def _execute_mmdc(self, cmd: list) -> subprocess.CompletedProcess:
        """Execute MMDC command with robust error handling."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout, check=True
            )

            if result.stderr:
                logger.warning(f"MMDC stderr: {result.stderr.strip()}")

            return result

        except subprocess.TimeoutExpired as e:
            error_msg = f"MMDC execution timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise MermaidCLIError(error_msg) from e

        except subprocess.CalledProcessError as e:
            error_msg = f"MMDC execution failed with return code {e.returncode}"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            logger.error(error_msg)
            raise MermaidCLIError(error_msg) from e

        except FileNotFoundError as e:
            error_msg = f"MMDC executable not found at '{self.mmdc_path}'"
            logger.error(error_msg)
            raise ConfigurationError(error_msg) from e

    def batch_convert(
        self, mermaid_files: Dict[str, str]
    ) -> Dict[str, ConversionResult]:
        """
        Convert multiple Mermaid files in batch.

        Args:
            mermaid_files: Dictionary mapping output filenames to Mermaid code

        Returns:
            Dictionary mapping filenames to conversion results
        """
        results = {}

        for filename, mermaid_code in mermaid_files.items():
            try:
                result = self.convert_and_save(mermaid_code, filename)
                results[filename] = result
            except Exception as e:
                results[filename] = ConversionResult(
                    status=ConversionStatus.FAILED, error_message=str(e)
                )

        success_count = sum(
            1 for r in results.values() if r.status == ConversionStatus.SUCCESS
        )
        logger.info(
            f"Batch conversion completed: {success_count}/{len(results)} successful"
        )

        return results

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def cleanup(self):
        """Clean up temporary resources."""
        self.temp_manager.cleanup()
        logger.info("Temporary resources cleaned up")


class EnhancedMermaidConverter:
    """
    Enhanced converter that combines local Mermaid conversion with Markdown processing.
    """

    def __init__(self, **converter_kwargs):
        self.base_converter = LocalMermaidConverter(**converter_kwargs)
        self.markdown_processor = MarkdownMermaidProcessor(self.base_converter)

    def convert_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        process_markdown: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Convert input file based on its type.

        Args:
            input_file: Input file path
            output_file: Output file path (optional)
            process_markdown: Whether to process as Markdown file
            **kwargs: Additional options for Markdown processing

        Returns:
            Conversion results
        """
        input_path = Path(input_file)

        # Determine processing mode
        if input_path.suffix.lower() == ".md" or process_markdown:
            return self.markdown_processor.process_markdown_file(
                input_file,
                output_dir=kwargs.get("output_dir"),
                replace_blocks=kwargs.get("replace_blocks", False),
            )
        else:
            # Single Mermaid file conversion
            if output_file is None:
                output_file = input_path.with_suffix(".png")

            with open(input_file, "r", encoding="utf-8") as f:
                mermaid_code = f.read()

            result = self.base_converter.convert_and_save(mermaid_code, output_file)

            return {
                "file": input_file,
                "output_file": output_file,
                "success": result.status.value == "success",
                "error": result.error_message,
                "file_size": result.file_size,
                "execution_time": result.execution_time,
            }

    def batch_convert(self, files: List[str], **kwargs) -> Dict[str, Any]:
        """Convert multiple files with automatic type detection."""
        results = {}

        for file_path in files:
            try:
                path = Path(file_path)
                if path.suffix.lower() == ".md":
                    results[file_path] = self.convert_file(
                        file_path, process_markdown=True, **kwargs
                    )
                else:
                    results[file_path] = self.convert_file(file_path, **kwargs)
            except Exception as e:
                results[file_path] = {"success": False, "error": str(e)}

        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.base_converter.cleanup()
