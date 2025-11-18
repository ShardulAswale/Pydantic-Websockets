# stock_ticker_api

A tiny but complete FastAPI project demonstrating:

- Modern Python packaging with `pyproject.toml`
- Clean `src/` layout
- HTTP Basic authentication (username/password)
- Real-time WebSocket endpoint for stock updates
- Pydantic **v2** model generated via `datamodel-code-generator`
- Dependency management with a virtual environment and `requirements.txt`
- Async IO with background tasks and WebSockets
- Pytest example for the WebSocket

Tested with **Python 3.13.9** (but should work with any Python >= 3.13).

## Quickstart (Windows / macOS / Linux)

```bash
# 1) Create & activate a virtualenv (Python 3.13.9)
python -m venv .venv
# On macOS / Linux
source .venv/bin/activate
# On Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 2) Upgrade pip
pip install -U pip

# 3) Install project + dev dependencies (editable)
pip install -e .[dev]

# 4) (Re)generate Pydantic models from JSON Schema
python -m scripts.generate_models

# 5) Freeze exact dependencies
pip freeze > requirements.txt

# 6) Run the API (async via Uvicorn, ASGI server)
uvicorn stock_ticker_api.main:app --reload
```

## Authentication

- Default credentials:
  - **Username:** `admin`
  - **Password:** `changeme`

HTTP routes and WebSocket connections both require authentication.

### HTTP

```bash
curl -u admin:changeme http://127.0.0.1:8000/health
```

### WebSocket

You can authenticate either via:

1. `Authorization: Basic <base64("admin:changeme")>` header, or
2. Query parameters `?username=admin&password=changeme` (for learning/demo only).

Example (JavaScript):

```js
const ws = new WebSocket(
  "ws://127.0.0.1:8000/ws/ticker?username=admin&password=changeme"
);

ws.onmessage = (event) => {
  const payload = JSON.parse(event.data);
  console.log("Ticker update:", payload);
};
```

## Notes

- `stock_model.py` is generated from `models/schemas/stock_schema.json` using
  `datamodel-code-generator` targeting **Pydantic v2**.
- Async IO is used throughout:
  - FastAPI async routes
  - WebSocket handler
  - Background broadcasting task (`StockService`).
- In-memory store only; no database (simpler for learning).
