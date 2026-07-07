"""
core/utils.py

Shared helper utilities: fuzzy matching, number formatting, data normalization.
"""
from __future__ import annotations

from thefuzz import process


def fuzzy_find(name: str, choices: list[str], limit: int = 3, score_cutoff: int = 60):
    """
    Return a list of (choice, score) tuples for the best fuzzy matches of `name`
    within `choices`. Returns an empty list if nothing scores above the cutoff.
    """
    if not name or not choices:
        return []
    results = process.extract(name, choices, limit=limit)
    return [r for r in results if r[1] >= score_cutoff]


def format_population(n: int | float | None) -> str:
    """Format a population number as e.g. 123.4M or 1.4B."""
    if n is None:
        return "N/A"
    n = float(n)
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,.0f}"


def format_number(n: int | float | None) -> str:
    """Format a plain number with comma separators."""
    if n is None:
        return "N/A"
    try:
        return f"{n:,}"
    except (ValueError, TypeError):
        return str(n)


def format_area(n: float | None) -> str:
    """Format an area in km^2 with commas."""
    if n is None:
        return "N/A"
    return f"{n:,.0f} km²"


def safe_get(d: dict, *keys, default=None):
    """Safely walk a nested dict, returning `default` if any key is missing."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default
