# Architecture

- **FastAPI app** in `src/stock_ticker_api/main.py`
- **Authentication** via HTTP Basic in `auth/auth.py`
- **Data models** generated from JSON Schema:
  - `models/schemas/stock_schema.json` -> `models/stock_model.py`
  - Uses `datamodel-code-generator` targeting Pydantic v2
- **WebSocket** endpoint at `/ws/ticker` in `sockets/stock_socket.py`
- **Service layer** (`services/stock_service.py`):
  - Maintains in-memory stock prices
  - Runs an async background task to mutate prices periodically
  - Broadcasts batches to all connected WebSocket clients
