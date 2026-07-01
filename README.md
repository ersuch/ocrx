# ocrx

**Pythonic OCR eXtended** — 基于 PaddleOCR 的结构化文字识别工具。

`ocrx` 对 PaddleOCR 原始输出进行强类型封装和编排，提供一致的命令行和 Python API。引擎可替换，输出格式可定制，适合集成到自动化流程中。

## 特性

- **强类型数据模型** — `BBox` / `TextBlock` / `OCRResult` frozen dataclass，类型安全
- **上下文管理器** — `OCREngine` / `OCRProcessor` 自动管理引擎生命周期
- **多种输出格式** — JSON / 纯文本 / 结构化（含按置信度排序的元信息）
- **Click CLI** — `ocrx scan` 命令，支持批量处理和文件输出
- **可配置** — 语言、置信度阈值、方向分类、检测参数等均可调

## 安装

### 前置条件

Python 3.12+，已全局安装 PaddleOCR 依赖：

```bash
pip3 install paddlepaddle paddleocr
```

### 安装 ocrx

```bash
# 全局安装（可编辑模式，修改源码后即时生效）
pip3 install -e . --no-deps
```

> `--no-deps` 跳过 pip 重新安装 paddlepaddle / paddleocr，使用全局已有的版本。

### 卸载

```bash
pip3 uninstall ocrx -y
```

## 快速开始

```bash
# 单张图片 OCR
ocrx scan tests/data/test_image.png

# 指定语言和输出格式
ocrx --lang en scan document.jpg -f text

# 输出到文件
ocrx scan receipt.png -o result.json

# 详细日志
ocrx --verbose scan page.jpg
```

## CLI 使用

```
Usage: ocrx [OPTIONS] COMMAND [ARGS]...

  ocrx: Pythonic OCR eXtended — 基于 PaddleOCR 的结构化文字识别工具。

Options:
  --verbose                启用 DEBUG 级别日志。
  --lang TEXT              OCR 语言代码 (ch/en/...)。  [default: ch]
  --drop-score FLOAT       置信度阈值，低于此值的块将被丢弃。  [default: 0.5]
  --use-angle-cls / --no-angle-cls
                          启用或禁用文本方向分类。  [default: True]
  --help                   Show this message and exit.

Commands:
  scan  对单张图片运行 OCR 文字识别。
```

### scan 子命令

```
Usage: ocrx scan [OPTIONS] IMAGE

  IMAGE 是图片文件路径，支持 PNG / JPG / BMP / TIFF / WEBP 格式。

Options:
  -f, --format [json|text|structured]  输出格式。  [default: json]
  -o, --output PATH                    输出文件路径（默认输出到 stdout）。
  --help                                Show this message and exit.
```

## Python API

```python
from ocrx import OCRProcessor, OCRConfig, OutputFormat

config = OCRConfig(lang="ch", output_format=OutputFormat.JSON)
with OCRProcessor(config) as processor:
    result = processor.process_file("image.jpg")
    print(result.text)              # 所有文本，换行拼接
    print(result.block_count)       # 文本块数量
    print(result.confidence_mean)   # 平均置信度

    # 遍历文本块
    for block in result.blocks:
        print(f"{block.text} ({block.confidence:.2f}) at {block.bbox}")
```

### 数据模型

```python
from ocrx import BBox, TextBlock, OCRResult, TextDirection

# 四点边界框
bbox = BBox(top_left=(0, 0), top_right=(10, 0),
            bottom_right=(10, 10), bottom_left=(0, 10))

# 文本块
block = TextBlock(text="hello", confidence=0.95, bbox=bbox, direction=TextDirection.HORIZONTAL)

# 完整结果
result = OCRResult(
    image_path="test.png",
    blocks=[block],
    language="en",
    elapsed_time=0.5,
)
```

## 配置

`OCRConfig` 支持以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lang` | `str` | `"ch"` | OCR 语言代码 |
| `use_gpu` | `bool` | `False` | 是否启用 GPU |
| `use_angle_cls` | `bool` | `True` | 文本方向分类 |
| `drop_score` | `float` | `0.5` | 置信度阈值 [0, 1] |
| `det_db_thresh` | `float` | `0.3` | 检测阈值 [0, 1] |
| `det_db_box_thresh` | `float` | `0.5` | 检测框阈值 |
| `det_db_unclip_ratio` | `float` | `1.6` | 检测框扩张比例 |
| `rec_batch_num` | `int` | `6` | 识别批大小 |
| `output_format` | `OutputFormat` | `JSON` | 输出格式 |
| `output_dir` | `Optional[Path]` | `None` | 输出目录 |
| `verbose` | `bool` | `False` | DEBUG 日志 |

## 输出格式示例

### JSON

```json
{
  "image_path": "test_image.png",
  "language": "ch",
  "elapsed_time": 0.333,
  "block_count": 2,
  "confidence_mean": 0.9284,
  "blocks": [
    {
      "text": "Hello OCR World",
      "confidence": 0.991,
      "bbox": {
        "top_left": [19.0, 20.0],
        "top_right": [99.0, 20.0],
        "bottom_right": [99.0, 34.0],
        "bottom_left": [19.0, 34.0]
      },
      "direction": "unknown"
    }
  ]
}
```

### 纯文本

```
Hello OCR World
OCR图
```

### Structured（含元信息）

与 JSON 相同，但附加 `_meta.blocks_sorted_by_confidence` 字段。

## 项目结构

```
src/ocrx/
├── __init__.py      # 公开 API 入口
├── __main__.py      # python -m ocrx 支持
├── cli.py           # Click 命令行接口
├── config.py        # OCRConfig / OutputFormat 配置
├── engine.py        # PaddleOCR 引擎封装
├── exceptions.py    # 异常层次
├── formatter.py     # 结果序列化
├── models.py        # 数据模型 (BBox, TextBlock, OCRResult)
├── processor.py     # 编排器 (验证 → OCR → 格式化 → 输出)
└── utils.py         # 日志与图片验证工具
tests/
├── test_formatter.py
├── test_models.py
└── test_processor.py
```

## 开发

### 修改源码后

`pip3 install -e .` 是可编辑模式，源码改完即时生效，**不需要重新安装**。

如果修改了 `pyproject.toml`（如新增依赖），才需要：

```bash
pip3 install -e . --no-deps
# 然后单独安装新增的依赖
pip3 install <新依赖>
```

### 运行测试

```bash
pip3 install pytest
pytest

# 查看覆盖率
pytest --cov=ocrx

# 单张图片端到端测试
ocrx scan tests/data/test_image.png
```

## License

MIT
