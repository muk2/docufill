"""Extract document data from MRZ (Machine Readable Zone) on passports."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from docufill.models import DocumentResult

logger = logging.getLogger(__name__)


def _format_mrz_date(raw: str) -> Optional[str]:
    """Convert YYMMDD to DD/MM/YYYY."""
    if not raw or len(raw) != 6:
        return raw
    yy, mm, dd = raw[:2], raw[2:4], raw[4:6]
    year = int(yy)
    # Assume 2000s for years <= 40, 1900s otherwise
    century = 2000 if year <= 40 else 1900
    return f"{dd}/{mm}/{century + year}"


def _clean(value: Optional[str]) -> Optional[str]:
    """Strip filler characters from MRZ fields."""
    if not value:
        return None
    cleaned = value.replace("<", " ").strip()
    return cleaned if cleaned else None


def extract_mrz(source: Union[str, Path, Image.Image]) -> Optional[DocumentResult]:
    """Try to extract data from MRZ zone in an image.

    Args:
        source: File path or PIL Image.

    Returns:
        DocumentResult if MRZ found and parsed, None otherwise.
    """
    try:
        from passporteye import read_mrz
    except ImportError:
        logger.warning("passporteye not installed, skipping MRZ extraction")
        return None

    try:
        if isinstance(source, Image.Image):
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                source.save(tmp.name)
                mrz_data = read_mrz(tmp.name)
                Path(tmp.name).unlink(missing_ok=True)
        else:
            mrz_data = read_mrz(str(source))
    except Exception:
        logger.debug("passporteye failed to read MRZ", exc_info=True)
        return None

    if mrz_data is None:
        return None

    try:
        mrz_dict = mrz_data.to_dict()
    except Exception:
        logger.debug("MRZ to_dict failed", exc_info=True)
        return None

    surname = _clean(mrz_dict.get("surname"))
    given_names = _clean(mrz_dict.get("names"))
    full_name = " ".join(filter(None, [given_names, surname])) or None

    sex_raw = mrz_dict.get("sex", "")
    sex_map = {"M": "Male", "F": "Female"}
    sex = sex_map.get(sex_raw, sex_raw if sex_raw else None)

    return DocumentResult(
        surname=surname,
        given_names=given_names,
        full_name=full_name,
        date_of_birth=_format_mrz_date(mrz_dict.get("date_of_birth")),
        sex=sex,
        nationality=_clean(mrz_dict.get("nationality")),
        document_number=_clean(mrz_dict.get("number")),
        expiry_date=_format_mrz_date(mrz_dict.get("expiration_date")),
        document_type=_clean(mrz_dict.get("type")),
        issuing_country=_clean(mrz_dict.get("country")),
        personal_number=_clean(mrz_dict.get("personal_number")),
        method="mrz",
    )
