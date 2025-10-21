"""Contract registry and versioning support.

Phase 9.0: Schema evolution and version negotiation.
"""

from .compat import (
    compatible,
    get_compatibility_advice,
    is_backward_compatible_change,
    negotiate,
)
from .registry import SchemaMeta, augment_schema, compute_sha256, make_index, write_index

__all__ = [
    # Registry
    "SchemaMeta",
    "make_index",
    "write_index",
    "augment_schema",
    "compute_sha256",
    # Compatibility
    "compatible",
    "negotiate",
    "is_backward_compatible_change",
    "get_compatibility_advice",
]

