"""
Local Mermaid to PNG Converter with robust error handling and validation.

Usage:
    converter = LocalMermaidConverter()
    png_data = converter.convert_to_png(mermaid_code)
    converter.save_to_file(mermaid_code, "diagram.png")
"""

import argparse
from pathlib import Path
from .core.converter import EnhancedMermaidConverter


# Update the main CLI to support Markdown processing


def main():
    parser = argparse.ArgumentParser(
        description="Convert Mermaid diagrams to PNG with Markdown file support"
    )
    parser.add_argument(
        "input", help="Input file (.mmd, .mermaid, or .md for Markdown files)"
    )
    parser.add_argument(
        "output", nargs="?", help="Output file or directory (optional for Markdown)"
    )

    # Mermaid conversion options
    parser.add_argument(
        "--timeout", type=int, default=60, help="Conversion timeout in seconds"
    )
    parser.add_argument("--width", type=int, default=6400, help="Diagram width")
    parser.add_argument("--height", type=int, default=3200, help="Diagram height")
    parser.add_argument(
        "--theme",
        default="default",
        choices=["default", "forest", "dark", "neutral"],
        help="Diagram theme",
    )
    parser.add_argument(
        "-bg",
        "--background",
        default="transparent",
        help="Diagram theme",
    )
    # Markdown processing options
    parser.add_argument(
        "--process-markdown",
        action="store_true",
        help="Force Markdown processing (for .md files)",
    )
    parser.add_argument("--output-dir", help="Output directory for Markdown images")
    parser.add_argument(
        "--replace-blocks",
        action="store_true",
        help="Replace Mermaid blocks with images in output Markdown",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process multiple files (input can be glob pattern)",
    )

    args = parser.parse_args()

    converter = None

    try:
        # Create enhanced converter
        converter = EnhancedMermaidConverter(timeout=args.timeout)
        converter.base_converter.set_config(
            width=args.width,
            height=args.height,
            theme=args.theme,
            backgroundColor=args.background,
        )
        # Handle batch processing
        if args.batch:
            import glob

            files = glob.glob(args.input)
            results = converter.batch_convert(
                files,
                output_dir=args.output_dir,
                replace_blocks=args.replace_blocks,
            )

            # Print summary
            successful = sum(
                1
                for r in results.values()
                if r.get("success", False) or r.get("blocks_converted", 0) > 0
            )
            print(
                f"Batch processing complete: {successful}/{len(results)} files processed successfully"
            )

            for file_path, result in results.items():
                status = (
                    "✓"
                    if result.get("success", False)
                    or result.get("blocks_converted", 0) > 0
                    else "✗"
                )
                print(f"  {status} {file_path}")

        else:
            # Single file processing
            result = converter.convert_file(
                args.input,
                args.output,
                process_markdown=args.process_markdown
                or Path(args.input).suffix.lower() == ".md",
                output_dir=args.output_dir,
                replace_blocks=args.replace_blocks,
            )

            if "blocks_found" in result:
                # Markdown processing result
                print(f"Markdown Processing: {args.input}")
                print(f"  Blocks found: {result['blocks_found']}")
                print(f"  Blocks converted: {result['blocks_converted']}")
                if result.get("modified_markdown"):
                    print(f"  Modified Markdown: {result['modified_markdown']}")
            else:
                # Single file result
                if result.get("success"):
                    print(f"✓ Successfully converted to {result['output_file']}")
                    print(f"  File size: {result.get('file_size', 0)} bytes")
                    print(f"  Time: {result.get('execution_time', 0):.2f}s")
                else:
                    print(
                        f"✗ Conversion failed: {result.get('error', 'Unknown error')}"
                    )

    except KeyboardInterrupt:
        print("\nConversion cancelled by user")
    except Exception as e:
        print(f"\033[33m✗ Fatal error: \033[31m{e}\033[0m")
    finally:
        if converter:
            converter.base_converter.cleanup()


if __name__ == "__main__":
    main()
