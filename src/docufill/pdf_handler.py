"""Convert PDF files to images for OCR processing."""

from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import Image

from docufill._system_check import require_poppler


def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> List[Image.Image]:
    """Convert a PDF file to a list of PIL Images.

    Args:
        pdf_path: Path to the PDF file.
        dpi: Resolution for rendering. Higher = better OCR but slower.

    Returns:
        List of PIL Image objects, one per page.
    """
    require_poppler()
    from pdf2image import convert_from_path

    return convert_from_path(str(pdf_path), dpi=dpi)
