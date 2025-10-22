"""Codecs for serializing/deserializing events.

JsonCodec is the primary codec, supporting:
- Pydantic model → JSON → bytes
- Schema track awareness (v1/v2)
- Content hashing for integrity
- Schema validation via Phase 9.0 registry
"""

from .json_codec import JsonCodec

__all__ = ["JsonCodec"]

