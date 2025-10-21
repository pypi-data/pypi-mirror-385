"""In-memory event bus implementation for testing.

InMemoryBus is a simple, fast, in-process event bus that uses asyncio.Queue
for each stream. It's perfect for unit tests and local development.

Features:
- No external dependencies
- Zero latency
- Perfect delivery guarantees (no network failures)
- AsyncIterator for backpressure-aware streaming

Limitations:
- Not distributed (single process only)
- No persistence (events lost on restart)
- No consumer group load balancing (one queue per group)
- ack/fail are no-ops (no delivery tracking)

Usage:
    bus = InMemoryBus()
    
    # Publish
    feedback = FeedbackEvent(...)
    envelope_id = await bus.publish("telemetry.feedback", feedback)
    
    # Subscribe
    async for envelope in bus.subscribe("telemetry.feedback", group="test", consumer="c1"):
        # Process envelope
        await bus.ack("telemetry.feedback", envelope.id)
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import defaultdict
from collections.abc import AsyncIterator, Mapping
from typing import Any, TypeVar

from pydantic import BaseModel

from ..envelope import EventEnvelope, EventMeta
from ..observability import EventBusObserver

T = TypeVar("T", bound=BaseModel)


class InMemoryBus:
    """In-memory event bus using asyncio.Queue for each stream.

    This implementation is optimized for testing and local development.
    It provides perfect delivery guarantees but is not suitable for
    production (not distributed, no persistence).

    Attributes:
        _streams: Dict mapping stream names to asyncio.Queue instances
        _consumer_groups: Dict tracking consumer groups (for future use)
    """

    def __init__(self, enable_observability: bool = True):
        """Initialize the in-memory bus.
        
        Args:
            enable_observability: Whether to enable metrics and logging
        """
        self._streams: dict[str, asyncio.Queue[EventEnvelope[Any]]] = defaultdict(
            asyncio.Queue
        )
        self._consumer_groups: dict[str, set[str]] = defaultdict(set)
        self._observer = EventBusObserver("inmem") if enable_observability else None

    async def publish(
        self,
        stream: str,
        value: T,
        *,
        key: str | None = None,
    ) -> str:
        """Publish an event to a stream.

        Args:
            stream: Stream name (e.g., "telemetry.feedback")
            value: Event payload (Pydantic model)
            key: Optional partitioning key

        Returns:
            Generated envelope ID (UUID)

        Example:
            >>> bus = InMemoryBus()
            >>> feedback = FeedbackEvent(...)
            >>> envelope_id = await bus.publish("telemetry.feedback", feedback)
        """
        # Extract schema_id from model (use model name as fallback)
        schema_id = getattr(
            value, "__schema_id__", f"{value.__class__.__module__}.{value.__class__.__name__}"
        )
        if schema_id.startswith("market_data_core."):
            schema_id = schema_id.replace("market_data_core.", "")

        # Observability: track publish start
        start_time = self._observer.on_publish_start(stream, schema_id) if self._observer else time.time()

        try:
            # Generate unique ID
            envelope_id = uuid.uuid4().hex

            # Create envelope
            envelope = EventEnvelope(
                id=envelope_id,
                key=key,
                ts=time.time(),
                meta=EventMeta(schema_id=schema_id, track="v1"),  # Default to v1
                payload=value,
            )

            # Add to queue (non-blocking in inmem)
            await self._streams[stream].put(envelope)

            # Observability: track success
            if self._observer:
                self._observer.on_publish_success(stream, envelope_id, start_time)

            return envelope_id

        except Exception as e:
            # Observability: track error
            if self._observer:
                self._observer.on_publish_error(stream, e, start_time)
            raise

    async def subscribe(
        self,
        stream: str,
        *,
        group: str,
        consumer: str,
    ) -> AsyncIterator[EventEnvelope[Any]]:
        """Subscribe to a stream and yield envelopes.

        Args:
            stream: Stream name (e.g., "telemetry.feedback")
            group: Consumer group name
            consumer: Consumer instance name

        Yields:
            EventEnvelope with payload

        Example:
            >>> bus = InMemoryBus()
            >>> async for envelope in bus.subscribe("telemetry.feedback", group="test", consumer="c1"):
            ...     print(envelope.payload)
            ...     await bus.ack("telemetry.feedback", envelope.id)
        """
        # Track consumer group (for future use)
        group_key = f"{stream}:{group}"
        self._consumer_groups[group_key].add(consumer)

        # Get queue for stream
        queue = self._streams[stream]

        # Yield envelopes forever
        while True:
            envelope = await queue.get()
            
            # Observability: track consume
            if self._observer:
                self._observer.on_consume_success(stream, envelope.id)
            
            yield envelope

    async def ack(self, stream: str, envelope_id: str) -> None:
        """Acknowledge successful processing of an envelope.

        In InMemoryBus, this is a no-op since we don't track delivery state.

        Args:
            stream: Stream name
            envelope_id: Envelope ID to acknowledge
        """
        # Observability: track ACK
        if self._observer:
            self._observer.on_ack(stream, envelope_id)
        pass  # No-op for in-memory

    async def fail(self, stream: str, envelope_id: str, reason: str) -> None:
        """Mark an envelope as failed.

        In InMemoryBus, this is a no-op. A real implementation would
        move the message to a DLQ or retry queue.

        Args:
            stream: Stream name
            envelope_id: Envelope ID to fail
            reason: Failure reason
        """
        # Observability: track NACK
        if self._observer:
            self._observer.on_nack(stream, envelope_id, reason)
        pass  # No-op for in-memory

    async def health(self) -> Mapping[str, str]:
        """Return backend health status.

        Returns:
            Dict with backend info and status

        Example:
            >>> bus = InMemoryBus()
            >>> health = await bus.health()
            >>> assert health["status"] == "ok"
        """
        health_data = {
            "backend": "inmem",
            "status": "ok",
            "streams": str(len(self._streams)),
            "consumer_groups": str(len(self._consumer_groups)),
        }
        
        # Add metrics if observer is enabled
        if self._observer:
            metrics = self._observer.get_metrics_summary()
            health_data.update({
                "published": str(metrics["published"]),
                "consumed": str(metrics["consumed"]),
                "error_rate": str(metrics["error_rate"]),
            })
        
        return health_data

    def _get_stats(self) -> dict[str, Any]:
        """Get internal stats for debugging/testing.

        Returns:
            Dict with stream sizes and consumer group info
        """
        return {
            "streams": {
                name: queue.qsize() for name, queue in self._streams.items()
            },
            "consumer_groups": dict(self._consumer_groups),
        }

