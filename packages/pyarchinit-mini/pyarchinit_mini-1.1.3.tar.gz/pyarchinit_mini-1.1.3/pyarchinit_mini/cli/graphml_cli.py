"""
CLI commands for GraphML Converter functionality
"""

import click
from rich.console import Console
from pathlib import Path
import os

console = Console()


@click.group()
def graphml():
    """Convert Graphviz DOT files to yEd GraphML format"""
    pass


@graphml.command('convert')
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--title', '-t', default="", help='Diagram title/header')
@click.option('--reverse-epochs/--no-reverse-epochs', default=False,
              help='Reverse epoch ordering (default: no)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def convert_command(input_file, output_file, title, reverse_epochs, verbose):
    """
    Convert a DOT file to GraphML format.

    INPUT_FILE: Path to input .dot file

    OUTPUT_FILE: Path to output .graphml file

    Example:
        pyarchinit-graphml convert harris.dot harris.graphml -t "Pompei - Regio VI"
    """
    try:
        from pyarchinit_mini.graphml_converter import (
            convert_dot_to_graphml,
            GraphMLConverterOptions
        )

        # Create options
        options = GraphMLConverterOptions()
        options.verbose = verbose

        # Convert
        console.print(f"[cyan]Converting DOT to GraphML...[/cyan]")
        if title:
            console.print(f"[dim]  Title: {title}[/dim]")
        console.print(f"[dim]  Input: {input_file}[/dim]")
        console.print(f"[dim]  Output: {output_file}[/dim]")
        console.print(f"[dim]  Reverse epochs: {reverse_epochs}[/dim]")
        console.print()

        success = convert_dot_to_graphml(
            input_file,
            output_file,
            title=title,
            reverse_epochs=reverse_epochs,
            options=options
        )

        if success:
            # Check output file size
            size = os.path.getsize(output_file)
            size_kb = size / 1024
            console.print(f"[green]✓ Conversion successful![/green]")
            console.print(f"[dim]  Output file: {output_file} ({size_kb:.1f} KB)[/dim]")
        else:
            console.print(f"[red]✗ Conversion failed[/red]")
            raise click.Abort()

    except Exception as e:
        console.print(f"[red]✗ Error during conversion: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@graphml.command('template')
@click.argument('output_file', type=click.Path(), default='EM_palette.graphml')
def template_command(output_file):
    """
    Download the yEd GraphML template file.

    OUTPUT_FILE: Path to save the template (default: EM_palette.graphml)

    Example:
        pyarchinit-graphml template my_template.graphml
    """
    try:
        from pyarchinit_mini.graphml_converter import get_template_path
        import shutil

        template_path = get_template_path()

        if not os.path.exists(template_path):
            console.print(f"[red]✗ Template file not found at {template_path}[/red]")
            raise click.Abort()

        # Copy template to output location
        console.print(f"[cyan]Copying yEd template...[/cyan]")
        console.print(f"[dim]  From: {template_path}[/dim]")
        console.print(f"[dim]  To: {output_file}[/dim]")
        console.print()

        shutil.copy2(template_path, output_file)

        size = os.path.getsize(output_file)
        size_kb = size / 1024
        console.print(f"[green]✓ Template copied successfully![/green]")
        console.print(f"[dim]  Output file: {output_file} ({size_kb:.1f} KB)[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error copying template: {e}[/red]")
        raise click.Abort()


@graphml.command('batch')
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory (default: same as input)')
@click.option('--title-prefix', '-t', default="", help='Prefix for diagram titles')
@click.option('--reverse-epochs/--no-reverse-epochs', default=False,
              help='Reverse epoch ordering (default: no)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch_command(input_dir, output_dir, title_prefix, reverse_epochs, verbose):
    """
    Batch convert all DOT files in a directory to GraphML.

    INPUT_DIR: Directory containing .dot files

    Example:
        pyarchinit-graphml batch /path/to/dot/files -o /path/to/output
    """
    try:
        from pyarchinit_mini.graphml_converter import (
            convert_dot_to_graphml,
            GraphMLConverterOptions
        )

        # Setup directories
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all .dot files
        dot_files = list(input_path.glob('*.dot'))

        if not dot_files:
            console.print(f"[yellow]⚠ No .dot files found in {input_dir}[/yellow]")
            return

        console.print(f"[cyan]Found {len(dot_files)} DOT files to convert[/cyan]")
        console.print()

        # Create options
        options = GraphMLConverterOptions()
        options.verbose = verbose

        # Convert each file
        success_count = 0
        fail_count = 0

        for dot_file in dot_files:
            # Generate title from filename
            title = f"{title_prefix}{dot_file.stem}" if title_prefix else dot_file.stem

            # Output file path
            graphml_file = output_path / f"{dot_file.stem}.graphml"

            console.print(f"[dim]Converting {dot_file.name}...[/dim]")

            try:
                success = convert_dot_to_graphml(
                    str(dot_file),
                    str(graphml_file),
                    title=title,
                    reverse_epochs=reverse_epochs,
                    options=options
                )

                if success:
                    success_count += 1
                    size = os.path.getsize(graphml_file)
                    size_kb = size / 1024
                    console.print(f"  [green]✓ {graphml_file.name} ({size_kb:.1f} KB)[/green]")
                else:
                    fail_count += 1
                    console.print(f"  [red]✗ Failed[/red]")

            except Exception as e:
                fail_count += 1
                console.print(f"  [red]✗ Error: {e}[/red]")

        console.print()
        console.print(f"[cyan]Batch conversion complete:[/cyan]")
        console.print(f"  [green]✓ Success: {success_count}[/green]")
        if fail_count > 0:
            console.print(f"  [red]✗ Failed: {fail_count}[/red]")

    except Exception as e:
        console.print(f"[red]✗ Error during batch conversion: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


def main():
    """Entry point for pyarchinit-graphml command"""
    graphml()


if __name__ == '__main__':
    main()
