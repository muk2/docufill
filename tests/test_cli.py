"""Tests for the CLI."""

from click.testing import CliRunner

from docufill.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "docufill" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.output
    assert "doctor" in result.output
    assert "serve" in result.output


def test_scan_missing_file():
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "/nonexistent.jpg"])
    assert result.exit_code != 0
