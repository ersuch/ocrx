"""格式化器单元测试。"""

import json
from pathlib import Path

import pytest

from ocrx.config import OutputFormat
from ocrx.formatter import ResultFormatter
from ocrx.models import BBox, OCRResult, TextBlock


@pytest.fixture
def sample_result():
    bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
    return OCRResult(
        image_path="test.png",
        blocks=[
            TextBlock(text="hello", confidence=0.9, bbox=bbox),
            TextBlock(text="world", confidence=0.8, bbox=bbox),
        ],
        language="en",
        elapsed_time=0.5,
    )


class TestResultFormatter:
    def test_to_text(self, sample_result):
        text = ResultFormatter.to_text(sample_result)
        assert text == "hello\nworld"

    def test_to_json(self, sample_result):
        output = ResultFormatter.to_json(sample_result)
        data = json.loads(output)
        assert data["block_count"] == 2
        assert data["blocks"][0]["text"] == "hello"

    def test_to_structured(self, sample_result):
        structured = ResultFormatter.to_structured(sample_result)
        assert "_meta" in structured
        assert "blocks_sorted_by_confidence" in structured["_meta"]
        # highest confidence first
        sorted_blocks = structured["_meta"]["blocks_sorted_by_confidence"]
        assert sorted_blocks[0]["confidence"] == 0.9

    def test_serialize_json(self, sample_result):
        output = ResultFormatter.serialize(sample_result, OutputFormat.JSON)
        data = json.loads(output)
        assert data["block_count"] == 2

    def test_serialize_text(self, sample_result):
        output = ResultFormatter.serialize(sample_result, OutputFormat.TEXT)
        assert output == "hello\nworld"

    def test_write_and_read(self, sample_result, tmp_path):
        out_path = tmp_path / "result.json"
        ResultFormatter.write(sample_result, out_path, OutputFormat.JSON)
        assert out_path.exists()
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["block_count"] == 2
