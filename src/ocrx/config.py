"""配置模块。OCRConfig 是所有可配置参数的唯一来源。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from ocrx.exceptions import ConfigError


class OutputFormat(Enum):
    """OCR 输出的序列化格式。"""

    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"


@dataclass
class OCRConfig:
    """OCR 引擎与输出配置，包含内置验证。

    用法:
        config = OCRConfig(lang="ch", drop_score=0.5)
        config.validate()
    """

    # --- PaddleOCR parameters ---
    lang: str = "ch"
    use_gpu: bool = False
    use_angle_cls: bool = True
    det_db_thresh: float = 0.3
    det_db_box_thresh: float = 0.5
    det_db_unclip_ratio: float = 1.6
    rec_batch_num: int = 6
    drop_score: float = 0.5

    # --- Output ---
    output_format: OutputFormat = OutputFormat.JSON
    output_dir: Optional[Path] = None

    # --- Debug ---
    verbose: bool = False

    def validate(self) -> None:
        """验证配置值，不合法时抛出 ConfigError。"""
        if self.drop_score < 0.0 or self.drop_score > 1.0:
            raise ConfigError(
                f"drop_score 必须介于 0 和 1 之间，实际为 {self.drop_score}"
            )
        if self.det_db_thresh < 0.0 or self.det_db_thresh > 1.0:
            raise ConfigError(
                f"det_db_thresh 必须介于 0 和 1 之间，实际为 {self.det_db_thresh}"
            )


__all__ = ["OutputFormat", "OCRConfig"]
