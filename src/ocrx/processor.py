"""OCR 处理编排器。统筹验证 → OCR → 格式化 → 输出。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Union

from ocrx.config import OCRConfig, OutputFormat
from ocrx.engine import OCREngine
from ocrx.exceptions import OcrxError, ValidationError
from ocrx.formatter import ResultFormatter
from ocrx.models import OCRResult
from ocrx.utils import setup_logging, validate_image

logger = logging.getLogger(__name__)


class OCRProcessor:
    """端到端 OCR 处理器。上下文管理器，管理引擎生命周期。

    用法:
        with OCRProcessor(config) as processor:
            result = processor.process_file("image.jpg")
            processor.save_result(result)
    """

    def __init__(self, config: OCRConfig) -> None:
        self._config = config
        self._engine: Optional[OCREngine] = None

        if config.verbose:
            setup_logging(verbose=True)

    def __enter__(self) -> OCRProcessor:
        self._engine = OCREngine(self._config).__enter__()
        return self

    def __exit__(self, *args) -> None:
        if self._engine is not None:
            self._engine.__exit__(*args)

    def process_file(self, image_path: Union[str, Path]) -> OCRResult:
        """对单张图片运行 OCR。

        Args:
            image_path: 图片文件路径。

        Returns:
            OCRResult 包含检测到的所有文本块。
        """
        path = Path(image_path)
        if not validate_image(path):
            raise ValidationError(f"图片不存在或格式不支持: {path}")

        if self._engine is None:
            raise OcrxError("处理器未初始化，请使用上下文管理器。")

        logger.info("处理图片: %s", path)
        return self._engine.run(path)

    def process_batch(self, paths: List[Union[str, Path]]) -> List[OCRResult]:
        return [self.process_file(p) for p in paths]

    def save_result(self, result: OCRResult) -> Optional[Path]:
        """根据配置输出 OCR 结果。output_dir 为 None 时输出到 stdout。"""
        if self._config.output_dir is None:
            output = ResultFormatter.serialize(result, self._config.output_format)
            print(output)
            return None

        output_dir = self._config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        fmt = self._config.output_format
        suffix = ".json" if fmt == OutputFormat.JSON else ".txt"
        output_path = output_dir / f"{result.image_path.stem}_ocr{suffix}"

        ResultFormatter.write(result, output_path, fmt)
        logger.info("结果已保存至 %s", output_path)
        return output_path


__all__ = ["OCRProcessor"]
