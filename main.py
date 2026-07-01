from __future__ import annotations

import os
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from commands.ask import ask_ai_command
from commands.compare import compare_countries
from commands.country import country_lookup
from commands.currency import convert_currency_command
from commands.learn import show_continent_summary
from commands.quiz import run_quiz
from commands.rankings import show_rankings
from commands.travel import travel_info
from core.display import (
    show_error,
    show_success,
    show_title_banner,
    show_warning,
)

console = Console()
app = typer.Typer(name="atlas", add_completion=False, help="ATLAS — World Intelligence CLI")

app.command("country")(country_lookup)
app.command("compare")(compare_countries)
app.command("top")(show_rankings)
app.command("convert")(convert_currency_command)
app.command("learn")(show_continent_summary)
app.command("quiz")(run_quiz)
app.command("ask")(ask_ai_command)
app.command("travel")(travel_info)


def _check_env() -> bool:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    exchange_key = os.getenv("EXCHANGE_API_KEY", "").strip()
    return bool(api_key and api_key != "your_key_here" and exchange_key and exchange_key != "your_key_here")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    load_dotenv()
    if ctx.invoked_subcommand is None:
        if not _check_env():
            show_warning(
                "Environment variables are not fully configured.\n"
                "Copy .env.example to .env and add API keys for live AI/currency features.",
                title="⚙️ Setup required",
            )
            return
        interactive_menu()


def interactive_menu() -> None:
    while True:
        show_title_banner()
        console.print()
        console.print("[bold cyan]1[/bold cyan] Country Lookup")
        console.print("[bold cyan]2[/bold cyan] Compare Countries")
        console.print("[bold cyan]3[/bold cyan] World Rankings")
        console.print("[bold cyan]4[/bold cyan] Currency Converter")
        console.print("[bold cyan]5[/bold cyan] World Clock")
        console.print("[bold cyan]6[/bold cyan] Geography Quiz")
        console.print("[bold cyan]7[/bold cyan] Learn by Continent")
        console.print("[bold cyan]8[/bold cyan] Ask ATLAS AI")
        console.print("[bold cyan]0[/bold cyan] Exit")
        console.print()

        choice = Prompt.ask("Select an option", console=console)
        if choice == "0":
            show_success("Thanks for exploring the world with ATLAS.")
            break

        if choice == "1":
            name = Prompt.ask("Country name", console=console)
            country_lookup(name)
        elif choice == "2":
            a = Prompt.ask("First country", console=console)
            b = Prompt.ask("Second country", console=console)
            compare_countries(a, b)
        elif choice == "3":
            metric = Prompt.ask("Metric (population/area/borders)", console=console)
            show_rankings(metric)
        elif choice == "4":
            amount = Prompt.ask("Amount", console=console)
            from_code = Prompt.ask("From currency", console=console).upper()
            to_code = Prompt.ask("To currency", console=console).upper()
            convert_currency_command(float(amount), from_code, to_code)
        elif choice == "5":
            country_name = Prompt.ask("Country", console=console)
            from commands.country import show_world_clock_command

            show_world_clock_command(country_name)
        elif choice == "6":
            run_quiz()
        elif choice == "7":
            continent = Prompt.ask("Continent", console=console)
            show_continent_summary(continent)
        elif choice == "8":
            question = Prompt.ask("Ask ATLAS", console=console)
            ask_ai_command(question)
        else:
            show_error("Please enter a valid option from 0-8.")


if __name__ == "__main__":
    app()
