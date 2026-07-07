from __future__ import annotations

import json
from pathlib import Path

import typer

from atlas.core.display import show_error

app = typer.Typer(help="Travel tips and info")


@app.callback(invoke_without_command=True)
def travel_info(country: str = typer.Argument(..., help="Country name")) -> None:
    if not country:
        show_error("Please provide a country name.")
        raise typer.Exit(code=1)

    data_path = Path(__file__).resolve().parent.parent / "data" / "travel_info.json"
    with data_path.open("r", encoding="utf-8") as handle:
        content = json.load(handle)

    match = content.get(country.lower())
    if not match:
        show_error("Travel info is not available for that country yet.")
        return

    from rich.console import Console
    from rich.panel import Panel

    lines = [f"Visa: {match.get('visa', 'N/A')}", f"Emergency: {match.get('emergency_numbers', 'N/A')}", f"Best months: {match.get('best_months', 'N/A')}", f"Weather: {match.get('weather_overview', 'N/A')}"]
    Console().print(Panel("\n".join(lines), title=f"✈️ Travel tips for {country.title()}", border_style="cyan"))
