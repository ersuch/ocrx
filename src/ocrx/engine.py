"""PaddleOCR 引擎封装。上下文管理器管理模型生命周期。"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from ocrx.config import OCRConfig
from ocrx.exceptions import EngineError, ImageError
from ocrx.models import BBox, OCRResult, TextBlock, TextDirection
from ocrx.utils import validate_image

logger = logging.getLogger(__name__)


class OCREngine:
    """PaddleOCR 检测与识别的上下文管理器封装。

    用法:
        with OCREngine(config) as engine:
            result = engine.run("image.jpg")
    """

    def __init__(self, config: OCRConfig) -> None:
        self._config = config
        self._ocr: Any = None  # PaddleOCR 实例

    def __enter__(self) -> OCREngine:
        self._initialize()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        self.close()

    def _initialize(self) -> None:
        try:
            from paddleocr import PaddleOCR

            logger.info(
                "初始化 PaddleOCR (lang=%s, use_angle_cls=%s)",
                self._config.lang,
                self._config.use_angle_cls,
            )
            self._ocr = PaddleOCR(
                use_angle_cls=self._config.use_angle_cls,
                lang=self._config.lang,
                use_gpu=self._config.use_gpu,
                det_db_thresh=self._config.det_db_thresh,
                det_db_box_thresh=self._config.det_db_box_thresh,
                det_db_unclip_ratio=self._config.det_db_unclip_ratio,
                rec_batch_num=self._config.rec_batch_num,
                drop_score=self._config.drop_score,
                show_log=self._config.verbose,
            )
        except ImportError as exc:
            raise EngineError(
                "无法导入 PaddleOCR，请运行: uv pip install paddlepaddle paddleocr"
            ) from exc
        except Exception as exc:
            raise EngineError(f"初始化 PaddleOCR 引擎失败: {exc}") from exc

    def run(self, image: Union[str, Path, np.ndarray]) -> OCRResult:
        """对单张图片运行 OCR。

        Args:
            image: 文件路径或 numpy 数组。

        Returns:
            OCRResult 包含所有检测到的文本块。
        """
        if self._ocr is None:
            raise EngineError("OCR 引擎未初始化，请使用上下文管理器。")

        if isinstance(image, (str, Path)):
            path = Path(image)
            if not validate_image(path):
                raise ImageError(f"图片不存在或格式不支持: {path}")
            image_input: Union[str, Path] = str(path)
        else:
            path = Path("(numpy array)")
            image_input = image

        try:
            start = time.perf_counter()
            raw = self._ocr.ocr(image_input, cls=self._config.use_angle_cls)
            elapsed = time.perf_counter() - start
        except Exception as exc:
            raise EngineError(f"OCR 处理失败: {exc}") from exc

        return self._parse_result(image_path=path, raw=raw, elapsed=elapsed)

    def _parse_result(
        self,
        image_path: Path,
        raw: List[Any],
        elapsed: float,
    ) -> OCRResult:
        """将 PaddleOCR 原始输出解析为强类型 OCRResult。"""
        blocks: List[TextBlock] = []

        for page in raw:
            for item in page:
                raw_bbox, rec_result = item
                text, confidence = rec_result
                bbox = BBox.from_paddle(raw_bbox)
                block = TextBlock(
                    text=text,
                    confidence=confidence,
                    bbox=bbox,
                )
                blocks.append(block)

        return OCRResult(
            image_path=image_path,
            blocks=blocks,
            language=self._config.lang,
            elapsed_time=elapsed,
        )

    def close(self) -> None:
        if self._ocr is not None:
            logger.debug("释放 OCR 引擎资源")
            self._ocr = None


__all__ = ["OCREngine"]
