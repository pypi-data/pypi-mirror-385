"""Core settings - provider-agnostic configuration.

Settings are Pydantic models that can be loaded from:
- Environment variables
- Configuration files (YAML, JSON, TOML)
- Direct instantiation

Provider-specific settings go in `provider_extras` dict.
"""

import os
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class CoreSettings(BaseModel):
    """Core settings for market data system.
    
    This is the top-level configuration that orchestrates the entire system.
    Provider-specific settings (e.g., IBKR host/port) go in `provider_extras`.
    
    Example:
        ```python
        settings = CoreSettings(
            watchlist=["AAPL", "MSFT", "GOOGL"],
            provider_name="ibkr",
            provider_extras={
                "host": "127.0.0.1",
                "port": 4002,
                "client_id": 17,
            },
            database_url="postgresql://localhost/market_data"
        )
        ```
    
    Environment variables:
        MARKET_DATA_WATCHLIST: Comma-separated symbols
        MARKET_DATA_PROVIDER: Provider name (ibkr, synthetic)
        DATABASE_URL: Database connection URL
        METRICS_PORT: Prometheus metrics port
    """
    
    # ========================================================================
    # Watchlist Configuration
    # ========================================================================
    
    watchlist: list[str] = Field(
        default_factory=list,
        description="Symbols to monitor (e.g., ['AAPL', 'MSFT'])"
    )
    
    @field_validator("watchlist", mode="before")
    @classmethod
    def parse_watchlist(cls, v: Any) -> list[str]:
        """Parse watchlist from comma-separated string or list."""
        if isinstance(v, str):
            return [s.strip().upper() for s in v.split(",") if s.strip()]
        return v
    
    # ========================================================================
    # Pipeline Configuration
    # ========================================================================
    
    queue_maxsize: int = Field(
        default=1000,
        description="Max queue size for backpressure control",
        ge=1,
        le=100000,
    )
    
    worker_concurrency: int = Field(
        default=4,
        description="Number of concurrent workers for sinks",
        ge=1,
        le=100,
    )
    
    flush_timeout_sec: float = Field(
        default=5.0,
        description="Flush timeout in seconds",
        ge=0.1,
        le=300.0,
    )
    
    batch_size: int = Field(
        default=500,
        description="Batch size for database writes",
        ge=1,
        le=10000,
    )
    
    batch_flush_ms: int = Field(
        default=1000,
        description="Batch flush interval in milliseconds",
        ge=100,
        le=60000,
    )
    
    # ========================================================================
    # Provider Configuration
    # ========================================================================
    
    provider_name: Literal["ibkr", "synthetic", "replay"] = Field(
        default="ibkr",
        description="Provider to use for market data"
    )
    
    provider_extras: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific configuration (e.g., IBKRSettings dict)"
    )
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/market_data",
        description="Database connection URL (for sinks)"
    )
    
    database_pool_min: int = Field(
        default=2,
        description="Minimum database connection pool size",
        ge=1,
        le=100,
    )
    
    database_pool_max: int = Field(
        default=10,
        description="Maximum database connection pool size",
        ge=1,
        le=100,
    )
    
    database_timeout_sec: float = Field(
        default=30.0,
        description="Database query timeout in seconds",
        ge=1.0,
        le=300.0,
    )
    
    # ========================================================================
    # Observability Configuration
    # ========================================================================
    
    telemetry_enabled: bool = Field(
        default=True,
        description="Enable telemetry collection (metrics, traces)"
    )
    
    metrics_port: int = Field(
        default=8000,
        description="Prometheus metrics HTTP port",
        ge=1024,
        le=65535,
    )
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    log_json: bool = Field(
        default=False,
        description="Output logs in JSON format"
    )
    
    # ========================================================================
    # WebSocket Configuration (if running API server)
    # ========================================================================
    
    websocket_max_connections: int = Field(
        default=1000,
        description="Maximum concurrent WebSocket connections",
        ge=1,
        le=10000,
    )
    
    websocket_rate_limit: int = Field(
        default=100,
        description="WebSocket messages per second per connection",
        ge=1,
        le=1000,
    )
    
    websocket_queue_size: int = Field(
        default=1000,
        description="WebSocket message queue size per connection",
        ge=10,
        le=10000,
    )
    
    # ========================================================================
    # Pacing Configuration (provider-agnostic)
    # ========================================================================
    
    pacing_burst: int = Field(
        default=1000,
        description="Pacing burst capacity (tokens)",
        ge=1,
        le=10000,
    )
    
    pacing_refill_rate: int = Field(
        default=1000,
        description="Pacing refill rate (tokens per second)",
        ge=1,
        le=10000,
    )
    
    # ========================================================================
    # Environment Variable Loading
    # ========================================================================
    
    @classmethod
    def from_env(cls) -> "CoreSettings":
        """Load settings from environment variables.
        
        Environment variables:
            MARKET_DATA_WATCHLIST: Comma-separated symbols
            MARKET_DATA_PROVIDER: Provider name
            DATABASE_URL: Database connection URL
            METRICS_PORT: Prometheus port
            LOG_LEVEL: Logging level
            
            IBKR_HOST: IBKR host (goes into provider_extras)
            IBKR_PORT: IBKR port (goes into provider_extras)
            IBKR_CLIENT_ID: IBKR client ID (goes into provider_extras)
        
        Returns:
            CoreSettings instance
        """
        # Build provider_extras from environment
        provider_extras = {}
        
        # IBKR-specific env vars
        if os.getenv("IBKR_HOST"):
            provider_extras["host"] = os.getenv("IBKR_HOST")
        if os.getenv("IBKR_PORT"):
            provider_extras["port"] = int(os.getenv("IBKR_PORT"))
        if os.getenv("IBKR_CLIENT_ID"):
            provider_extras["client_id"] = int(os.getenv("IBKR_CLIENT_ID"))
        if os.getenv("IBKR_MARKET_DATA_TYPE"):
            provider_extras["market_data_type"] = int(os.getenv("IBKR_MARKET_DATA_TYPE"))
        
        return cls(
            watchlist=os.getenv("MARKET_DATA_WATCHLIST", "").split(",") if os.getenv("MARKET_DATA_WATCHLIST") else [],
            provider_name=os.getenv("MARKET_DATA_PROVIDER", "ibkr"),  # type: ignore
            provider_extras=provider_extras,
            database_url=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/market_data"),
            metrics_port=int(os.getenv("METRICS_PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),  # type: ignore
            telemetry_enabled=os.getenv("TELEMETRY_ENABLED", "true").lower() == "true",
        )
    
    class Config:
        extra = "allow"  # Allow extra fields for extensibility
        use_enum_values = True


# ============================================================================
# Backward Compatibility
# ============================================================================

# Map old Config class methods to new CoreSettings
def get_pipeline_config() -> dict[str, Any]:
    """Get pipeline configuration (backward compatibility).
    
    Deprecated: Use CoreSettings directly instead.
    """
    import warnings
    warnings.warn(
        "get_pipeline_config() is deprecated. Use CoreSettings instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    settings = CoreSettings.from_env()
    return {
        'batch_size': settings.batch_size,
        'flush_ms': settings.batch_flush_ms,
        'pacing_budget': (settings.pacing_burst, settings.pacing_refill_rate),
    }


def get_database_config() -> dict[str, Any]:
    """Get database configuration (backward compatibility).
    
    Deprecated: Use CoreSettings directly instead.
    """
    import warnings
    warnings.warn(
        "get_database_config() is deprecated. Use CoreSettings instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    settings = CoreSettings.from_env()
    return {
        'dsn': settings.database_url,
        'pool_max': settings.database_pool_max,
    }


def get_ibkr_config() -> dict[str, Any]:
    """Get IBKR configuration (backward compatibility).
    
    Deprecated: Use CoreSettings.provider_extras instead.
    """
    import warnings
    warnings.warn(
        "get_ibkr_config() is deprecated. Use CoreSettings.provider_extras instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    settings = CoreSettings.from_env()
    return settings.provider_extras


# ============================================================================
# Composition Settings (NEW for v1.1.0)
# ============================================================================

class CompositeSettings(BaseModel):
    """High-level composition of settings across system components.
    
    Enables nested validation and composition for multi-component systems.
    Each component validates its own section.
    
    Example:
        ```python
        settings = CompositeSettings(
            pipeline={"batch_size": 500, "flush_ms": 1000},
            store={"pool_max": 10, "timeout_sec": 30},
            orchestrator={"mode": "dag", "workers": 4},
            auth={"issuer": "https://auth.example.com", "audience": "market-data"},
            federation={"cluster_id": "prod-us-east"}
        )
        ```
    """
    
    pipeline: dict = Field(default_factory=dict, description="Pipeline-specific settings")
    store: dict = Field(default_factory=dict, description="Store-specific settings")
    orchestrator: dict = Field(default_factory=dict, description="Orchestrator-specific settings")
    auth: dict = Field(default_factory=dict, description="Authentication/authorization settings")
    federation: dict = Field(default_factory=dict, description="Federation settings")


class ProviderConfig(BaseModel):
    """Provider configuration for wiring.
    
    Example:
        ```python
        config = ProviderConfig(
            name="ibkr",
            params={"host": "127.0.0.1", "port": 4002}
        )
        ```
    """
    
    name: str = Field(..., description="Provider name")
    params: dict = Field(default_factory=dict, description="Provider parameters")


class SinkConfig(BaseModel):
    """Sink configuration for wiring.
    
    Example:
        ```python
        config = SinkConfig(
            name="bars_sink",
            params={"db_url": "postgresql://...", "batch_size": 500}
        )
        ```
    """
    
    name: str = Field(..., description="Sink name")
    params: dict = Field(default_factory=dict, description="Sink parameters")


class WiringPlan(BaseModel):
    """Declarative wiring plan for pipeline construction.
    
    Specifies which providers and sinks to wire up, with their configuration.
    
    Example:
        ```python
        plan = WiringPlan(
            providers=[
                ProviderConfig(name="ibkr", params={...}),
            ],
            sinks=[
                SinkConfig(name="bars_sink", params={...}),
                SinkConfig(name="quotes_sink", params={...}),
            ]
        )
        ```
    """
    
    providers: list[ProviderConfig] = Field(default_factory=list, description="Providers to wire")
    sinks: list[SinkConfig] = Field(default_factory=list, description="Sinks to wire")


__all__ = [
    "CoreSettings",
    # Backward compatibility
    "get_pipeline_config",
    "get_database_config",
    "get_ibkr_config",
    # NEW for v1.1.0
    "CompositeSettings",
    "ProviderConfig",
    "SinkConfig",
    "WiringPlan",
]

