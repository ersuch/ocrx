"""OCR 操作的数据模型，为 PaddleOCR 原始输出提供强类型封装。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TextDirection(Enum):
    """文本方向，来自角度分类。"""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BBox:
    """四边形边界框，四点格式 [左上, 右上, 右下, 左下]。"""

    top_left: Tuple[float, float]
    top_right: Tuple[float, float]
    bottom_right: Tuple[float, float]
    bottom_left: Tuple[float, float]

    @classmethod
    def from_paddle(cls, points: List[List[float]]) -> BBox:
        if len(points) != 4:
            raise ValueError(f"PaddleOCR bbox 需要恰好四个点，但收到 {len(points)} 个")
        return cls(
            top_left=(points[0][0], points[0][1]),
            top_right=(points[1][0], points[1][1]),
            bottom_right=(points[2][0], points[2][1]),
            bottom_left=(points[3][0], points[3][1]),
        )

    @property
    def x_min(self) -> float:
        return min(self.top_left[0], self.bottom_left[0])

    @property
    def x_max(self) -> float:
        return max(self.top_right[0], self.bottom_right[0])

    @property
    def y_min(self) -> float:
        return min(self.top_left[1], self.top_right[1])

    @property
    def y_max(self) -> float:
        return max(self.bottom_left[1], self.bottom_right[1])

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_paddle(self) -> List[List[float]]:
        return [
            [self.top_left[0], self.top_left[1]],
            [self.top_right[0], self.top_right[1]],
            [self.bottom_right[0], self.bottom_right[1]],
            [self.bottom_left[0], self.bottom_left[1]],
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "top_left": list(self.top_left),
            "top_right": list(self.top_right),
            "bottom_right": list(self.bottom_right),
            "bottom_left": list(self.bottom_left),
        }


@dataclass
class TextBlock:
    """OCR 检测到的单个文本块。"""

    text: str
    confidence: float
    bbox: BBox
    direction: TextDirection = TextDirection.UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox.to_dict(),
            "direction": self.direction.value,
        }


@dataclass
class OCRResult:
    """单张图片的完整 OCR 结果。"""

    image_path: Path
    blocks: List[TextBlock]
    language: str
    elapsed_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    image_size: Optional[Tuple[int, int]] = None

    @property
    def text(self) -> str:
        return "\n".join(block.text for block in self.blocks)

    @property
    def confidence_mean(self) -> float:
        if not self.blocks:
            return 0.0
        return sum(b.confidence for b in self.blocks) / len(self.blocks)

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_path": str(self.image_path),
            "image_size": list(self.image_size) if self.image_size else None,
            "language": self.language,
            "elapsed_time": round(self.elapsed_time, 3),
            "timestamp": self.timestamp.isoformat(),
            "block_count": self.block_count,
            "confidence_mean": round(self.confidence_mean, 4),
            "blocks": [b.to_dict() for b in self.blocks],
        }


__all__ = [
    "TextDirection",
    "BBox",
    "TextBlock",
    "OCRResult",
]
