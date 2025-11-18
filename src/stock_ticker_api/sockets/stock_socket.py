import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Header, Query

from ..auth.auth import parse_basic_auth_header, verify_user
from ..services.stock_service import stock_service

router = APIRouter()

@router.websocket("/ws/ticker")
async def websocket_ticker_endpoint(
    websocket: WebSocket,
    authorization: Optional[str] = Header(default=None),
    username: Optional[str] = Query(default=None),
    password: Optional[str] = Query(default=None),
) -> None:
    """Authenticated WebSocket endpoint streaming live stock updates.

    Any connection must provide valid Basic credentials, either via header
    or query parameters. Once connected, the server periodically pushes
    ticker batches to all clients using async IO.
    """
    # --- Authenticate ---
    creds = parse_basic_auth_header(authorization) if authorization else None
    if creds is None and username and password:
        creds = (username, password)

    if not creds or not verify_user(*creds):
        # Accept then close to send a clear close code.
        await websocket.accept()
        await websocket.close(code=4403)  # 4403: Forbidden (custom)
        return

    await websocket.accept()
    await stock_service.register(websocket)

    try:
        # Keep the connection alive; updates are pushed from the background task.
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        await stock_service.unregister(websocket)
    except Exception:
        await stock_service.unregister(websocket)
        await websocket.close()
