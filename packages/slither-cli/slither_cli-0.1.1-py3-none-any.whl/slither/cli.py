"""Typer-based CLI interface for slither."""

from pathlib import Path
from typing import Optional
import typer
from slither.tree import SlitherBuilder


app = typer.Typer(
    name="slither",
    help="Display directory structure as a tree in your terminal",
    add_completion=False,
)


@app.command()
def main(
    directory: Path = typer.Argument(
        Path("."),
        help="Directory to display",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    level: Optional[int] = typer.Option(
        None,
        "-L",
        "--level",
        help="Max display depth of the directory tree",
        min=1,
    ),
    all_files: bool = typer.Option(
        False,
        "-a",
        "--all",
        help="Print all files, including hidden files (those starting with .)",
    ),
    dirs_only: bool = typer.Option(
        False,
        "-d",
        "--dirs-only",
        help="List directories only",
    ),
    pattern: Optional[str] = typer.Option(
        None,
        "-P",
        "--pattern",
        help="List only files that match the given pattern (wildcard)",
    ),
    ignore: Optional[str] = typer.Option(
        None,
        "-I",
        "--ignore",
        help="Do not list files that match the given pattern",
    ),
    size: bool = typer.Option(
        False,
        "-s",
        "--size",
        help="Print the size of each file in bytes along with the name",
    ),
    human: bool = typer.Option(
        False,
        "-h",
        "--human",
        help="Print file sizes in human-readable format (e.g., 1K, 234M, 2G)",
    ),
    sort_reverse: bool = typer.Option(
        False,
        "-r",
        "--reverse",
        help="Sort the output in reverse order",
    ),
):
    """
    Display directory structure in ASCII art format.

    Examples:

        slither                   # Display current directory

        slither /path/to/dir      # Display specific directory

        slither -L 2              # Limit depth to 2 levels

        slither -a                # Show hidden files

        slither -d                # Show directories only

        slither -P "*.py"         # Show only Python files

        slither -I "*.pyc"        # Ignore compiled Python files

        slither -s -h             # Show human-readable file sizes
    """
    # Validate that human-readable requires size flag
    if human and not size:
        size = True

    # Build the directory structure
    builder = SlitherBuilder(
        max_depth=level,
        show_hidden=all_files,
        dirs_only=dirs_only,
        pattern=pattern,
        ignore_pattern=ignore,
        show_size=size,
        human_readable=human,
        sort_reverse=sort_reverse,
    )

    # Render and print
    output = builder.render(directory)
    typer.echo(output)


if __name__ == "__main__":
    app()
