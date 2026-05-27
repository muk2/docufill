"""Fallback OCR extraction using pytesseract + regex pattern matching."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from docufill._system_check import require_tesseract
from docufill.models import DocumentResult

logger = logging.getLogger(__name__)

# Common date formats: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD
_DATE_PATTERN = re.compile(
    r"\b(\d{2}[/\-\.]\d{2}[/\-\.]\d{4}|\d{4}[/\-\.]\d{2}[/\-\.]\d{2})\b"
)

# Passport / document number: typically 1-2 letters followed by 6-9 digits
_DOC_NUMBER_PATTERN = re.compile(r"\b([A-Z]{0,2}\d{6,9})\b")

# Sex
_SEX_PATTERN = re.compile(r"\b(MALE|FEMALE|M(?:ALE)?|F(?:EMALE)?)\b", re.IGNORECASE)

# Country codes (3-letter)
_COUNTRY_PATTERN = re.compile(r"\b([A-Z]{3})\b")

# Name-like lines (all caps, letters and spaces/hyphens)
_NAME_PATTERN = re.compile(r"^([A-Z][A-Z\s\-']{2,})$", re.MULTILINE)


def _ocr_image(source: Union[str, Path, Image.Image]) -> str:
    """Run Tesseract OCR on an image and return raw text."""
    require_tesseract()
    import pytesseract

    if isinstance(source, (str, Path)):
        img = Image.open(str(source))
    else:
        img = source
    return pytesseract.image_to_string(img)


def _find_dates(text: str) -> list[str]:
    return _DATE_PATTERN.findall(text)


def _find_doc_number(text: str) -> Optional[str]:
    match = _DOC_NUMBER_PATTERN.search(text)
    return match.group(1) if match else None


def _find_sex(text: str) -> Optional[str]:
    match = _SEX_PATTERN.search(text)
    if not match:
        return None
    raw = match.group(1).upper()
    if raw in ("M", "MALE"):
        return "Male"
    if raw in ("F", "FEMALE"):
        return "Female"
    return raw


def _find_names(text: str) -> Optional[str]:
    """Find the most likely name from OCR text."""
    # Look for common label patterns
    for label in ("SURNAME", "LAST NAME", "NOM", "FAMILY NAME"):
        pattern = re.compile(
            rf"{label}\s*[:/]?\s*([A-Z][A-Z\s\-']+)", re.IGNORECASE
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()

    # Fall back to longest all-caps line
    matches = _NAME_PATTERN.findall(text)
    if matches:
        return max(matches, key=len).strip()
    return None


def extract_ocr(source: Union[str, Path, Image.Image]) -> Optional[DocumentResult]:
    """Extract document fields via full-page OCR + regex matching.

    Args:
        source: File path or PIL Image.

    Returns:
        DocumentResult with whatever fields could be extracted, or None.
    """
    try:
        text = _ocr_image(source)
    except Exception:
        logger.debug("OCR failed", exc_info=True)
        return None

    if not text or not text.strip():
        return None

    dates = _find_dates(text)
    doc_number = _find_doc_number(text)
    sex = _find_sex(text)
    full_name = _find_names(text)

    # Heuristic: first date is DOB, second is expiry
    dob = dates[0] if len(dates) >= 1 else None
    expiry = dates[1] if len(dates) >= 2 else None

    result = DocumentResult(
        full_name=full_name,
        date_of_birth=dob,
        sex=sex,
        document_number=doc_number,
        expiry_date=expiry,
        method="ocr",
    )

    # Only return if we extracted at least one meaningful field
    meaningful = [full_name, dob, doc_number]
    if not any(meaningful):
        return None

    return result
