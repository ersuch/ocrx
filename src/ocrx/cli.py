"""Click CLI 入口。定义 ocrx 命令行工具。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from ocrx.config import OCRConfig, OutputFormat
from ocrx.exceptions import OcrxError
from ocrx.processor import OCRProcessor


@click.group()
@click.option("--verbose", is_flag=True, help="启用 DEBUG 级别日志。")
@click.option("--lang", default="ch", show_default=True, help="OCR 语言代码 (ch/en/...)。")
@click.option(
    "--drop-score",
    default=0.5,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="置信度阈值，低于此值的块将被丢弃。",
)
@click.option(
    "--use-angle-cls/--no-angle-cls",
    default=True,
    help="启用或禁用文本方向分类。",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    lang: str,
    drop_score: float,
    use_angle_cls: bool,
) -> None:
    """ocrx: Pythonic OCR eXtended — 基于 PaddleOCR 的结构化文字识别工具。

    支持中文和英文文本检测与识别，输出 JSON / 纯文本 / 结构化格式。
    """
    ctx.ensure_object(dict)
    config = OCRConfig(
        lang=lang,
        verbose=verbose,
        drop_score=drop_score,
        use_angle_cls=use_angle_cls,
    )
    config.validate()
    ctx.obj["config"] = config


@cli.command()
@click.argument("image", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "-f",
    "--format",
    "output_fmt",
    type=click.Choice([f.value for f in OutputFormat], case_sensitive=False),
    default="json",
    show_default=True,
    help="输出格式。",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="输出文件路径（默认输出到 stdout）。",
)
@click.pass_context
def scan(
    ctx: click.Context,
    image: Path,
    output_fmt: str,
    output: Optional[Path],
) -> None:
    """对单张图片运行 OCR 文字识别。

    IMAGE 是图片文件路径，支持 PNG / JPG / BMP / TIFF / WEBP 格式。
    """
    config: OCRConfig = ctx.obj["config"]
    config.output_format = OutputFormat(output_fmt)
    if output:
        config.output_dir = output.parent

    try:
        with OCRProcessor(config) as processor:
            result = processor.process_file(image)
            processor.save_result(result)
    except OcrxError as exc:
        click.echo(f"错误: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
