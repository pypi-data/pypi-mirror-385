"""market_data_core - Core contracts for market data system.

This package provides provider-agnostic protocols, models, errors, and settings
that all market data implementations should use.

Core is the foundation - it has NO dependencies on other packages.
Other packages (pipeline, store, ibkr) depend on Core.

Version 1.0.0 - Contracts-only refactor
"""

# ============================================================================
# Protocols (interfaces)
# ============================================================================
from .protocols import (
    MarketDataProvider,
    PipelineRunner,
    Sink,
    Source,
    Transform,
)

# ============================================================================
# Models (DTOs)
# ============================================================================
from ._models import (
    # Instruments
    Instrument,
    # Market Data
    Bar,
    MarketDepth,
    PriceBar,  # Alias for Bar
    Quote,
    Trade,
    # Options
    OptionChain,
    OptionContract,  # Alias for OptionSnapshot
    OptionGreeks,
    OptionSnapshot,
    # Portfolio
    AccountSummary,
    Position,
    PortfolioUpdate,
    # Metadata
    EventMeta,
    Health,
    # Contract Resolution
    Contract,
)

# ============================================================================
# Errors (canonical exceptions)
# ============================================================================
from .errors import (
    # Base
    MarketDataError,
    # Retryable
    ConnectionFailed,
    FarmTransient,
    PacingViolation,
    RetryableProviderError,
    TemporaryUnavailable,
    # Non-retryable
    AuthenticationFailed,
    ConfigurationError,
    InvalidInstrument,
    NonRetryableProviderError,
    PermissionsMissing,
    # Validation
    ValidationError,
    # Pipeline
    BatcherError,
    PipelineError,
    SinkError,
    SourceError,
    TransformError,
    # Backward compatibility (deprecated)
    ConnectionException,
    IBKRPacingError,
    IBKRUnavailable,
    MarketDataException,
    ProviderException,
    RateLimitException,
    ValidationException,
)

# ============================================================================
# Settings (configuration)
# ============================================================================
from .settings import (
    CoreSettings,
    # Backward compatibility functions
    get_database_config,
    get_ibkr_config,
    get_pipeline_config,
    # NEW in v1.1.0
    CompositeSettings,
    ProviderConfig,
    SinkConfig,
    WiringPlan,
)

# ============================================================================
# Telemetry (NEW in v1.1.0)
# ============================================================================
from .telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
    HealthState,
    HealthComponent,
    HealthStatus,
    Probe,
    MetricPoint,
    MetricSeries,
    Labels,
    ControlAction,
    ControlResult,
    AuditEnvelope,
)

# ============================================================================
# Federation (NEW in v1.1.0)
# ============================================================================
from .federation import (
    ClusterId,
    NodeId,
    NodeRole,
    Region,
    NodeStatus,
    ClusterTopology,
)

# ============================================================================
# Registry (NEW in v1.1.0)
# ============================================================================
from .registry import (
    Capability,
    ProviderSpec,
    SinkSpec,
)

# ============================================================================
# Schema Registry (NEW in v1.2.0 - Phase 11.1)
# ============================================================================
from .models.registry import (
    EnforcementMode,
    SchemaPublishedEvent,
    SchemaDeprecatedEvent,
    SchemaDriftEvent,
    SchemaValidationResult,
)
from .registry import (
    RegistryClient,
    DriftDetector,
    EnforcementPolicy,
    SchemaUsageTracker,
    get_enforcement_mode,
    should_enforce_strict,
    should_log_warning,
)

# ============================================================================
# Protocol Extensions (NEW in v1.1.0)
# ============================================================================
from .protocols import (
    # ... existing protocols already imported above ...
    # NEW for v1.1.0
    ProviderRegistry,
    SinkRegistry,
    FeedbackPublisher,
    RateController,
    FederationDirectory,
)

# ============================================================================
# Error Extensions (NEW in v1.1.0)
# ============================================================================
from .errors import (
    # ... existing errors already imported above ...
    # NEW for v1.1.0
    RegistryError,
    ContractValidationError,
)

# ============================================================================
# Version
# ============================================================================
__version__ = "1.2.9"

# ============================================================================
# Backward Compatibility (deprecated - will be removed in v2.0)
# ============================================================================
try:
    # Re-export pipeline functions if available (deprecated)
    from market_data_pipeline import (
        create_explicit_pipeline,
        create_pipeline,
        ensure_windows_selector_event_loop,
    )
    
    _has_pipeline_compat = True
except ImportError:
    _has_pipeline_compat = False
    create_pipeline = None  # type: ignore
    create_explicit_pipeline = None  # type: ignore
    ensure_windows_selector_event_loop = None  # type: ignore

# ============================================================================
# Public API
# ============================================================================
__all__ = [
    # Version
    "__version__",
    # Protocols
    "MarketDataProvider",
    "Source",
    "Transform",
    "Sink",
    "PipelineRunner",
    # Protocols - NEW v1.1.0
    "ProviderRegistry",
    "SinkRegistry",
    "FeedbackPublisher",
    "RateController",
    "FederationDirectory",
    # Models - Instruments
    "Instrument",
    # Models - Market Data
    "Bar",
    "PriceBar",
    "Quote",
    "Trade",
    "MarketDepth",
    # Models - Options
    "OptionSnapshot",
    "OptionContract",
    "OptionGreeks",
    "OptionChain",
    # Models - Portfolio
    "Position",
    "AccountSummary",
    "PortfolioUpdate",
    # Models - Metadata
    "EventMeta",
    "Health",
    "Contract",
    # Telemetry - NEW v1.1.0
    "BackpressureLevel",
    "FeedbackEvent",
    "RateAdjustment",
    "HealthState",
    "HealthComponent",
    "HealthStatus",
    "Probe",
    "MetricPoint",
    "MetricSeries",
    "Labels",
    "ControlAction",
    "ControlResult",
    "AuditEnvelope",
    # Federation - NEW v1.1.0
    "ClusterId",
    "NodeId",
    "NodeRole",
    "Region",
    "NodeStatus",
    "ClusterTopology",
    # Registry - NEW v1.1.0
    "Capability",
    "ProviderSpec",
    "SinkSpec",
    # Schema Registry - NEW v1.2.0 (Phase 11.1)
    "EnforcementMode",
    "SchemaPublishedEvent",
    "SchemaDeprecatedEvent",
    "SchemaDriftEvent",
    "SchemaValidationResult",
    "RegistryClient",
    "DriftDetector",
    "EnforcementPolicy",
    "SchemaUsageTracker",
    "get_enforcement_mode",
    "should_enforce_strict",
    "should_log_warning",
    # Errors - Base
    "MarketDataError",
    # Errors - Retryable
    "RetryableProviderError",
    "PacingViolation",
    "FarmTransient",
    "ConnectionFailed",
    "TemporaryUnavailable",
    # Errors - Non-retryable
    "NonRetryableProviderError",
    "PermissionsMissing",
    "InvalidInstrument",
    "ConfigurationError",
    "AuthenticationFailed",
    # Errors - Validation
    "ValidationError",
    # Errors - Pipeline
    "PipelineError",
    "SourceError",
    "TransformError",
    "SinkError",
    "BatcherError",
    # Errors - NEW v1.1.0
    "RegistryError",
    "ContractValidationError",
    # Settings
    "CoreSettings",
    # Settings - NEW v1.1.0
    "CompositeSettings",
    "ProviderConfig",
    "SinkConfig",
    "WiringPlan",
]

# Add backward compatibility exports if available
if _has_pipeline_compat:
    __all__.extend([
        "create_pipeline",
        "create_explicit_pipeline",
        "ensure_windows_selector_event_loop",
    ])
