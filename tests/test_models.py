"""数据模型单元测试。"""

import pytest

from ocrx.models import BBox, OCRResult, TextBlock, TextDirection


class TestBBox:
    def test_from_paddle(self):
        points = [[10, 20], [100, 20], [100, 80], [10, 80]]
        bbox = BBox.from_paddle(points)
        assert bbox.top_left == (10, 20)
        assert bbox.top_right == (100, 20)
        assert bbox.bottom_right == (100, 80)
        assert bbox.bottom_left == (10, 80)

    def test_from_paddle_invalid_points(self):
        import pytest
        with pytest.raises(ValueError, match="需要恰好四个点"):
            BBox.from_paddle([[0, 0], [1, 1]])

    def test_properties(self):
        bbox = BBox.from_paddle([[10, 20], [100, 20], [100, 80], [10, 80]])
        assert bbox.x_min == 10
        assert bbox.x_max == 100
        assert bbox.y_min == 20
        assert bbox.y_max == 80
        assert bbox.width == 90
        assert bbox.height == 60
        assert bbox.area == 5400

    def test_to_paddle_roundtrip(self):
        points = [[10, 20], [100, 20], [100, 80], [10, 80]]
        bbox = BBox.from_paddle(points)
        assert bbox.to_paddle() == points

    def test_to_dict(self):
        bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
        d = bbox.to_dict()
        assert d["top_left"] == [0, 0]
        assert d["bottom_right"] == [10, 10]


class TestTextBlock:
    def test_to_dict(self):
        bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
        block = TextBlock(text="hello", confidence=0.95, bbox=bbox)
        d = block.to_dict()
        assert d["text"] == "hello"
        assert d["confidence"] == 0.95
        assert d["direction"] == "unknown"


class TestOCRResult:
    def test_text_concatenation(self):
        bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
        result = OCRResult(
            image_path="test.png",
            blocks=[
                TextBlock(text="hello", confidence=0.9, bbox=bbox),
                TextBlock(text="world", confidence=0.8, bbox=bbox),
            ],
            language="en",
            elapsed_time=0.5,
        )
        assert result.text == "hello\nworld"
        assert result.block_count == 2
        assert result.confidence_mean == pytest.approx(0.85)

    def test_empty_blocks(self):
        result = OCRResult(
            image_path="test.png",
            blocks=[],
            language="en",
            elapsed_time=0.1,
        )
        assert result.text == ""
        assert result.confidence_mean == 0.0

    def test_to_dict(self):
        bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
        result = OCRResult(
            image_path="test.png",
            blocks=[TextBlock(text="hi", confidence=0.9, bbox=bbox)],
            language="en",
            elapsed_time=0.5,
        )
        d = result.to_dict()
        assert d["image_path"] == "test.png"
        assert d["block_count"] == 1
        assert d["confidence_mean"] == 0.9
