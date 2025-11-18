import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, List, Set

from fastapi import WebSocket

from ..models.stock_model import StockTicker

class StockService:
    """In-memory stock price store + async broadcaster."""

    def __init__(self) -> None:
        self._symbols: Dict[str, float] = {
            "AAPL": 180.00,
            "GOOG": 145.00,
            "MSFT": 380.00,
            "AMZN": 145.00,
        }
        self._clients: Set[WebSocket] = set()
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    def start(self) -> None:
        """Start the background async loop that ticks prices and broadcasts."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="stock-service-loop")

    async def stop(self) -> None:
        """Stop the background loop gracefully."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.add(ws)

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def _run(self) -> None:
        """Main async loop: update prices and broadcast batches."""
        try:
            while True:
                await asyncio.sleep(2.0)
                updates = self._tick()
                await self._broadcast(updates)
        except asyncio.CancelledError:
            # graceful shutdown
            pass

    def _tick(self) -> List[StockTicker]:
        updates: List[StockTicker] = []
        now = datetime.now(timezone.utc)
        for sym, price in list(self._symbols.items()):
            delta = random.uniform(-1.0, 1.0)
            new_price = max(0.01, price + delta)
            change = new_price - price
            pct = (change / price) * 100.0 if price else 0.0
            self._symbols[sym] = new_price
            updates.append(
                StockTicker(
                    symbol=sym,
                    price=round(new_price, 2),
                    change=round(change, 2),
                    percent_change=round(pct, 3),
                    last_updated=now,
                )
            )
        return updates

    async def _broadcast(self, updates: List[StockTicker]) -> None:
        if not updates:
            return
        message = [u.model_dump(mode="json") for u in updates]
        payload = {"type": "ticker_batch", "data": message}

        # Copy connections while holding the lock, then send outside of it.
        async with self._lock:
            clients = list(self._clients)

        coros = [ws.send_json(payload) for ws in clients]
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

stock_service = StockService()
