from __future__ import annotations

import typer
from rich.prompt import Prompt

from atlas.core.api import check_internet, get_country, search_countries
from atlas.core.display import show_country_card, show_error, show_loading, show_no_internet, show_suggestions

app = typer.Typer(help="Look up country details")


@app.callback(invoke_without_command=True)
def country_lookup(name: str = typer.Argument(..., help="Country name")) -> None:
    if not name:
        show_error("Please provide a country name.")
        raise typer.Exit(code=1)

    if not check_internet():
        show_no_internet()
        return

    with show_loading(f"Looking up {name}..."):
        data = get_country(name)

    if not data:
        suggestions = [c["name"] for c in search_countries(name, limit=3)]
        show_suggestions(name, suggestions)
        return

    show_country_card(data)


@app.command("clock")
def show_world_clock_command(country_name: str) -> None:
    if not check_internet():
        show_no_internet()
        return

    data = get_country(country_name)
    if not data:
        show_error(f"Country '{country_name}' was not found.")
        return

    from datetime import datetime
    from zoneinfo import ZoneInfo

    tz_name = None
    for candidate in data.get("timezones") or []:
        try:
            tz_name = candidate
            ZoneInfo(candidate)
            break
        except Exception:
            continue

    if not tz_name:
        show_error("No timezone data available for that country.")
        return

    now = datetime.now(ZoneInfo(tz_name))
    offset = now.strftime("%z")
    offset_text = f"UTC{offset[:3]}:{offset[3:]}"
    from atlas.core.display import show_world_clock

    show_world_clock(f"{data.get('capital', 'N/A')}, {data.get('name', 'N/A')}", now.strftime("%Y-%m-%d %H:%M:%S"), offset_text)
