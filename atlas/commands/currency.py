from __future__ import annotations

import typer

from atlas.core.api import check_internet, convert_currency
from atlas.core.display import show_conversion, show_error, show_no_internet

app = typer.Typer(help="Convert currencies")


@app.callback(invoke_without_command=True)
def convert_currency_command(
    amount: float = typer.Argument(..., help="Amount to convert"),
    from_code: str = typer.Argument(..., help="Source currency code"),
    to_code: str = typer.Argument(..., help="Destination currency code"),
) -> None:
    if amount <= 0:
        show_error("Amount must be greater than zero.")
        raise typer.Exit(code=1)

    if not check_internet():
        show_no_internet()
        return

    result = convert_currency(amount, from_code, to_code)
    if not result:
        show_error(
            f"Unable to convert {from_code} to {to_code}. Try valid codes such as USD, EUR, GBP, JPY, PKR."
        )
        return

    show_conversion(
        result["amount"],
        result["from"],
        result["to"],
        result["result"],
        rate=result.get("rate"),
        date=result.get("date"),
    )
