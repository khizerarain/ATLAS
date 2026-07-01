from __future__ import annotations

import typer

from core.api import check_internet, get_all_countries
from core.display import show_error, show_no_internet, show_rankings_table

app = typer.Typer(help="Show top rankings")


@app.callback(invoke_without_command=True)
def show_rankings(metric: str = typer.Argument("population", help="Metric to rank by")) -> None:
    if metric not in {"population", "area", "borders"}:
        show_error("Metric must be one of: population, area, borders")
        raise typer.Exit(code=1)

    if not check_internet():
        show_no_internet()
        return

    countries = get_all_countries()
    if not countries:
        show_error("No country data available right now.")
        return

    if metric == "population":
        ranked = sorted(countries, key=lambda c: (c.get("population") or 0), reverse=True)[:10]
        rows = [(i + 1, c.get("flag_emoji", ""), c.get("name", "N/A"), f"{int(c.get('population') or 0):,}") for i, c in enumerate(ranked)]
        title = "🌍 Top 10 by Population"
    elif metric == "area":
        ranked = sorted(countries, key=lambda c: (c.get("area_km2") or 0), reverse=True)[:10]
        rows = [(i + 1, c.get("flag_emoji", ""), c.get("name", "N/A"), f"{int(c.get('area_km2') or 0):,} km²") for i, c in enumerate(ranked)]
        title = "🌍 Top 10 by Area"
    else:
        ranked = sorted(countries, key=lambda c: len(c.get("borders") or []), reverse=True)[:10]
        rows = [(i + 1, c.get("flag_emoji", ""), c.get("name", "N/A"), str(len(c.get("borders") or []))) for i, c in enumerate(ranked)]
        title = "🌍 Top 10 by Borders"

    show_rankings_table(title, rows)
