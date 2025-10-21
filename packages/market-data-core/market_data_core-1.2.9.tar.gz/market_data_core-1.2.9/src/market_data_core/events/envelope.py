"""EventEnvelope: Generic container for events with metadata.

The EventEnvelope wraps any Pydantic model (payload) with:
- id: Opaque identifier from the event bus backend
- key: Optional partitioning/routing key
- ts: Timestamp when event was created
- meta: EventMeta with schema_id, track (v1/v2), and optional headers
- payload: The actual event data (FeedbackEvent, RateAdjustment, etc.)

This allows the event bus to be polymorphic over any Pydantic model while
preserving schema versioning and metadata.
"""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class EventMeta(BaseModel):
    """Metadata for an event envelope.

    Attributes:
        schema_id: Fully qualified schema identifier (e.g., "telemetry.FeedbackEvent")
        track: Schema track version ("v1" or "v2")
        headers: Optional key-value headers for routing, auth, etc.
        hash: Optional SHA256 content hash for integrity verification
    """

    schema_id: str = Field(..., description="Schema identifier (e.g., 'telemetry.FeedbackEvent')")
    track: Literal["v1", "v2"] = Field(default="v1", description="Schema track version")
    headers: dict[str, str] = Field(default_factory=dict, description="Optional headers")
    hash: str | None = Field(default=None, description="SHA256 content hash (optional)")


class EventEnvelope(BaseModel, Generic[T]):
    """Generic envelope for any event payload with metadata.

    The envelope is backend-agnostic and can be used with InMemoryBus,
    RedisStreamsBus, or any other EventBus implementation.

    Attributes:
        id: Opaque identifier from backend (e.g., Redis message ID)
        key: Optional partitioning/routing key
        ts: Unix timestamp when event was published
        meta: Event metadata (schema_id, track, headers, hash)
        payload: The actual event data (generic type T)

    Example:
        >>> from market_data_core.telemetry import FeedbackEvent
        >>> feedback = FeedbackEvent(coordinator_id="bars_1", ...)
        >>> envelope = EventEnvelope(
        ...     id="12345",
        ...     ts=time.time(),
        ...     meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1"),
        ...     payload=feedback
        ... )
    """

    id: str = Field(..., description="Opaque id from backend (e.g., Redis message ID)")
    key: str | None = Field(default=None, description="Optional partitioning/routing key")
    ts: float = Field(..., description="Unix timestamp when event was published")
    meta: EventMeta = Field(..., description="Event metadata")
    payload: T = Field(..., description="The actual event data")

    class Config:
        arbitrary_types_allowed = True

