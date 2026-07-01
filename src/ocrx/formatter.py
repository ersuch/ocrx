"""OCR 结果格式化。无状态函数，用于序列化为 JSON / 文本 / 结构化字典。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ocrx.config import OutputFormat
from ocrx.exceptions import FormatError
from ocrx.models import OCRResult


class ResultFormatter:
    """OCRResult 序列化器。所有方法均为无状态的 static method。"""

    @staticmethod
    def to_json(result: OCRResult, indent: int = 2) -> str:
        try:
            return json.dumps(result.to_dict(), indent=indent, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise FormatError(f"JSON 序列化失败: {exc}") from exc

    @staticmethod
    def to_text(result: OCRResult) -> str:
        return result.text

    @staticmethod
    def to_structured(result: OCRResult) -> Dict[str, Any]:
        return {
            **result.to_dict(),
            "_meta": {
                "blocks_sorted_by_confidence": sorted(
                    [b.to_dict() for b in result.blocks],
                    key=lambda b: b["confidence"],
                    reverse=True,
                ),
            },
        }

    @staticmethod
    def serialize(result: OCRResult, fmt: OutputFormat) -> str:
        mapping = {
            OutputFormat.JSON: ResultFormatter.to_json,
            OutputFormat.TEXT: ResultFormatter.to_text,
            OutputFormat.STRUCTURED: lambda r: json.dumps(
                ResultFormatter.to_structured(r), indent=2, ensure_ascii=False
            ),
        }
        formatter = mapping.get(fmt)
        if formatter is None:
            raise FormatError(f"不支持的输出格式: {fmt}")
        return formatter(result)

    @staticmethod
    def write(result: OCRResult, path: Path, fmt: OutputFormat) -> Path:
        content = ResultFormatter.serialize(result, fmt)
        try:
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise FormatError(f"写入输出文件失败 {path}: {exc}") from exc
        return path


__all__ = ["ResultFormatter"]
