"""Event bus adapters for different backends.

Available adapters:
- InMemoryBus: Fast in-process bus for testing
- RedisStreamsBus: Production-ready bus backed by Redis Streams
"""

from .inmem import InMemoryBus

try:
    from .redis_streams import RedisStreamsBus

    __all__ = ["InMemoryBus", "RedisStreamsBus"]
except ImportError:
    # Redis not available
    __all__ = ["InMemoryBus"]

