"""Backpressure and feedback contracts."""

from enum import Enum
from pydantic import BaseModel, Field


class BackpressureLevel(str, Enum):
    """Backpressure severity levels."""
    
    ok = "ok"          # System operating normally
    soft = "soft"      # Approaching capacity, throttle recommended
    hard = "hard"      # At capacity, must throttle


class FeedbackEvent(BaseModel):
    """Backpressure feedback event from Store to Pipeline/Provider.
    
    Emitted by Store coordinators when queue levels cross thresholds.
    Consumed by Pipeline or Provider to adjust ingestion rates.
    
    Example:
        ```python
        event = FeedbackEvent(
            coordinator_id="bars_coordinator_1",
            queue_size=850,
            capacity=1000,
            level=BackpressureLevel.soft,
            source="store",
            ts=time.time()
        )
        await feedback_bus.publish(event)
        ```
    """
    
    coordinator_id: str = Field(..., description="ID of the coordinator emitting feedback")
    queue_size: int = Field(..., ge=0, description="Current queue size")
    capacity: int = Field(..., gt=0, description="Maximum queue capacity")
    level: BackpressureLevel = Field(..., description="Backpressure severity")
    source: str = Field(default="store", description="Source component (store, pipeline, etc.)")
    ts: float = Field(..., description="Unix epoch seconds")
    
    class Config:
        frozen = True


class RateAdjustment(BaseModel):
    """Rate adjustment command from Pipeline to Provider.
    
    Pipeline applies feedback events to produce rate adjustments for providers.
    
    Example:
        ```python
        adjustment = RateAdjustment(
            provider="ibkr",
            scale=0.7,  # Reduce to 70% of normal rate
            reason=BackpressureLevel.soft,
            ts=time.time()
        )
        await rate_controller.apply(adjustment)
        ```
    """
    
    provider: str = Field(..., description="Provider name (ibkr, synthetic, etc.)")
    scale: float = Field(..., ge=0.0, le=1.0, description="Rate scale factor (0.0 = pause, 1.0 = full)")
    reason: BackpressureLevel = Field(..., description="Reason for adjustment")
    ts: float = Field(..., description="Unix epoch seconds")
    
    class Config:
        frozen = True

