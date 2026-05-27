"""CLI commands for docufill."""

from __future__ import annotations

import sys

import click

from docufill import __version__


@click.group()
@click.version_option(version=__version__, prog_name="docufill")
def main() -> None:
    """Docufill - Extract guest info from passport/ID scans."""


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def scan(file: str, as_json: bool) -> None:
    """Scan a passport or ID image/PDF and extract fields."""
    from docufill.exceptions import ExtractionError, SystemDependencyError
    from docufill.scanner import scan as do_scan

    try:
        result = do_scan(file)
    except SystemDependencyError as exc:
        click.secho(f"Missing dependency: {exc}", fg="red", err=True)
        click.echo("Run 'docufill doctor' for setup instructions.", err=True)
        sys.exit(1)
    except ExtractionError as exc:
        click.secho(f"Extraction failed: {exc}", fg="red", err=True)
        sys.exit(1)

    if as_json:
        click.echo(result.to_json())
    else:
        click.echo(result.to_table())


@main.command()
def doctor() -> None:
    """Check that all system dependencies are installed."""
    from docufill._system_check import check_all

    results = check_all()
    all_ok = True

    for name, ok, msg in results:
        symbol = click.style("✓", fg="green") if ok else click.style("✗", fg="red")
        click.echo(f"  {symbol} {name}: {msg}")
        if not ok:
            all_ok = False

    if all_ok:
        click.echo()
        click.secho("All dependencies OK.", fg="green")
    else:
        click.echo()
        click.secho("Some dependencies are missing. See above.", fg="red")
        sys.exit(1)


@main.command()
@click.option("--port", default=5050, help="Port to serve on.", show_default=True)
@click.option("--host", default="127.0.0.1", help="Host to bind to.", show_default=True)
def serve(port: int, host: str) -> None:
    """Launch the web UI for drag-and-drop scanning."""
    from docufill.web.app import create_app

    app = create_app()
    click.echo(f"Docufill web UI: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
