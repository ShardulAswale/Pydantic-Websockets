# API Endpoints

## GET /health

- Requires HTTP Basic auth
- Returns `{ "status": "ok" }`

## WS /ws/ticker

- Requires authentication either via:
  - `Authorization: Basic <token>` header, or
  - `?username=&password=` query parameters (demo only)
- Sends periodic JSON messages of the form:

```json
{
  "type": "ticker_batch",
  "data": [
    {
      "symbol": "AAPL",
      "price": 181.23,
      "change": 0.42,
      "percent_change": 0.232,
      "last_updated": "2025-11-10T10:00:00Z"
    }
  ]
}
```
