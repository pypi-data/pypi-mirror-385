import re
from typing import Any, List, Dict, Optional
import json
from pathlib import Path
from ..utils.simple import logger
from ..core.types import MermaidBlock


class MarkdownMermaidProcessor:
    """
    Processes Markdown files to extract and convert Mermaid code blocks to PNG.
    """

    # Regex pattern to match Mermaid code blocks
    MERMAID_BLOCK_PATTERN = re.compile(
        r"```\s*(mermaid|mmd)\s*(.*?)\n(.*?)```", re.DOTALL | re.IGNORECASE
    )

    def __init__(self, base_converter: Any):
        self.converter = base_converter
        self.blocks_found = 0
        self.blocks_converted = 0

    def extract_mermaid_blocks(self, markdown_content: str) -> List[MermaidBlock]:
        """
        Extract all Mermaid code blocks from Markdown content.

        Args:
            markdown_content: Raw Markdown text

        Returns:
            List of MermaidBlock objects
        """
        blocks = []
        lines = markdown_content.split("\n")

        # Find all code blocks using regex
        for match in self.MERMAID_BLOCK_PATTERN.finditer(markdown_content):
            language = match.group(1).lower()
            metadata_str = match.group(2).strip()
            code_content = match.group(3).strip()

            # Parse metadata (key=value pairs)
            metadata = self._parse_metadata(metadata_str)

            # Calculate approximate line number
            line_number = markdown_content[: match.start()].count("\n") + 1

            block = MermaidBlock(
                code=code_content,
                line_number=line_number,
                block_index=len(blocks),
                language=language,
                metadata=metadata,
            )
            blocks.append(block)

        # Alternative method: line-by-line parsing for better line numbers
        if not blocks:
            blocks.extend(self._extract_blocks_line_by_line(markdown_content))

        self.blocks_found = len(blocks)
        logger.info(f"Found {self.blocks_found} Mermaid code blocks in Markdown")

        return blocks

    def _extract_blocks_line_by_line(self, markdown_content: str) -> List[MermaidBlock]:
        """Alternative extraction method using line-by-line parsing."""
        blocks = []
        lines = markdown_content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check for Mermaid code block start
            if line.startswith("```") and any(
                lang in line.lower() for lang in ["mermaid", "mmd"]
            ):
                # Extract language and metadata
                parts = line[3:].strip().split()
                language = parts[0].lower() if parts else "mermaid"
                metadata_str = " ".join(parts[1:]) if len(parts) > 1 else ""
                metadata = self._parse_metadata(metadata_str)

                # Collect code content until closing backticks
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1

                if code_lines:
                    block = MermaidBlock(
                        code="\n".join(code_lines),
                        line_number=i - len(code_lines),
                        block_index=len(blocks),
                        language=language,
                        metadata=metadata,
                    )
                    blocks.append(block)

            i += 1

        return blocks

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """Parse metadata string into key-value pairs."""
        metadata = {}
        if not metadata_str:
            return metadata

        try:
            # Try JSON format first
            if metadata_str.startswith("{") and metadata_str.endswith("}"):
                return json.loads(metadata_str)

            # Parse key=value pairs
            for pair in metadata_str.split():
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    # Try to convert to appropriate type
                    if value.lower() in ("true", "false"):
                        value = value.lower() == "true"
                    elif value.isdigit():
                        value = int(value)
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    metadata[key.strip()] = value
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse metadata '{metadata_str}': {e}")

        return metadata

    def process_markdown_file(
        self,
        md_file_path: str,
        output_dir: Optional[str] = None,
        replace_blocks: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a Markdown file, convert all Mermaid blocks to PNG.

        Args:
            md_file_path: Path to Markdown file
            output_dir: Directory for PNG outputs (default: same as MD file)
            replace_blocks: Whether to replace code blocks with images in output

        Returns:
            Processing results summary
        """
        md_path = Path(md_file_path)
        if not md_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

        # Set output directory
        if output_dir is None:
            output_dir = md_path.parent
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Read Markdown content
        markdown_content = md_path.read_text(encoding="utf-8")

        # Extract Mermaid blocks
        blocks = self.extract_mermaid_blocks(markdown_content)

        if not blocks:
            logger.warning(f"No Mermaid code blocks found in {md_file_path}")
            return {
                "file": md_file_path,
                "blocks_found": 0,
                "blocks_converted": 0,
                "output_files": [],
            }

        # Convert each block
        results = []
        output_files = []

        for block in blocks:
            try:
                # Generate output filename
                output_filename = self._generate_output_filename(
                    md_path, block, output_path, len(results)
                )

                # Apply block-specific configuration
                self._apply_block_configuration(block)

                # Convert to PNG
                conversion_result = self.converter.convert_and_save(
                    block.code, output_filename
                )

                if conversion_result.status.value == "success":
                    self.blocks_converted += 1
                    output_files.append(str(conversion_result.output_path))
                    logger.info(
                        f"Converted block {block.block_index} to {output_filename}"
                    )
                else:
                    logger.error(
                        f"Failed to convert block {block.block_index}: {conversion_result.error_message}"
                    )

                results.append(
                    {
                        "block_index": block.block_index,
                        "line_number": block.line_number,
                        "output_file": output_filename,
                        "success": conversion_result.status.value == "success",
                        "error": conversion_result.error_message,
                    }
                )

            except Exception as e:
                logger.error(f"Error processing block {block.block_index}: {e}")
                results.append(
                    {
                        "block_index": block.block_index,
                        "line_number": block.line_number,
                        "output_file": None,
                        "success": False,
                        "error": str(e),
                    }
                )

        # Generate summary
        summary = {
            "file": md_file_path,
            "blocks_found": len(blocks),
            "blocks_converted": self.blocks_converted,
            "output_files": output_files,
            "block_results": results,
        }

        # Replace blocks in Markdown if requested
        if replace_blocks and output_files:
            new_content = self._replace_blocks_with_images(
                markdown_content, blocks, output_files
            )
            output_md_path = output_path / f"{md_path.stem}_with_images{md_path.suffix}"
            output_md_path.write_text(new_content, encoding="utf-8")
            summary["modified_markdown"] = str(output_md_path)

        logger.info(
            f"Processed {md_file_path}: {self.blocks_converted}/{len(blocks)} blocks converted"
        )

        return summary

    def _generate_output_filename(
        self, md_path: Path, block: MermaidBlock, output_dir: Path, sequence: int
    ) -> str:
        """Generate output PNG filename for a Mermaid block."""
        base_name = md_path.stem

        # Use metadata title if available
        title = block.metadata.get("title") if block.metadata else None
        if title:
            # Sanitize title for filename
            title_clean = re.sub(r"[^\w\-_\. ]", "_", str(title))
            filename = f"{base_name}_{title_clean}.png"
        else:
            filename = f"{base_name}_diagram_{sequence:02d}.png"

        return str(output_dir / filename)

    def _apply_block_configuration(self, block: MermaidBlock):
        """Apply block-specific configuration to the converter."""
        if not block.metadata:
            return

        config_updates = {}

        # Map metadata to converter configuration
        mapping = {
            "width": "width",
            "height": "height",
            "theme": "theme",
            "bgcolor": "backgroundColor",
        }

        for metadata_key, config_key in mapping.items():
            if metadata_key in block.metadata:
                config_updates[config_key] = block.metadata[metadata_key]

        if config_updates:
            self.converter.set_config(**config_updates)
            logger.debug(f"Applied block configuration: {config_updates}")

    def _replace_blocks_with_images(
        self, markdown_content: str, blocks: List[MermaidBlock], image_files: List[str]
    ) -> str:
        """Replace Mermaid code blocks with image references in Markdown."""
        content = markdown_content
        replacements_made = 0

        for i, block in enumerate(blocks):
            if i < len(image_files) and image_files[i]:
                # Find the exact block in content
                block_pattern = f"```{block.language}{' ' + json.dumps(block.metadata) if block.metadata else ''}\n{block.code}```"

                # Create image markdown
                image_alt = block.metadata.get("title", f"Mermaid Diagram {i}")
                image_markdown = f"![{image_alt}]({Path(image_files[i]).name})"

                # Replace first occurrence
                if block_pattern in content:
                    content = content.replace(block_pattern, image_markdown, 1)
                    replacements_made += 1
                else:
                    # Fallback: use approximate replacement
                    alt_pattern = f"```{block.language}"
                    if alt_pattern in content:
                        # More complex replacement would be needed here
                        logger.warning(
                            f"Could not exactly replace block {i}, using fallback"
                        )

        logger.info(f"Replaced {replacements_made} code blocks with image references")
        return content
