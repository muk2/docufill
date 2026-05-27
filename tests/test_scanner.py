"""Tests for the scanner orchestrator."""

from unittest.mock import patch

import pytest

from docufill.exceptions import ExtractionError
from docufill.models import DocumentResult
from docufill.scanner import scan


def test_scan_file_not_found():
    with pytest.raises(FileNotFoundError):
        scan("/nonexistent/file.jpg")


def test_scan_unsupported_extension(tmp_path):
    f = tmp_path / "doc.xyz"
    f.write_text("hello")
    with pytest.raises(ExtractionError, match="Unsupported file type"):
        scan(str(f))


@patch("docufill.scanner.extract_mrz")
@patch("docufill.scanner.extract_ocr")
def test_scan_tries_mrz_first(mock_ocr, mock_mrz, tmp_path):
    img = tmp_path / "test.png"
    # Create a minimal valid PNG
    from PIL import Image

    Image.new("RGB", (100, 100)).save(str(img))

    expected = DocumentResult(full_name="John Doe", method="mrz")
    mock_mrz.return_value = expected

    result = scan(str(img))
    assert result.full_name == "John Doe"
    assert result.method == "mrz"
    mock_ocr.assert_not_called()


@patch("docufill.scanner.extract_mrz")
@patch("docufill.scanner.extract_ocr")
def test_scan_falls_back_to_ocr(mock_ocr, mock_mrz, tmp_path):
    img = tmp_path / "test.jpg"
    from PIL import Image

    Image.new("RGB", (100, 100)).save(str(img))

    mock_mrz.return_value = None
    expected = DocumentResult(full_name="Jane Doe", method="ocr")
    mock_ocr.return_value = expected

    result = scan(str(img))
    assert result.full_name == "Jane Doe"
    assert result.method == "ocr"


@patch("docufill.scanner.extract_mrz")
@patch("docufill.scanner.extract_ocr")
def test_scan_raises_when_nothing_extracted(mock_ocr, mock_mrz, tmp_path):
    img = tmp_path / "test.png"
    from PIL import Image

    Image.new("RGB", (100, 100)).save(str(img))

    mock_mrz.return_value = None
    mock_ocr.return_value = None

    with pytest.raises(ExtractionError, match="Could not extract"):
        scan(str(img))
