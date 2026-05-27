"""Check that required system dependencies are installed."""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import List, Tuple

from docufill.exceptions import SystemDependencyError

_INSTALL_HINTS = {
    "tesseract": {
        "linux": "sudo apt-get install tesseract-ocr",
        "darwin": "brew install tesseract",
        "win32": "choco install tesseract  (or download from https://github.com/UB-Mannheim/tesseract/wiki)",
    },
    "poppler": {
        "linux": "sudo apt-get install poppler-utils",
        "darwin": "brew install poppler",
        "win32": "choco install poppler  (or conda install -c conda-forge poppler)",
    },
}


def _platform_key() -> str:
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "darwin"
    return "win32"


def _check_tesseract() -> Tuple[bool, str]:
    if shutil.which("tesseract") is None:
        hint = _INSTALL_HINTS["tesseract"].get(_platform_key(), "")
        return False, f"tesseract not found. Install: {hint}"
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        version = result.stdout.split("\n")[0] if result.stdout else "unknown"
        return True, f"tesseract {version}"
    except Exception as exc:
        return False, f"tesseract found but failed: {exc}"


def _check_poppler() -> Tuple[bool, str]:
    if shutil.which("pdftoppm") is None:
        hint = _INSTALL_HINTS["poppler"].get(_platform_key(), "")
        return False, f"poppler (pdftoppm) not found. Install: {hint}"
    try:
        result = subprocess.run(
            ["pdftoppm", "-v"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stderr.strip() or result.stdout.strip()
        version = output.split("\n")[0] if output else "unknown"
        return True, f"poppler {version}"
    except Exception as exc:
        return False, f"poppler found but failed: {exc}"


def check_all() -> List[Tuple[str, bool, str]]:
    """Return list of (name, ok, message) for all system deps."""
    results = []
    ok, msg = _check_tesseract()
    results.append(("tesseract", ok, msg))
    ok, msg = _check_poppler()
    results.append(("poppler", ok, msg))
    return results


def require_tesseract() -> None:
    """Raise SystemDependencyError if tesseract is not available."""
    ok, msg = _check_tesseract()
    if not ok:
        raise SystemDependencyError(msg)


def require_poppler() -> None:
    """Raise SystemDependencyError if poppler is not available."""
    ok, msg = _check_poppler()
    if not ok:
        raise SystemDependencyError(msg)
