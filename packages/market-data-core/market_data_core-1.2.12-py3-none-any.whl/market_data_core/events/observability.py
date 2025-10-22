"""Observability helpers for event bus.

Provides structured logging and metrics hooks for monitoring event bus operations.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class BusMetrics:
    """Event bus metrics for monitoring and alerting.
    
    Tracks publish/consume rates, errors, and consumer lag.
    """
    
    # Publish metrics
    messages_published: int = 0
    publish_errors: int = 0
    publish_latency_sum: float = 0.0
    
    # Subscribe metrics
    messages_consumed: int = 0
    consume_errors: int = 0
    acks: int = 0
    nacks: int = 0
    
    # Stream-level metrics
    stream_metrics: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    
    def record_publish(self, stream: str, latency: float, success: bool = True) -> None:
        """Record a publish operation.
        
        Args:
            stream: Stream name
            latency: Publish latency in seconds
            success: Whether publish succeeded
        """
        self.messages_published += 1
        self.publish_latency_sum += latency
        
        self.stream_metrics[stream]["published"] += 1
        
        if not success:
            self.publish_errors += 1
            self.stream_metrics[stream]["publish_errors"] += 1
    
    def record_consume(self, stream: str, success: bool = True) -> None:
        """Record a consume operation.
        
        Args:
            stream: Stream name
            success: Whether consume succeeded
        """
        self.messages_consumed += 1
        self.stream_metrics[stream]["consumed"] += 1
        
        if not success:
            self.consume_errors += 1
            self.stream_metrics[stream]["consume_errors"] += 1
    
    def record_ack(self, stream: str) -> None:
        """Record a message acknowledgement."""
        self.acks += 1
        self.stream_metrics[stream]["acks"] += 1
    
    def record_nack(self, stream: str) -> None:
        """Record a message failure/NACK."""
        self.nacks += 1
        self.stream_metrics[stream]["nacks"] += 1
    
    @property
    def avg_publish_latency(self) -> float:
        """Average publish latency in milliseconds."""
        if self.messages_published == 0:
            return 0.0
        return (self.publish_latency_sum / self.messages_published) * 1000
    
    @property
    def error_rate(self) -> float:
        """Overall error rate (0.0 to 1.0)."""
        total = self.messages_published + self.messages_consumed
        if total == 0:
            return 0.0
        errors = self.publish_errors + self.consume_errors
        return errors / total
    
    def get_stream_stats(self, stream: str) -> dict[str, int]:
        """Get metrics for a specific stream."""
        return dict(self.stream_metrics.get(stream, {}))
    
    def summary(self) -> dict:
        """Get a summary of all metrics."""
        return {
            "published": self.messages_published,
            "consumed": self.messages_consumed,
            "acks": self.acks,
            "nacks": self.nacks,
            "publish_errors": self.publish_errors,
            "consume_errors": self.consume_errors,
            "avg_publish_latency_ms": round(self.avg_publish_latency, 2),
            "error_rate": round(self.error_rate, 4),
            "streams": len(self.stream_metrics),
        }


class MetricsCollector(Protocol):
    """Protocol for metrics collection backends.
    
    Implementations can export to Prometheus, StatsD, CloudWatch, etc.
    """
    
    def increment(self, metric: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        """Increment a counter metric."""
        ...
    
    def gauge(self, metric: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Set a gauge metric."""
        ...
    
    def histogram(self, metric: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a histogram value."""
        ...


class NoOpMetricsCollector:
    """No-op metrics collector (default, no dependencies)."""
    
    def increment(self, metric: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        pass
    
    def gauge(self, metric: str, value: float, tags: dict[str, str] | None = None) -> None:
        pass
    
    def histogram(self, metric: str, value: float, tags: dict[str, str] | None = None) -> None:
        pass


def get_logger(name: str) -> logging.Logger:
    """Get a structured logger for event bus operations.
    
    Args:
        name: Logger name (e.g., "pulse.inmem", "pulse.redis")
    
    Returns:
        Logger instance configured for structured logging
    """
    logger = logging.getLogger(f"market_data_core.events.{name}")
    
    # If no handlers, add a basic one
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


class EventBusObserver:
    """Observer for event bus operations.
    
    Combines metrics collection and structured logging.
    """
    
    def __init__(
        self,
        name: str,
        metrics_collector: MetricsCollector | None = None,
        enable_logging: bool = True,
    ):
        """Initialize observer.
        
        Args:
            name: Observer name (e.g., "inmem", "redis")
            metrics_collector: Optional metrics collector
            enable_logging: Whether to enable structured logging
        """
        self.name = name
        self.metrics = BusMetrics()
        self.collector = metrics_collector or NoOpMetricsCollector()
        self.logger = get_logger(name) if enable_logging else None
    
    def on_publish_start(self, stream: str, schema_id: str) -> float:
        """Called when publish starts.
        
        Returns:
            Start timestamp for latency tracking
        """
        if self.logger:
            self.logger.debug(f"Publishing to {stream}: {schema_id}")
        return time.time()
    
    def on_publish_success(self, stream: str, envelope_id: str, start_time: float) -> None:
        """Called when publish succeeds."""
        latency = time.time() - start_time
        self.metrics.record_publish(stream, latency, success=True)
        
        self.collector.increment("pulse_messages_published_total", tags={"stream": stream})
        self.collector.histogram("pulse_publish_latency_seconds", latency, tags={"stream": stream})
        
        if self.logger:
            self.logger.info(f"Published to {stream}: {envelope_id} ({latency*1000:.1f}ms)")
    
    def on_publish_error(self, stream: str, error: Exception, start_time: float) -> None:
        """Called when publish fails."""
        latency = time.time() - start_time
        self.metrics.record_publish(stream, latency, success=False)
        
        self.collector.increment("pulse_publish_errors_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.error(f"Publish failed for {stream}: {error}")
    
    def on_consume_success(self, stream: str, envelope_id: str) -> None:
        """Called when message is consumed."""
        self.metrics.record_consume(stream, success=True)
        
        self.collector.increment("pulse_messages_consumed_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.debug(f"Consumed from {stream}: {envelope_id}")
    
    def on_consume_error(self, stream: str, error: Exception) -> None:
        """Called when consume fails."""
        self.metrics.record_consume(stream, success=False)
        
        self.collector.increment("pulse_consume_errors_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.error(f"Consume failed for {stream}: {error}")
    
    def on_ack(self, stream: str, envelope_id: str) -> None:
        """Called when message is acknowledged."""
        self.metrics.record_ack(stream)
        
        self.collector.increment("pulse_acks_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.debug(f"ACK {stream}: {envelope_id}")
    
    def on_nack(self, stream: str, envelope_id: str, reason: str) -> None:
        """Called when message is NACKed."""
        self.metrics.record_nack(stream)
        
        self.collector.increment("pulse_nacks_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.warning(f"NACK {stream}: {envelope_id} - {reason}")
    
    def on_dlq(self, stream: str, envelope_id: str, reason: str) -> None:
        """Called when message is moved to DLQ."""
        self.collector.increment("pulse_dlq_messages_total", tags={"stream": stream})
        
        if self.logger:
            self.logger.error(f"DLQ {stream}: {envelope_id} - {reason}")
    
    def get_metrics_summary(self) -> dict:
        """Get current metrics summary."""
        return self.metrics.summary()

