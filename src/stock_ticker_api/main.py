from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from .auth.auth import basic_auth_dep
from .sockets.stock_socket import router as ws_router
from .services.stock_service import stock_service

app = FastAPI(
    title="Stock Ticker API",
    version="0.1.0",
    summary="Demo FastAPI app with Basic auth, WebSockets, and Pydantic v2 models.",
)

# Include WebSocket routes
app.include_router(ws_router)

@app.on_event("startup")
async def on_startup() -> None:
    # Start background async price update loop
    stock_service.start()

@app.on_event("shutdown")
async def on_shutdown() -> None:
    await stock_service.stop()

@app.get("/health")
async def health(_: str = Depends(basic_auth_dep)) -> JSONResponse:
    return JSONResponse({"status": "ok"})
