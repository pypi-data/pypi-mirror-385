"""Console script for x_series."""

import typer
from rich.console import Console

from x_series import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for x_series."""
    console.print("Replace this message by putting your code into "
               "x_series.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
