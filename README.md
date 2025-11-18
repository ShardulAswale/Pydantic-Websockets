# stock_ticker_api

A tiny but complete FastAPI project demonstrating:

- Modern Python packaging with pyproject.toml
- Clean src/ layout
- HTTP Basic authentication (username/password)
- Real-time WebSocket endpoint for stock updates
- Pydantic v2 models generated via datamodel-code-generator
- Async IO with background tasks and WebSockets
- Dependency management with a virtual environment and requirements.txt
- HTTP + WebSocket API for stock tickers
- Pytest example for the WebSocket

Tested with Python 3.13.9 (requires Python >= 3.13).

## Quickstart (Windows / macOS / Linux)

# 1) Create & activate a virtualenv (Python 3.13.9)
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 2) Upgrade pip
pip install -U pip

# 3) Install project + dev dependencies (editable)
pip install -e .[dev]

# 4) (Re)generate Pydantic v2 models from JSON Schema
python -m scripts.generate_models

# 5) Freeze exact dependencies
pip freeze > requirements.txt

# 6) Run the API (async via Uvicorn, ASGI server)
uvicorn stock_ticker_api.main:app --reload

## HTTP API (Basic Auth Required)

- GET /health — health check
- GET /me — authenticated username
- GET /tickers — list all tickers
- GET /tickers/{symbol} — get a single ticker
- POST /tickers/{symbol}/reset — reset ticker

Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

## Authentication

Default credentials:

- Username: admin
- Password: changeme

### HTTP Example:
curl -u admin:changeme http://127.0.0.1:8000/health

## WebSocket

Authenticate with either:

1. Authorization: Basic <base64("admin:changeme")>
2. Query params (demo only): ?username=admin&password=changeme

### JavaScript Example:
const ws = new WebSocket(
  "ws://127.0.0.1:8000/ws/ticker?username=admin&password=changeme"
);
ws.onmessage = (event) => {
  console.log("Ticker update:", JSON.parse(event.data));
};

## About the Data Model

stock_model.py is generated from:
src/stock_ticker_api/models/schemas/stock_schema.json

Run generator:
python -m scripts.generate_models

Generated Pydantic v2 model fields:
- symbol: str
- price: float
- change: float
- percent_change: float
- last_updated: datetime

## Notes

- Async IO used everywhere:
  - FastAPI async routes
  - WebSocket handler
  - Background broadcasting task (StockService)
- In-memory ticker store (no DB, simpler for learning)
- Designed for learning real-time API patterns
