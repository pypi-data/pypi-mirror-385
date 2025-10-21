"""Metrics contracts for observability."""

from pydantic import BaseModel, Field


class Labels(BaseModel):
    """Metric labels (tags) for dimensional metrics.
    
    Example:
        ```python
        labels = Labels(values={"symbol": "AAPL", "exchange": "NASDAQ"})
        ```
    """
    
    values: dict[str, str] = Field(default_factory=dict, description="Label key-value pairs")


class MetricPoint(BaseModel):
    """Single metric observation.
    
    Example:
        ```python
        point = MetricPoint(
            name="market_data_quotes_received",
            value=1250.0,
            labels=Labels(values={"provider": "ibkr", "symbol": "MSFT"}),
            ts=time.time()
        )
        ```
    """
    
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    labels: Labels = Field(default_factory=Labels, description="Metric labels")
    ts: float = Field(..., description="Unix epoch seconds")


class MetricSeries(BaseModel):
    """Time series of metric points.
    
    Example:
        ```python
        series = MetricSeries(
            name="latency_ms",
            points=[
                MetricPoint(name="latency_ms", value=12.0, ts=t1),
                MetricPoint(name="latency_ms", value=15.0, ts=t2),
            ]
        )
        ```
    """
    
    name: str = Field(..., description="Series name")
    points: list[MetricPoint] = Field(default_factory=list, description="Time series data")

