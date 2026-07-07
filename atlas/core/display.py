"""
core/display.py

All Rich-based rendering helpers. Individual commands should stay thin and
just call these functions instead of formatting output themselves.
"""
from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from atlas.core.utils import format_population, format_area, format_number


def _configure_utf8_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


_configure_utf8_streams()

console = Console()

BORDER_STYLE = "cyan"


# ---------------------------------------------------------------------------
# Generic status panels
# ---------------------------------------------------------------------------

def show_error(message: str, title: str = "⚠ Error") -> None:
    console.print(
        Panel(f"[bold red]{message}[/bold red]", title=title, border_style="red")
    )


def show_success(message: str, title: str = "✔ Success") -> None:
    console.print(
        Panel(f"[bold green]{message}[/bold green]", title=title, border_style="green")
    )


def show_warning(message: str, title: str = "⚠ Warning") -> None:
    console.print(
        Panel(f"[bold yellow]{message}[/bold yellow]", title=title, border_style="yellow")
    )


def show_loading(message: str):
    """Returns a Rich status context manager for use with `with`."""
    return console.status(f"[bold cyan]{message}[/bold cyan]", spinner="earth")


def show_no_internet() -> None:
    show_warning(
        "No internet connection detected.\n"
        "This command needs live data. Please check your network and try again.",
        title="📡 No Internet Connection",
    )


# ---------------------------------------------------------------------------
# Country card
# ---------------------------------------------------------------------------

def show_country_card(data: dict) -> None:
    flag = data.get("flag_emoji", "")
    name = data.get("name", "Unknown")

    left = Text()
    left.append("Capital\n", style="bold cyan")
    left.append(f"{data.get('capital', 'N/A')}\n\n", style="white")
    left.append("Population\n", style="bold cyan")
    left.append(f"{format_population(data.get('population'))}\n\n", style="white")
    left.append("Area\n", style="bold cyan")
    left.append(f"{format_area(data.get('area_km2'))}\n\n", style="white")
    left.append("Continent\n", style="bold cyan")
    left.append(f"{data.get('continent', 'N/A')}\n", style="white")

    right = Text()
    right.append("Currency\n", style="bold cyan")
    right.append(
        f"{data.get('currency_name', 'N/A')} ({data.get('currency_code', 'N/A')})\n\n",
        style="white",
    )
    right.append("Official Language\n", style="bold cyan")
    right.append(f"{data.get('language', 'N/A')}\n\n", style="white")
    tz = data.get("timezones") or []
    right.append("Time Zone\n", style="bold cyan")
    right.append(f"{', '.join(tz) if tz else 'N/A'}\n\n", style="white")
    borders = data.get("borders") or []
    right.append("Borders\n", style="bold cyan")
    right.append(f"{', '.join(borders) if borders else 'None (island/isolated)'}\n", style="white")

    table = Table.grid(padding=(0, 4), expand=True)
    table.add_column(ratio=1)
    table.add_column(ratio=1)
    table.add_row(left, right)

    console.print(
        Panel(
            table,
            title=f"{flag}  {name}",
            border_style=BORDER_STYLE,
            title_align="left",
            padding=(1, 2),
        )
    )


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def _highlight_winner(a_val, b_val, a_str: str, b_str: str, higher_is_better: bool = True):
    """Return (a_str, b_str) with the winning value wrapped in bold green."""
    try:
        if a_val is None or b_val is None:
            return a_str, b_str
        if a_val == b_val:
            return a_str, b_str
        a_wins = (a_val > b_val) if higher_is_better else (a_val < b_val)
        if a_wins:
            return f"[bold green]{a_str}[/bold green]", b_str
        else:
            return a_str, f"[bold green]{b_str}[/bold green]"
    except TypeError:
        return a_str, b_str


def show_comparison_table(a: dict, b: dict) -> None:
    table = Table(
        title=f"{a.get('flag_emoji','')} {a.get('name','?').upper()}  vs  "
              f"{b.get('flag_emoji','')} {b.get('name','?').upper()}",
        border_style=BORDER_STYLE,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Metric", style="bold cyan")
    table.add_column(a.get("name", "A"), justify="center")
    table.add_column(b.get("name", "B"), justify="center")

    pop_a, pop_b = a.get("population"), b.get("population")
    pop_a_s, pop_b_s = _highlight_winner(
        pop_a, pop_b, format_population(pop_a), format_population(pop_b)
    )
    table.add_row("Population", pop_a_s, pop_b_s)

    area_a, area_b = a.get("area_km2"), b.get("area_km2")
    area_a_s, area_b_s = _highlight_winner(
        area_a, area_b, format_area(area_a), format_area(area_b)
    )
    table.add_row("Area (km²)", area_a_s, area_b_s)

    table.add_row(
        "Currency",
        f"{a.get('currency_name','N/A')} ({a.get('currency_code','N/A')})",
        f"{b.get('currency_name','N/A')} ({b.get('currency_code','N/A')})",
    )
    table.add_row("Language", a.get("language", "N/A"), b.get("language", "N/A"))
    table.add_row("Continent", a.get("continent", "N/A"), b.get("continent", "N/A"))
    table.add_row(
        "Timezones",
        ", ".join(a.get("timezones") or []) or "N/A",
        ", ".join(b.get("timezones") or []) or "N/A",
    )

    borders_a = len(a.get("borders") or [])
    borders_b = len(b.get("borders") or [])
    borders_a_s, borders_b_s = _highlight_winner(
        borders_a, borders_b, str(borders_a), str(borders_b)
    )
    table.add_row("Borders Count", borders_a_s, borders_b_s)

    console.print(table)


# ---------------------------------------------------------------------------
# Rankings table
# ---------------------------------------------------------------------------

def show_rankings_table(title: str, rows: list[tuple]) -> None:
    """
    rows: list of (rank, flag_emoji, name, value_str)
    """
    table = Table(title=title, border_style=BORDER_STYLE, header_style="bold cyan")
    table.add_column("#", justify="right", style="bold cyan", width=3)
    table.add_column("Flag", justify="center", width=4)
    table.add_column("Country", style="white")
    table.add_column("Value", justify="right", style="bold green")

    for rank, flag, name, value in rows:
        table.add_row(str(rank), flag, name, str(value))

    console.print(table)


# ---------------------------------------------------------------------------
# Currency conversion panel
# ---------------------------------------------------------------------------

def show_conversion(amount: float, from_code: str, to_code: str, result: float, rate=None, date=None) -> None:
    body = Text(justify="center")
    body.append(f"{format_number(amount)} {from_code}\n\n", style="bold white")
    body.append("↓\n\n", style="bold cyan")
    body.append(f"{format_number(round(result, 2))} {to_code}", style="bold green")

    subtitle = ""
    if rate is not None:
        subtitle += f"Rate: 1 {from_code} = {rate:.4f} {to_code}"
    if date:
        subtitle += f"  |  Date: {date}"

    console.print(
        Panel(
            Align.center(body),
            title="💱 Currency Conversion",
            subtitle=subtitle if subtitle else None,
            border_style=BORDER_STYLE,
        )
    )


# ---------------------------------------------------------------------------
# World clock panel
# ---------------------------------------------------------------------------

def show_world_clock(location: str, local_time: str, utc_offset: str) -> None:
    body = Text(justify="center")
    body.append(f"{location}\n\n", style="bold cyan")
    body.append(f"{local_time}\n\n", style="bold white")
    body.append(f"{utc_offset}", style="white")

    console.print(Panel(Align.center(body), title="🕒 World Clock", border_style=BORDER_STYLE))


# ---------------------------------------------------------------------------
# Learn / continent panel
# ---------------------------------------------------------------------------

def show_learn_panel(continent: str, num_countries: int, largest: dict, most_populous: dict) -> None:
    body = Text()
    body.append(f"{num_countries} Countries\n\n", style="bold white")
    body.append("Largest by Area\n", style="bold cyan")
    body.append(
        f"{largest.get('flag_emoji','')} {largest.get('name','N/A')} "
        f"({format_area(largest.get('area_km2'))})\n\n",
        style="white",
    )
    body.append("Most Populous\n", style="bold cyan")
    body.append(
        f"{most_populous.get('flag_emoji','')} {most_populous.get('name','N/A')} "
        f"({format_population(most_populous.get('population'))})\n",
        style="white",
    )

    console.print(Panel(body, title=f"🎓 {continent}", border_style=BORDER_STYLE))


# ---------------------------------------------------------------------------
# AI answer panel
# ---------------------------------------------------------------------------

def show_ai_answer(answer: str) -> None:
    console.print(Panel(answer, title="🌍 ATLAS AI", border_style=BORDER_STYLE, padding=(1, 2)))


# ---------------------------------------------------------------------------
# Suggestions ("did you mean")
# ---------------------------------------------------------------------------

def show_suggestions(query: str, suggestions: list[str]) -> None:
    if not suggestions:
        show_error(f"No country found matching '{query}'.")
        return
    body = Text()
    body.append(f"No exact match found for '{query}'.\n\n", style="white")
    body.append("Did you mean:\n", style="bold cyan")
    for s in suggestions:
        body.append(f"  • {s}\n", style="white")
    console.print(Panel(body, title="🔍 Did You Mean?", border_style="yellow"))


def show_title_banner() -> None:
    console.print(
        Panel(
            Align.center(Text("🌍 ATLAS — World Intelligence CLI", style="bold cyan")),
            border_style=BORDER_STYLE,
        )
    )
