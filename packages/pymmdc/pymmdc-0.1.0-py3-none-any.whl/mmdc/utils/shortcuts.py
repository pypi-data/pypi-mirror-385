from ..core.converter import LocalMermaidConverter
from ..utils.simple import logger
from ..core.types import ConversionStatus


# Convenience functions
def create_mermaid_converter(**kwargs) -> LocalMermaidConverter:
    """Factory function to create a configured Mermaid converter."""
    return LocalMermaidConverter(**kwargs)


def quick_convert(mermaid_code: str, output_file: str, **kwargs) -> bool:
    """
    Quick conversion utility for simple use cases.

    Returns:
        bool: True if conversion was successful
    """
    converter = LocalMermaidConverter(**kwargs)
    try:
        result = converter.convert_and_save(mermaid_code, output_file)
        return result.status == ConversionStatus.SUCCESS
    except Exception as e:
        logger.error(f"Quick conversion failed: {e}")
        return False
    finally:
        converter.cleanup()
