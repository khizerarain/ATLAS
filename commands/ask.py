from __future__ import annotations

import os

import typer

from core.api import ask_ai, check_internet
from core.display import show_ai_answer, show_error, show_no_internet, show_warning

app = typer.Typer(help="Ask ATLAS AI")


@app.callback(invoke_without_command=True)
def ask_ai_command(question: str = typer.Argument(..., help="Question to ask ATLAS")) -> None:
    if not question:
        show_error("Please provide a question.")
        raise typer.Exit(code=1)

    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_key_here":
        show_warning("OpenAI API key is not configured. Add it to .env to enable AI answers.")
        return

    if not check_internet():
        show_no_internet()
        return

    answer = ask_ai(question)
    if answer:
        show_ai_answer(answer)
    else:
        show_error("ATLAS AI could not answer that question right now.")
