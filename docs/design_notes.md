# Design Notes

- Focus on **learning** async FastAPI + WebSockets, not production readiness.
- Single responsibility:
  - Auth concerns live in `auth/auth.py`.
  - WebSocket protocol / routing in `sockets/stock_socket.py`.
  - State & broadcasting in `services/stock_service.py`.
- `datamodel-code-generator` makes regenerating models repeatable and explicit.
- Async IO is central:
  - Background task for ticker updates
  - WebSocket connections
  - Non-blocking broadcasts to all clients
