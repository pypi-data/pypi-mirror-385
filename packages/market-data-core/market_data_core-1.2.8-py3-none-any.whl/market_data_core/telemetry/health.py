"""Health check contracts."""

from typing import Literal, Dict
from pydantic import BaseModel, Field


HealthState = Literal["healthy", "degraded", "unhealthy"]


class HealthComponent(BaseModel):
    """Health status of a single component.
    
    Example:
        ```python
        component = HealthComponent(
            name="ibkr_connection",
            state="healthy",
            details={"connected": "true", "latency_ms": "12"}
        )
        ```
    """
    
    name: str = Field(..., description="Component name")
    state: HealthState = Field(..., description="Health state")
    details: Dict[str, str] = Field(default_factory=dict, description="Component-specific details")


class HealthStatus(BaseModel):
    """Overall health status for a service.
    
    Example:
        ```python
        status = HealthStatus(
            service="market-data-core",
            state="healthy",
            components=[
                HealthComponent(name="ibkr", state="healthy"),
                HealthComponent(name="database", state="healthy"),
            ],
            version="1.1.0",
            ts=time.time()
        )
        ```
    """
    
    service: str = Field(..., description="Service name")
    state: HealthState = Field(..., description="Aggregate health state")
    components: list[HealthComponent] = Field(default_factory=list, description="Component health list")
    version: str = Field(..., description="Service version")
    ts: float = Field(..., description="Unix epoch seconds")


class Probe(BaseModel):
    """Health probe result (liveness/readiness).
    
    Example:
        ```python
        probe = Probe(
            probe_type="readiness",
            passed=True,
            message="All subsystems ready"
        )
        ```
    """
    
    probe_type: Literal["liveness", "readiness"] = Field(..., description="Probe type")
    passed: bool = Field(..., description="Whether probe passed")
    message: str | None = Field(default=None, description="Optional status message")

