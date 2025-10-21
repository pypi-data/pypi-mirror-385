"""Event Bus and Telemetry Fabric (Phase 10.0 - Pulse).

Provides a unified event bus abstraction for publishing/subscribing to
telemetry events (FeedbackEvent, RateAdjustment, etc.) across the market data stack.

Key concepts:
- EventEnvelope: Generic wrapper for any Pydantic event with metadata
- EventPublisher/EventSubscriber: Protocol interfaces for pub/sub
- JsonCodec: Serialize/deserialize events with schema validation
- InMemoryBus: Fast in-process bus for tests
- RedisStreamsBus: Production-ready bus backed by Redis Streams

Example:
    from market_data_core.events import EventBus, InMemoryBus, JsonCodec
    from market_data_core.telemetry import FeedbackEvent

    bus = InMemoryBus()
    codec = JsonCodec(track="v1")

    # Publish
    event = FeedbackEvent(coordinator_id="bars_1", ...)
    await bus.publish("telemetry.feedback", event)

    # Subscribe
    async for envelope in bus.subscribe("telemetry.feedback", group="pipeline", consumer="worker-1"):
        event = envelope.payload
        # Process event
        await bus.ack("telemetry.feedback", envelope.id)
"""

from .adapters import InMemoryBus
from .codecs import JsonCodec
from .envelope import EventEnvelope, EventMeta
from .factory import create_event_bus, create_test_bus
from .protocols import EventBus, EventPublisher, EventSubscriber

try:
    from .adapters import RedisStreamsBus

    __all__ = [
        # Core types
        "EventEnvelope",
        "EventMeta",
        # Protocols
        "EventBus",
        "EventPublisher",
        "EventSubscriber",
        # Adapters
        "InMemoryBus",
        "RedisStreamsBus",
        # Codec
        "JsonCodec",
        # Factories
        "create_event_bus",
        "create_test_bus",
    ]
except ImportError:
    # Redis not available
    __all__ = [
        # Core types
        "EventEnvelope",
        "EventMeta",
        # Protocols
        "EventBus",
        "EventPublisher",
        "EventSubscriber",
        # Adapters
        "InMemoryBus",
        # Codec
        "JsonCodec",
        # Factories
        "create_event_bus",
        "create_test_bus",
    ]

