import base64

def _basic_header(username: str, password: str) -> dict:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def test_health_requires_auth(client):
    r = client.get("/health", auth=("admin", "changeme"))
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_websocket_connect_and_receive(client):
    headers = _basic_header("admin", "changeme")
    with client.websocket_connect("/ws/ticker", headers=headers) as ws:
        msg = ws.receive_json()
        assert msg["type"] == "ticker_batch"
        assert isinstance(msg["data"], list)
        assert msg["data"], "expected at least one ticker entry"
        sample = msg["data"][0]
        assert {"symbol", "price", "change", "percent_change", "last_updated"} <= set(
            sample.keys()
        )
