"""Console script for x_files."""

import typer
from rich.console import Console

from fileforge import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for x_files."""
    console.print("Replace this message by putting your code into "
               "x_files.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
