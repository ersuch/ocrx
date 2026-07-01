"""ocrx: Pythonic OCR eXtended — 基于 PaddleOCR 的结构化文字识别。

典型用法:
    from ocrx import OCRProcessor, OCRConfig, OutputFormat

    config = OCRConfig(lang="ch", output_format=OutputFormat.JSON)
    with OCRProcessor(config) as processor:
        result = processor.process_file("image.jpg")
        print(result.text)
"""

__version__ = "0.1.0"

from ocrx.config import OCRConfig, OutputFormat
from ocrx.exceptions import (
    ConfigError,
    EngineError,
    FormatError,
    ImageError,
    OcrxError,
    ValidationError,
)
from ocrx.models import BBox, OCRResult, TextBlock, TextDirection
from ocrx.processor import OCRProcessor

__all__ = [
    "__version__",
    "OCRConfig",
    "OutputFormat",
    "OCRResult",
    "TextBlock",
    "BBox",
    "TextDirection",
    "OcrxError",
    "ConfigError",
    "EngineError",
    "ImageError",
    "FormatError",
    "ValidationError",
    "OCRProcessor",
]
