from __future__ import annotations

import json
import random
from pathlib import Path

import typer
from rich.table import Table

from core.display import show_error, show_loading, show_success

app = typer.Typer(help="Take a geography quiz")


def _load_questions() -> list[dict]:
    data_path = Path(__file__).resolve().parent.parent / "data" / "quiz_questions.json"
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@app.callback(invoke_without_command=True)
def run_quiz() -> None:
    questions = _load_questions()
    if len(questions) < 10:
        show_error("Not enough quiz questions available.")
        return

    random.shuffle(questions)
    selected = questions[:10]
    score = 0
    results = []

    for idx, item in enumerate(selected, start=1):
        with show_loading(f"Question {idx}/10"):
            pass
        answer = typer.prompt(f"{idx}. {item['question']}")
        if str(answer).strip().lower() == str(item["answer"]).strip().lower():
            score += 1
            results.append((item["question"], answer, item["answer"], "✓"))
        else:
            results.append((item["question"], answer, item["answer"], "✗"))

    if score == 10:
        rating = "🌍 World Expert"
    elif score >= 7:
        rating = "✈️ Seasoned Traveler"
    elif score >= 4:
        rating = "🗺️ Explorer"
    else:
        rating = "📚 Keep Studying"

    table = Table(title=f"Quiz Score: {score}/10 — {rating}", border_style="cyan", header_style="bold cyan")
    table.add_column("#", justify="right")
    table.add_column("Question")
    table.add_column("Your Answer")
    table.add_column("Correct Answer")
    table.add_column("Result")
    for i, (question, your_answer, correct_answer, result) in enumerate(results, start=1):
        table.add_row(str(i), question, your_answer, correct_answer, result)

    from rich.console import Console

    Console().print(table)
    show_success(f"You scored {score}/10 — {rating}")
