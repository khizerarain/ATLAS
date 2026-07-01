"""
core/api.py

All external API calls live here:
  - RestCountries API (country data)
  - exchangerate.host (currency conversion)
  - OpenAI (AI Q&A)

Nothing in this module should crash the program. Every network call is wrapped
in try/except and returns None (or an empty structure) on failure so callers
can render a friendly error panel instead of a traceback.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from thefuzz import process

REST_COUNTRIES_BASE = "https://restcountries.com/v3.1"
REST_COUNTRIES_LEGACY_BASE = "https://restcountries.com/v3"
EXCHANGE_RATE_BASE = "https://api.exchangerate.host"
REQUEST_TIMEOUT = 10

# In-memory session cache so we don't hammer the API on every command.
_ALL_COUNTRIES_CACHE: list[dict] | None = None


class APIError(Exception):
    """Raised for any recoverable API/network failure."""


def _normalize_country(raw: dict) -> dict:
    """Flatten a raw RestCountries record into ATLAS's internal schema."""
    name_info = raw.get("name") or {}
    name = name_info.get("common") or name_info.get("official") or raw.get("name") or "Unknown"

    capital_list = raw.get("capital") or []
    capital = capital_list[0] if capital_list else "N/A"

    population = raw.get("population")
    area_km2 = raw.get("area")

    currencies = raw.get("currencies") or {}
    currency_code = next(iter(currencies), None)
    currency_name = currencies[currency_code]["name"] if currency_code else "N/A"

    languages = raw.get("languages") or {}
    language = next(iter(languages.values()), "N/A")

    continent = raw.get("region", "N/A")
    subregion = raw.get("subregion", "")
    flag_emoji = raw.get("flag", "")
    tld_list = raw.get("tld") or []
    tld = tld_list[0] if tld_list else "N/A"
    timezones = raw.get("timezones") or []
    borders = raw.get("borders") or []
    cca2 = raw.get("cca2", "")
    cca3 = raw.get("cca3", "")
    latlng = raw.get("latlng") or []
    flag_png = raw.get("flags", {}).get("png", "")

    return {
        "name": name,
        "official_name": name_info.get("official", name),
        "capital": capital,
        "population": population,
        "area_km2": area_km2,
        "currency_name": currency_name,
        "currency_code": currency_code or "N/A",
        "language": language,
        "continent": continent,
        "subregion": subregion,
        "flag_emoji": flag_emoji,
        "flag_png": flag_png,
        "tld": tld,
        "timezones": timezones,
        "borders": borders,
        "cca2": cca2,
        "cca3": cca3,
        "latlng": latlng,
        "independent": raw.get("independent", None),
        "unMember": raw.get("unMember", None),
        "gdp": None,
    }


def get_all_countries(force_refresh: bool = False) -> list[dict]:
    """Fetch (and cache) all countries, normalized into the ATLAS schema."""
    global _ALL_COUNTRIES_CACHE
    if _ALL_COUNTRIES_CACHE is not None and not force_refresh:
        return _ALL_COUNTRIES_CACHE

    for base in (REST_COUNTRIES_BASE, REST_COUNTRIES_LEGACY_BASE):
        try:
            resp = requests.get(f"{base}/all", timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            if isinstance(payload, dict) and payload.get("success") is False:
                continue
            raw_list = payload if isinstance(payload, list) else payload.get("data", [])
            if not isinstance(raw_list, list):
                continue
            normalized = [_normalize_country(c) for c in raw_list if isinstance(c, dict)]
            _ALL_COUNTRIES_CACHE = normalized
            return normalized
        except requests.exceptions.RequestException:
            continue
        except ValueError:
            continue

    fallback_path = Path(__file__).resolve().parent.parent / "data" / "country_fallback.json"
    if fallback_path.exists():
        try:
            with fallback_path.open("r", encoding="utf-8") as handle:
                raw_list = json.load(handle)
            normalized = [_normalize_country(c) for c in raw_list if isinstance(c, dict)]
            _ALL_COUNTRIES_CACHE = normalized
            return normalized
        except (json.JSONDecodeError, OSError):
            return []

    return []


def get_country(name: str) -> dict | None:
    """
    Look up a single country by (fuzzy) name.
    Tries an exact/direct API lookup first, then falls back to fuzzy matching
    against the cached full country list.
    """
    if not name:
        return None

    for base in (REST_COUNTRIES_BASE, REST_COUNTRIES_LEGACY_BASE):
        try:
            resp = requests.get(
                f"{base}/name/{name}",
                params={"fullText": "false"},
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 200:
                payload = resp.json()
                if isinstance(payload, list) and payload:
                    return _normalize_country(payload[0])
                if isinstance(payload, dict):
                    if isinstance(payload.get("data"), list) and payload["data"]:
                        return _normalize_country(payload["data"][0])
                    if payload.get("success") is False:
                        continue
                    return _normalize_country(payload)
        except requests.exceptions.RequestException:
            continue
        except ValueError:
            continue

    fallback_path = Path(__file__).resolve().parent.parent / "data" / "country_fallback.json"
    if fallback_path.exists():
        try:
            with fallback_path.open("r", encoding="utf-8") as handle:
                fallback = json.load(handle)
            for item in fallback:
                if item.get("name", {}).get("common", "").lower() == name.lower():
                    return _normalize_country(item)
        except (json.JSONDecodeError, OSError):
            pass

    # Fall back to fuzzy match against cached list (also works offline-ish
    # if the cache was already warmed, and gives better suggestions).
    all_countries = get_all_countries()
    if not all_countries:
        return None

    names = [c["name"] for c in all_countries]
    match = process.extractOne(name, names)
    if match and match[1] >= 60:
        matched_name = match[0]
        for c in all_countries:
            if c["name"] == matched_name:
                return c
    return None


def search_countries(query: str, limit: int = 5) -> list[dict]:
    """Fuzzy-search all countries by name; returns up to `limit` best matches."""
    all_countries = get_all_countries()
    if not all_countries or not query:
        return []

    names = [c["name"] for c in all_countries]
    matches = process.extract(query, names, limit=limit)
    result = []
    for matched_name, score in matches:
        if score < 40:
            continue
        for c in all_countries:
            if c["name"] == matched_name:
                result.append(c)
                break
    return result


def suggest_countries(query: str, limit: int = 3) -> list[str]:
    """Return just the names of the top fuzzy matches, for 'did you mean' UX."""
    matches = search_countries(query, limit=limit)
    return [m["name"] for m in matches]


def convert_currency(amount: float, from_code: str, to_code: str) -> dict | None:
    """
    Convert an amount between two currency codes using exchangerate.host.
    Returns a dict: {"amount": float, "from": str, "to": str, "result": float,
                      "rate": float, "date": str} or None on failure.
    """
    from_code = (from_code or "").upper().strip()
    to_code = (to_code or "").upper().strip()
    if not from_code or not to_code:
        return None

    try:
        resp = requests.get(
            f"{EXCHANGE_RATE_BASE}/convert",
            params={"from": from_code, "to": to_code, "amount": amount},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", True) and "result" not in data:
            return None
        result = data.get("result")
        if result is None:
            return None
        info = data.get("info", {})
        rate = info.get("rate")
        date = data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        return {
            "amount": amount,
            "from": from_code,
            "to": to_code,
            "result": result,
            "rate": rate,
            "date": date,
        }
    except requests.exceptions.RequestException:
        return None
    except ValueError:
        return None


def ask_ai(question: str, api_key: str | None = None) -> str | None:
    """
    Send a question to OpenAI and return the answer text.
    Returns None if the call fails or no API key is configured.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ATLAS, a world geography and geopolitics expert. "
                        "Answer questions about countries, economies, cultures, and "
                        "global affairs concisely in 3-5 sentences."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def check_internet(timeout: int = 5) -> bool:
    """Quick connectivity check used to gracefully degrade live-data commands."""
    try:
        requests.get(REST_COUNTRIES_BASE, timeout=timeout)
        return True
    except requests.exceptions.RequestException:
        return False
