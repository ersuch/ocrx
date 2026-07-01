"""共享工具函数：日志配置、图片验证。"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Set, Union

# 支持的图片格式
IMAGE_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp",
}

logger = logging.getLogger("ocrx")


def setup_logging(verbose: bool = False) -> None:
    """配置 ocrx 日志。默认为 INFO，verbose 时切换为 DEBUG。"""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(handler)
    logger.setLevel(level)
    # 防止重复添加
    logger.propagate = False


def validate_image(path: Union[str, Path]) -> bool:
    """检查路径是否指向一个可用的图片文件。"""
    p = Path(path)
    return p.exists() and p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS


__all__ = [
    "setup_logging",
    "validate_image",
    "IMAGE_EXTENSIONS",
]
