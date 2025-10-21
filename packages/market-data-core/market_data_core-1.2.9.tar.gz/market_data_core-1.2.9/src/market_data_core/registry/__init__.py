"""Registry contracts, protocols, and utilities.

This package provides:
- Provider/Sink registration (v1.1.0)
- Schema enforcement modes (v1.2.0 - Phase 11.1)
- Drift detection and reporting (v1.2.0 - Phase 11.1)
- Registry client protocols (v1.2.0 - Phase 11.1)
- Usage tracking (v1.2.0 - Phase 11.1)

Example:
    >>> from market_data_core.registry import EnforcementMode, get_enforcement_mode
    >>> mode = get_enforcement_mode()  # Reads from env
    >>> if mode == EnforcementMode.strict:
    ...     # Reject invalid payloads
    ...     pass
"""

# Existing v1.1.0 registry types
from market_data_core.registry.types import (
    Capability,
    ProviderSpec,
    SinkSpec,
)

# New v1.2.0 (Phase 11.1) types
from market_data_core.models.registry import EnforcementMode
from market_data_core.registry.protocols import (
    DriftDetector,
    EnforcementPolicy,
    RegistryClient,
    SchemaUsageTracker,
)
from market_data_core.registry.utils import (
    get_enforcement_mode,
    should_enforce_strict,
    should_log_warning,
)

__all__ = [
    # Existing v1.1.0
    "Capability",
    "ProviderSpec",
    "SinkSpec",
    # New v1.2.0 (Phase 11.1)
    "EnforcementMode",
    "RegistryClient",
    "DriftDetector",
    "EnforcementPolicy",
    "SchemaUsageTracker",
    "get_enforcement_mode",
    "should_enforce_strict",
    "should_log_warning",
]
