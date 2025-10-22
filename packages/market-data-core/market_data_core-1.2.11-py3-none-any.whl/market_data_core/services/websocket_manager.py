import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from ..config import get_websocket_config
from ..models.market_data import MarketDepth, Quote
from ..models.portfolio import PortfolioUpdate
from ..utils.observability import metrics
from .ib_client import ib_client


class WebSocketManager:
    """
    WebSocket connection manager with backpressure handling.
    Implements per-client ring buffers and server-side rate limiting.
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, set[WebSocket]] = {
            "quotes": set(),
            "depth": set(),
            "portfolio": set(),
        }

        # Get configuration
        ws_config = get_websocket_config()

        # Per-client asyncio.Queue for backpressure
        self.client_queues: dict[WebSocket, asyncio.Queue[dict[str, Any]]] = {}
        self.max_queue_size = ws_config["max_queue_size"]
        self.max_messages_per_second = ws_config["max_messages_per_second"]

        # Per-symbol cache for instant snapshots to late joiners
        self.symbol_caches: dict[str, dict[str, Any]] = {
            "quotes": {},
            "depth": {},
            "portfolio": {},
        }

        # Rate limiting
        self.last_message_time: dict[WebSocket, float] = {}
        self.message_counts: dict[WebSocket, int] = {}

        # Background task for processing queues
        self._queue_processors: dict[WebSocket, asyncio.Task[None]] = {}

    async def connect(self, websocket: WebSocket, stream_type: str) -> None:
        """Connect a WebSocket client."""
        await websocket.accept()
        self.active_connections[stream_type].add(websocket)

        # Initialize client queue and rate limiting
        self.client_queues[websocket] = asyncio.Queue(maxsize=self.max_queue_size)
        self.last_message_time[websocket] = 0.0
        self.message_counts[websocket] = 0

        # Start queue processor task
        self._queue_processors[websocket] = asyncio.create_task(
            self._process_client_queue(websocket, stream_type)
        )

        # Send cached data if available (for late joiners)
        await self._send_cached_data(websocket, stream_type)

        # Register subscription with IBClient for rehydration
        subscription_id = f"{stream_type}_{id(websocket)}"
        ib_client.register_subscription(stream_type, subscription_id)

        # Update metrics
        metrics.ws_clients.labels(stream_type=stream_type).set(
            len(self.active_connections[stream_type])
        )

        logger.info(f"WebSocket connected to {stream_type} stream")

    def disconnect(self, websocket: WebSocket, stream_type: str) -> None:
        """Disconnect a WebSocket client."""
        self.active_connections[stream_type].discard(websocket)

        # Unregister subscription from IBClient
        subscription_id = f"{stream_type}_{id(websocket)}"
        ib_client.unregister_subscription(stream_type, subscription_id)

        # Cancel queue processor task
        if websocket in self._queue_processors:
            self._queue_processors[websocket].cancel()
            del self._queue_processors[websocket]

        # Cleanup client data
        if websocket in self.client_queues:
            del self.client_queues[websocket]
        if websocket in self.last_message_time:
            del self.last_message_time[websocket]
        if websocket in self.message_counts:
            del self.message_counts[websocket]

        # Update metrics
        metrics.ws_clients.labels(stream_type=stream_type).set(
            len(self.active_connections[stream_type])
        )

        logger.info(f"WebSocket disconnected from {stream_type} stream")

    async def _rate_limit_check(self, websocket: WebSocket) -> bool:
        """Check if client is within rate limits."""
        import time

        current_time = time.time()

        # Reset counter every second
        if current_time - self.last_message_time[websocket] >= 1.0:
            self.message_counts[websocket] = 0
            self.last_message_time[websocket] = current_time

        # Check rate limit
        if self.message_counts[websocket] >= self.max_messages_per_second:
            return False

        self.message_counts[websocket] += 1
        return True

    async def _process_client_queue(self, websocket: WebSocket, stream_type: str) -> None:
        """Process messages from client queue with backpressure."""
        queue = self.client_queues.get(websocket)
        if not queue:
            return

        try:
            while True:
                # Get message from queue (blocks if empty)
                message = await queue.get()

                # Check rate limit
                if not await self._rate_limit_check(websocket):
                    logger.warning(f"Rate limit exceeded for {stream_type} stream")
                    metrics.ws_dropped_messages.labels(stream_type=stream_type).inc()
                    continue

                # Send message
                await websocket.send_text(json.dumps(message, default=str))
                metrics.ws_messages_sent.labels(stream_type=stream_type).inc()

                # Mark task as done
                queue.task_done()

        except asyncio.CancelledError:
            logger.info(f"Queue processor cancelled for {stream_type} stream")
        except Exception as e:
            logger.error(f"Error processing queue for {stream_type} stream: {e}")
            # Remove the problematic connection
            for stream_type in self.active_connections:
                self.active_connections[stream_type].discard(websocket)

    async def _send_cached_data(self, websocket: WebSocket, stream_type: str) -> None:
        """Send cached data to late joiners."""
        cache = self.symbol_caches.get(stream_type, {})
        if cache:
            try:
                # Send the most recent data for each symbol
                for _symbol, data in cache.items():
                    await websocket.send_text(json.dumps(data, default=str))
                    metrics.ws_messages_sent.labels(stream_type=stream_type).inc()
            except Exception as e:
                logger.error(f"Error sending cached data: {e}")

    async def _queue_message(
        self, websocket: WebSocket, data: dict[str, Any], stream_type: str
    ) -> None:
        """Queue a message for a client with backpressure handling."""
        queue = self.client_queues.get(websocket)
        if not queue:
            return

        try:
            # Try to put message in queue (non-blocking)
            queue.put_nowait(data)
        except asyncio.QueueFull:
            # Queue is full, drop oldest message and add new one
            try:
                queue.get_nowait()  # Remove oldest
                queue.put_nowait(data)  # Add newest
                metrics.ws_dropped_messages.labels(stream_type=stream_type).inc()
                logger.warning(f"Queue full, dropped oldest message for {stream_type} stream")
            except asyncio.QueueEmpty:
                # Queue was emptied by another task, try again
                try:
                    queue.put_nowait(data)
                except asyncio.QueueFull:
                    # Still full, drop the message
                    metrics.ws_dropped_messages.labels(stream_type=stream_type).inc()
                    logger.warning(f"Queue still full, dropped message for {stream_type} stream")
        except Exception as e:
            logger.error(f"Error queuing message: {e}")

    async def _send_with_backpressure(
        self, websocket: WebSocket, data: dict[str, Any], stream_type: str
    ) -> None:
        """Send data with backpressure handling."""
        try:
            # Queue the message for processing
            await self._queue_message(websocket, data, stream_type)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Remove the problematic connection
            for stream_type in self.active_connections:
                self.active_connections[stream_type].discard(websocket)

    async def broadcast_quote(self, symbol: str, quote: Quote) -> None:
        """Broadcast quote data to all quote subscribers."""
        data = {
            "type": "quote",
            "symbol": symbol,
            "data": quote.model_dump(),
            "timestamp": quote.timestamp.isoformat(),
        }

        # Cache the data for late joiners
        self.symbol_caches["quotes"][symbol] = data

        for websocket in self.active_connections["quotes"].copy():
            try:
                await self._send_with_backpressure(websocket, data, "quotes")
            except WebSocketDisconnect:
                self.disconnect(websocket, "quotes")
            except Exception as e:
                logger.error(f"Error broadcasting quote: {e}")
                self.disconnect(websocket, "quotes")

    async def broadcast_depth(self, symbol: str, depth: MarketDepth) -> None:
        """Broadcast market depth data to all depth subscribers."""
        data = {
            "type": "depth",
            "symbol": symbol,
            "data": depth.model_dump(),
            "timestamp": depth.timestamp.isoformat(),
        }

        # Cache the data for late joiners
        self.symbol_caches["depth"][symbol] = data

        for websocket in self.active_connections["depth"].copy():
            try:
                await self._send_with_backpressure(websocket, data, "depth")
            except WebSocketDisconnect:
                self.disconnect(websocket, "depth")
            except Exception as e:
                logger.error(f"Error broadcasting depth: {e}")
                self.disconnect(websocket, "depth")

    async def broadcast_portfolio(self, account_id: str, portfolio: PortfolioUpdate) -> None:
        """Broadcast portfolio data to all portfolio subscribers."""
        data = {
            "type": "portfolio",
            "account_id": account_id,
            "data": portfolio.model_dump(),
            "timestamp": portfolio.timestamp.isoformat(),
        }

        # Cache the data for late joiners
        self.symbol_caches["portfolio"][account_id] = data

        for websocket in self.active_connections["portfolio"].copy():
            try:
                await self._send_with_backpressure(websocket, data, "portfolio")
            except WebSocketDisconnect:
                self.disconnect(websocket, "portfolio")
            except Exception as e:
                logger.error(f"Error broadcasting portfolio: {e}")
                self.disconnect(websocket, "portfolio")

    def get_stats(self) -> dict[str, Any]:
        """Get WebSocket connection statistics."""
        return {
            "total_connections": sum(
                len(connections) for connections in self.active_connections.values()
            ),
            "quotes_connections": len(self.active_connections["quotes"]),
            "depth_connections": len(self.active_connections["depth"]),
            "portfolio_connections": len(self.active_connections["portfolio"]),
            "max_queue_size": self.max_queue_size,
            "max_messages_per_second": self.max_messages_per_second,
            "cached_symbols": {
                stream_type: len(cache) for stream_type, cache in self.symbol_caches.items()
            },
            "active_queue_processors": len(self._queue_processors),
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
