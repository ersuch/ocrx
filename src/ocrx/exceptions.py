"""ocrx 异常层次。所有自定义异常都继承自 OcrxError。"""


class OcrxError(Exception):
    """所有 ocrx 异常的基类。"""


class ConfigError(OcrxError):
    """无效配置值。"""


class EngineError(OcrxError):
    """PaddleOCR 引擎初始化或运行时失败。"""


class ImageError(OcrxError):
    """图像加载、解码或处理失败。"""


class FormatError(OcrxError):
    """输出格式化或序列化失败。"""


class ValidationError(OcrxError):
    """输入验证失败（文件不存在、类型错误等）。"""


__all__ = [
    "OcrxError",
    "ConfigError",
    "EngineError",
    "ImageError",
    "FormatError",
    "ValidationError",
]
