"""Main scanning orchestrator: MRZ first, OCR fallback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

from PIL import Image

from docufill.exceptions import ExtractionError
from docufill.models import DocumentResult
from docufill.mrz_extract import extract_mrz
from docufill.ocr_fallback import extract_ocr
from docufill.pdf_handler import pdf_to_images

logger = logging.getLogger(__name__)

_PDF_EXTENSIONS = {".pdf"}
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}


def scan(file_path: Union[str, Path]) -> DocumentResult:
    """Scan a document image or PDF and extract structured fields.

    Tries MRZ extraction first (passporteye), then falls back to
    full-page OCR with regex pattern matching.

    Args:
        file_path: Path to image (JPG/PNG) or PDF.

    Returns:
        DocumentResult with extracted fields.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ExtractionError: If no data could be extracted.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix in _PDF_EXTENSIONS:
        images = pdf_to_images(path)
    elif suffix in _IMAGE_EXTENSIONS:
        images = [Image.open(str(path))]
    else:
        raise ExtractionError(
            f"Unsupported file type: {suffix}. "
            f"Supported: {', '.join(sorted(_IMAGE_EXTENSIONS | _PDF_EXTENSIONS))}"
        )

    # Try each page/image
    for image in images:
        # 1. Try MRZ extraction first
        result = extract_mrz(image)
        if result:
            logger.info("Extracted data via MRZ")
            return result

        # 2. Fall back to OCR
        result = extract_ocr(image)
        if result:
            logger.info("Extracted data via OCR fallback")
            return result

    raise ExtractionError(
        "Could not extract any data from the document. "
        "Ensure the image is clear and contains a passport or ID."
    )
