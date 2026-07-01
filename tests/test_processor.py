"""处理器编排器单元测试。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ocrx.config import OCRConfig
from ocrx.exceptions import ValidationError
from ocrx.models import BBox, OCRResult, TextBlock
from ocrx.processor import OCRProcessor


@pytest.fixture
def config():
    return OCRConfig(lang="en", verbose=False)


@pytest.fixture
def sample_result():
    bbox = BBox.from_paddle([[0, 0], [10, 0], [10, 10], [0, 10]])
    return OCRResult(
        image_path="test.png",
        blocks=[TextBlock(text="hello", confidence=0.9, bbox=bbox)],
        language="en",
        elapsed_time=0.5,
    )


class TestOCRProcessor:
    @patch("ocrx.processor.OCREngine")
    def test_process_nonexistent_file(self, mock_engine_cls, config):
        mock_engine = MagicMock()
        mock_engine_cls.return_value.__enter__.return_value = mock_engine

        with OCRProcessor(config) as processor:
            with pytest.raises(ValidationError):
                processor.process_file("/nonexistent/image.png")

    @patch("ocrx.processor.validate_image", return_value=True)
    @patch("ocrx.processor.OCREngine")
    def test_process_file(
        self, mock_engine_cls, mock_validate, config, sample_result
    ):
        mock_engine = MagicMock()
        mock_engine.run.return_value = sample_result
        mock_engine_cls.return_value.__enter__.return_value = mock_engine

        with OCRProcessor(config) as processor:
            result = processor.process_file("test.png")
            assert result.block_count == 1
            assert result.text == "hello"

    @patch("ocrx.processor.validate_image", return_value=True)
    @patch("ocrx.processor.OCREngine")
    def test_process_batch(
        self, mock_engine_cls, mock_validate, config, sample_result
    ):
        mock_engine = MagicMock()
        mock_engine.run.return_value = sample_result
        mock_engine_cls.return_value.__enter__.return_value = mock_engine

        with OCRProcessor(config) as processor:
            results = processor.process_batch(["a.png", "b.png"])
            assert len(results) == 2
            assert mock_engine.run.call_count == 2
