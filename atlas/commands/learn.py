from __future__ import annotations

import typer

from atlas.core.api import check_internet, get_all_countries
from atlas.core.display import show_error, show_learn_panel, show_no_internet

app = typer.Typer(help="Learn continent summaries")

VALID_CONTINENTS = {
    "africa": "Africa",
    "asia": "Asia",
    "europe": "Europe",
    "americas": "Americas",
    "oceania": "Oceania",
}


@app.callback(invoke_without_command=True)
def show_continent_summary(continent: str = typer.Argument(..., help="Continent name")) -> None:
    normalized = continent.strip().lower()
    if normalized not in VALID_CONTINENTS:
        show_error("Continent must be one of: Africa, Asia, Europe, Americas, Oceania")
        raise typer.Exit(code=1)

    if not check_internet():
        show_no_internet()
        return

    countries = [c for c in get_all_countries() if c.get("continent", "").lower() == VALID_CONTINENTS[normalized].lower()]
    if not countries:
        show_error("No country data available for that continent.")
        return

    largest = max(countries, key=lambda c: c.get("area_km2") or 0)
    most_populous = max(countries, key=lambda c: c.get("population") or 0)
    show_learn_panel(VALID_CONTINENTS[normalized], len(countries), largest, most_populous)
