"""Tests for MRZ extraction utilities."""

from docufill.mrz_extract import _clean, _format_mrz_date


def test_format_mrz_date_birth():
    assert _format_mrz_date("900115") == "15/01/1990"


def test_format_mrz_date_2000s():
    assert _format_mrz_date("250601") == "01/06/2025"


def test_format_mrz_date_none():
    assert _format_mrz_date(None) is None


def test_format_mrz_date_short():
    assert _format_mrz_date("12") == "12"


def test_clean_removes_fillers():
    assert _clean("SMITH<<JOHN") == "SMITH  JOHN"


def test_clean_none():
    assert _clean(None) is None


def test_clean_empty():
    assert _clean("<<<") is None
