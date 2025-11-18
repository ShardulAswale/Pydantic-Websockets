import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional

from fastapi import WebSocket

from ..models.stock_model import StockTicker


class StockService:
    """In-memory stock price store + async broadcaster."""

    def __init__(self) -> None:
        # initial prices
        self._initial_symbols: Dict[str, float] = {
            "AAPL": 180.00,
            "GOOG": 145.00,
            "MSFT": 380.00,
            "AMZN": 145.00,
        }
        # current mutable prices
        self._symbols: Dict[str, float] = dict(self._initial_symbols)

        self._clients: Set[WebSocket] = set()
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    # --------------------------------------------------------------------- #
    # Lifecycle for background loop
    # --------------------------------------------------------------------- #

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

    # --------------------------------------------------------------------- #
    # WebSocket client management
    # --------------------------------------------------------------------- #

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.add(ws)

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    # --------------------------------------------------------------------- #
    # Background price update loop
    # --------------------------------------------------------------------- #

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
            # random walk around the current price
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

    # --------------------------------------------------------------------- #
    # HTTP-style helpers for REST endpoints
    # --------------------------------------------------------------------- #

    def snapshot(self) -> List[StockTicker]:
        """
        Return a snapshot of all symbols as StockTicker models.

        For the snapshot we set change/percent_change to 0, since they are
        only meaningful in the streaming updates.
        """
        now = datetime.now(timezone.utc)
        return [
            StockTicker(
                symbol=sym,
                price=round(price, 2),
                change=0.0,
                percent_change=0.0,
                last_updated=now,
            )
            for sym, price in self._symbols.items()
        ]

    def get_ticker(self, symbol: str) -> Optional[StockTicker]:
        """
        Return a single ticker, or None if unknown.
        """
        price = self._symbols.get(symbol.upper())
        if price is None:
            return None
        now = datetime.now(timezone.utc)
        return StockTicker(
            symbol=symbol.upper(),
            price=round(price, 2),
            change=0.0,
            percent_change=0.0,
            last_updated=now,
        )

    def reset_ticker(self, symbol: str) -> StockTicker:
        """
        Reset a ticker back to its initial configured price.

        Raises KeyError if the symbol is not known.
        """
        key = symbol.upper()
        if key not in self._initial_symbols:
            raise KeyError(key)

        base_price = self._initial_symbols[key]
        self._symbols[key] = base_price

        now = datetime.now(timezone.utc)
        return StockTicker(
            symbol=key,
            price=round(base_price, 2),
            change=0.0,
            percent_change=0.0,
            last_updated=now,
        )


stock_service = StockService()
