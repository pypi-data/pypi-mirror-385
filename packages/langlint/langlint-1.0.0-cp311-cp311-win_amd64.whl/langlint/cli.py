"""
Command-line interface for LangLint (Rust-powered).

This module provides a thin Python wrapper around the Rust implementation,
maintaining API compatibility with the original Python version.
"""

import json
import sys

import click

from . import scan as rust_scan
from . import translate as rust_translate
from . import version as rust_version


@click.group()
@click.version_option(rust_version(), prog_name="langlint")
def cli():
    """LangLint - Intelligent translation management for code and documentation"""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--format", "-f", default="json", type=click.Choice(["json", "text"]), help="Output format"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--exclude", "-e", multiple=True, help="Patterns to exclude (e.g., demo_files, tests)")
@click.option("--output", "-o", help="Output file (optional, defaults to stdout)")
def scan(path, format, verbose, exclude, output):
    """Scan files and extract translatable units"""
    try:
        # Convert exclude tuple to list
        exclude_list = list(exclude) if exclude else None
        result = rust_scan(path, format=format, verbose=verbose, exclude=exclude_list)
        
        # Write to file or stdout
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result)
            click.echo(f"Results written to: {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--source", "-s", required=True, help="Source language code (e.g., en, zh, ja)")
@click.option("--target", "-t", required=True, help="Target language code (e.g., en, zh, ja)")
@click.option(
    "--translator", default="google", type=click.Choice(["mock", "google"]), help="Translator to use"
)
@click.option("--output", "-o", help="Output file path (optional, defaults to in-place)")
@click.option("--dry-run", is_flag=True, help="Perform dry run without writing")
def translate(path, source, target, translator, output, dry_run):
    """Translate files from source to target language"""
    try:
        result = rust_translate(
            path, source, target, translator=translator, output=output, dry_run=dry_run
        )

        # Parse and pretty-print result
        result_data = json.loads(result)

        if result_data.get("status") == "success":
            translated = result_data.get("translated", 0)
            click.echo(f"[OK] Successfully translated {translated} units")

            if dry_run:
                click.echo("  (Dry run - no files were modified)")
            else:
                output_path = result_data.get("output", path)
                click.echo(f"  Output: {output_path}")
        else:
            click.echo(
                f"Translation failed: {result_data.get('message', 'Unknown error')}", err=True
            )
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--source", "-s", required=True, help="Source language code")
@click.option("--target", "-t", required=True, help="Target language code")
@click.option("--translator", default="google", help="Translator to use")
@click.option("--yes", "-y", is_flag=True, help="Auto-fix without confirmation")
def fix(path, source, target, translator, yes):
    """Fix translation issues in files (in-place translation with backup)"""
    if not yes:
        click.confirm(
            f"This will modify {path} in-place (a backup will be created). Continue?", abort=True
        )

    try:
        # Fix is just translate without output (in-place with backup)
        result = rust_translate(
            path, source, target, translator=translator, output=None, dry_run=False
        )

        result_data = json.loads(result)

        if result_data.get("status") == "success":
            translated = result_data.get("translated", 0)
            click.echo(f"[OK] Fixed {translated} units in {path}")
            click.echo(f"  Backup created: {path}.backup")
        else:
            click.echo(f"Fix failed: {result_data.get('message', 'Unknown error')}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
