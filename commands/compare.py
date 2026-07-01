from __future__ import annotations

import typer

from core.api import check_internet, get_country
from core.display import show_comparison_table, show_error, show_no_internet

app = typer.Typer(help="Compare two countries")


@app.callback(invoke_without_command=True)
def compare_countries(
    country_a: str = typer.Argument(..., help="First country"),
    country_b: str = typer.Argument(..., help="Second country"),
) -> None:
    if not country_a or not country_b:
        show_error("Please provide two country names.")
        raise typer.Exit(code=1)

    if not check_internet():
        show_no_internet()
        return

    a = get_country(country_a)
    b = get_country(country_b)
    if not a or not b:
        show_error("One or both countries could not be found.")
        return

    show_comparison_table(a, b)
