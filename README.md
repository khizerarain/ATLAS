# ATLAS

## Installation

```bash
pip install atlas-world-intel
```

Then run:

```bash
atlas
```

No cloning required.

ATLAS is a Python command-line experience for exploring the world from your terminal. It combines country data, rankings, currency conversion, travel tips, a geography quiz, and AI-powered explanations into a single polished dashboard.

![ATLAS demo](demo.gif)

> Animated demo placeholder — add a GIF named demo.gif to this folder to replace the placeholder.

## Development

```bash
git clone https://github.com/khizerarain/atlas
cd atlas
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python -m atlas.main
```

## Commands

| Command | Example | Description |
| --- | --- | --- |
| atlas country | atlas country japan | Show a Rich country profile with key facts |
| atlas compare | atlas compare france germany | Compare two countries side by side |
| atlas top | atlas top population | Show the top 10 countries by population, area, or borders |
| atlas convert | atlas convert 100 USD PKR | Convert currencies using live exchange rates |
| atlas time | atlas time japan | Show the current local time for a country |
| atlas quiz | atlas quiz | Run a 10-question geography quiz |
| atlas learn | atlas learn africa | Show continent-level highlights |
| atlas ask | atlas ask What is the capital of Morocco? | Ask ATLAS AI a geography question |
| atlas travel | atlas travel japan | Show travel tips and emergency info |

## Tech Stack

- Python
- Typer
- Rich
- RestCountries API
- OpenAI
- exchangerate.host

## Environment Variables

- OPENAI_API_KEY: Required for AI answers via the atlas ask command.
- EXCHANGE_API_KEY: Optional for exchange-rate integrations; the default free endpoint is used when it is not present.

## License

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
