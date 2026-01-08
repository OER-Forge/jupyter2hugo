"""Command-line interface for jupyter2hugo."""

from pathlib import Path
import click
import sys

from .core.hugo_builder import HugoBuilder


@click.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('output_dir', type=click.Path(path_type=Path))
@click.option(
    '--check-accessibility',
    is_flag=True,
    help='Run accessibility checks after conversion (requires pa11y)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
@click.version_option(version='0.1.0')
def main(source_dir: Path, output_dir: Path, check_accessibility: bool, verbose: bool):
    """
    Convert a Jupyter Book project to a Hugo static site.

    SOURCE_DIR: Path to the Jupyter Book project directory (containing _toc.yml)

    OUTPUT_DIR: Path where the Hugo site will be created
    """
    click.echo("=" * 60)
    click.echo("jupyter2hugo - Jupyter Book to Hugo Converter")
    click.echo("=" * 60)
    click.echo()

    # Validate source directory
    toc_file = source_dir / "_toc.yml"
    if not toc_file.exists():
        click.echo(f"Error: _toc.yml not found in {source_dir}", err=True)
        click.echo("Make sure you're pointing to a valid Jupyter Book project directory.", err=True)
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Build the Hugo site
        builder = HugoBuilder(source_dir, output_dir, verbose=verbose)
        builder.build()

        click.echo()
        click.secho("✓ Conversion completed successfully!", fg='green', bold=True)
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  1. cd {output_dir}")
        click.echo("  2. hugo server")
        click.echo("  3. Visit http://localhost:1313")
        click.echo()

        # Run accessibility check if requested
        if check_accessibility:
            click.echo("Running accessibility checks...")
            from .accessibility.checker import run_accessibility_check
            try:
                result = run_accessibility_check(output_dir / 'hugo-site')
                if result:
                    click.secho("✓ Accessibility check completed", fg='green')
                else:
                    click.secho("⚠ Accessibility issues found", fg='yellow')
            except ImportError:
                click.secho("⚠ pa11y not available - skipping accessibility check", fg='yellow')
                click.echo("  Install pa11y: npm install -g pa11y")
            except Exception as e:
                click.secho(f"⚠ Accessibility check failed: {e}", fg='yellow')

    except Exception as e:
        click.secho(f"✗ Conversion failed: {e}", fg='red', bold=True, err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
