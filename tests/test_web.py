"""Tests for the web application."""

import io
from unittest.mock import patch

from docufill.models import DocumentResult
from docufill.web.app import create_app


def test_index():
    app = create_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Docufill" in resp.data


def test_api_scan_no_file():
    app = create_app()
    client = app.test_client()
    resp = client.post("/api/scan")
    assert resp.status_code == 400


@patch("docufill.scanner.scan")
def test_api_scan_success(mock_scan):
    mock_scan.return_value = DocumentResult(
        full_name="John Doe",
        date_of_birth="15/01/1990",
        method="mrz",
    )
    app = create_app()
    client = app.test_client()
    data = {"file": (io.BytesIO(b"fake image data"), "test.jpg")}
    resp = client.post("/api/scan", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data["full_name"] == "John Doe"
