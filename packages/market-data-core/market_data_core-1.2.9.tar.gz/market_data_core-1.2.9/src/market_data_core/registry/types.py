"""Registry type definitions - contracts only."""

from pydantic import BaseModel, Field


class Capability(BaseModel):
    """Capability descriptor for providers/sinks.
    
    Example:
        ```python
        cap = Capability(
            name="historical_bars",
            params={"max_duration_days": "365", "resolutions": "1m,1h,1d"}
        )
        ```
    """
    
    name: str = Field(..., description="Capability name")
    params: dict[str, str] = Field(default_factory=dict, description="Capability parameters")


class ProviderSpec(BaseModel):
    """Provider specification for registry.
    
    Describes a provider without instantiating it.
    Actual instantiation happens in application layer.
    
    Example:
        ```python
        spec = ProviderSpec(
            name="ibkr",
            module="market_data_ibkr",
            entry="IBKRProvider",
            capabilities=[
                Capability(name="realtime_quotes"),
                Capability(name="historical_bars"),
            ]
        )
        ```
    """
    
    name: str = Field(..., description="Provider name (ibkr, synthetic, etc.)")
    module: str = Field(..., description="Python module path")
    entry: str = Field(..., description="Class or entry point name")
    capabilities: list[Capability] = Field(default_factory=list, description="Provider capabilities")


class SinkSpec(BaseModel):
    """Sink specification for registry.
    
    Describes a sink without instantiating it.
    
    Example:
        ```python
        spec = SinkSpec(
            name="timescale_bars",
            module="market_data_store.sinks",
            entry="BarsSink",
            kind="bars"
        )
        ```
    """
    
    name: str = Field(..., description="Sink name")
    module: str = Field(..., description="Python module path")
    entry: str = Field(..., description="Class or entry point name")
    kind: str = Field(..., description="Data kind (bars, quotes, options, etc.)")

