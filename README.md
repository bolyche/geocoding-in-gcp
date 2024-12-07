# Overview

## Structure

- Data has an IP CSV (& saves out to there)
- Docs has an architecture diagram
- Src has the project code
- Tests has tests

## Setup

Install uv `pip install uv` (or curl, [see docs](https://github.com/astral-sh/uv))

Run
```zsh
uv venv
source .venv/bin/activate
uv sync
```

### Test

Run
```zsh
pytest
```

### Geo

You need a token - Which currently resides in a variable in `src/geocode/geocoder.py`. Please update line 10 (in lieu of there being secrets tool) and/or set your API_TOKEN via env vars. This is for testing.

Run 
```zsh
python src/geocode/main.py
```

This prints/saves out geo data and outputs the failed calls to a separate file, both in data/


