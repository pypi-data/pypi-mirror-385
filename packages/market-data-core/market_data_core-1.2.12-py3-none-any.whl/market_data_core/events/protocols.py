"""Protocol interfaces for the event bus.

These protocols define the contract for event publishers, subscribers, and
the unified event bus. Any backend (InMemory, Redis, Kafka) must implement
these interfaces.

Design notes:
- AsyncIterator for subscribe() allows backpressure-aware streaming
- ack() and fail() provide at-least-once delivery semantics
- health() returns backend-specific status for monitoring
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Generic, Protocol, TypeVar

from .envelope import EventEnvelope

T = TypeVar("T", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


class EventPublisher(Protocol, Generic[T]):
    """Protocol for publishing events to a stream.

    Implementations must handle:
    - Serialization of payload
    - Envelope creation (id, ts, meta)
    - Backend-specific publishing (e.g., Redis XADD)
    - Idempotency key generation
    """

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
            value: Event payload (must be a Pydantic model)
            key: Optional partitioning/routing key

        Returns:
            Opaque envelope ID from backend

        Raises:
            PublishError: If publishing fails
        """
        ...


class EventSubscriber(Protocol, Generic[T_co]):
    """Protocol for subscribing to events from a stream.

    Implementations must handle:
    - Consumer group creation (if needed)
    - Deserialization of payload
    - Envelope reconstruction
    - DLQ handling for poison pills
    """

    async def subscribe(
        self,
        stream: str,
        *,
        group: str,
        consumer: str,
    ) -> AsyncIterator[EventEnvelope[T_co]]:
        """Subscribe to a stream and yield envelopes.

        Args:
            stream: Stream name (e.g., "telemetry.feedback")
            group: Consumer group name (for load balancing)
            consumer: Consumer instance name (unique within group)

        Yields:
            EventEnvelope with deserialized payload

        Raises:
            SubscribeError: If subscription fails
        """
        ...

    async def ack(self, stream: str, envelope_id: str) -> None:
        """Acknowledge successful processing of an envelope.

        Args:
            stream: Stream name
            envelope_id: Envelope ID to acknowledge

        Raises:
            AckError: If acknowledgement fails
        """
        ...

    async def fail(self, stream: str, envelope_id: str, reason: str) -> None:
        """Mark an envelope as failed and optionally move to DLQ.

        Args:
            stream: Stream name
            envelope_id: Envelope ID to fail
            reason: Human-readable failure reason

        Raises:
            FailError: If failure handling fails
        """
        ...


class EventBus(EventPublisher[T], EventSubscriber[T_co], Protocol):
    """Unified event bus protocol combining publish and subscribe.

    This is the main interface for interacting with the event bus.
    """

    async def health(self) -> Mapping[str, str]:
        """Return backend health status.

        Returns:
            Dictionary with backend-specific health info (e.g., {"backend": "redis", "status": "ok"})

        Raises:
            HealthCheckError: If health check fails
        """
        ...

