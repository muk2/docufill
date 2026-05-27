"""Flask web application for docufill."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/scan", methods=["POST"])
    def api_scan():
        from docufill.exceptions import ExtractionError, SystemDependencyError
        from docufill.scanner import scan

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        suffix = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            result = scan(tmp_path)
            return jsonify(result.to_dict())
        except SystemDependencyError as exc:
            return jsonify({"error": f"Missing dependency: {exc}"}), 500
        except ExtractionError as exc:
            return jsonify({"error": str(exc)}), 422
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return app
