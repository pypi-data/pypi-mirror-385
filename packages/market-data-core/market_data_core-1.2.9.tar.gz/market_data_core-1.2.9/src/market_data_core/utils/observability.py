"""Observability utilities for metrics and logging."""

import os
import time
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from loguru import logger
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


class MetricsCollector:
    """Centralized metrics collection for the application."""

    def __init__(self) -> None:
        # Request metrics
        self.requests_total = Counter(
            "reqs_total", "Total requests", ["method", "endpoint", "status_code"]
        )

        self.request_duration = Histogram(
            "request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
        )

        # Provider metrics
        self.provider_errors = Counter(
            "provider_errors_total", "Provider errors", ["provider", "code", "type"]
        )

        # WebSocket metrics
        self.ws_clients = Gauge("ws_clients", "Active WebSocket clients", ["stream_type"])

        self.ws_dropped_messages = Counter(
            "ws_dropped_messages_total", "Dropped WebSocket messages", ["stream_type"]
        )

        self.ws_messages_sent = Counter(
            "ws_messages_sent_total", "WebSocket messages sent", ["stream_type"]
        )

        # IBKR specific metrics
        self.ib_connected = Gauge("ib_connected", "IBKR connection status")
        self.ib_reconnects = Counter("ib_reconnects_total", "Total IBKR reconnections")
        self.ib_subscriptions = Gauge(
            "ib_subscriptions_active", "Active IBKR subscriptions", ["type"]
        )
        self.ib_errors = Counter("ib_errors_total", "Total IBKR errors", ["error_type"])
        self.ib_pacing_violations = Counter("ib_pacing_violations_total", "IBKR pacing violations")
        self.ib_backoff_events = Counter("ib_backoff_events_total", "IBKR backoff events")

        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            "circuit_breaker_state", "Circuit breaker state", ["name"]
        )

        self.circuit_breaker_failures = Counter(
            "circuit_breaker_failures_total", "Circuit breaker failures", ["name"]
        )


# Global metrics instance
metrics = MetricsCollector()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request IDs for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add to request headers for logging (commented out for testing)
        # request.headers["X-Request-ID"] = request_id

        # Process request
        start_time = time.time()
        response: StarletteResponse = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        endpoint = request.url.path
        method = request.method
        status_code = str(response.status_code)

        metrics.requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        metrics.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        # Add request ID to response headers (commented out for testing)
        # response.headers["X-Request-ID"] = request_id

        return response


class StructuredLogger:
    """Structured logging with request context."""

    def __init__(self) -> None:
        # Configure loguru for structured logging
        logger.remove()  # Remove default handler

        # Add structured JSON logging
        logger.add(
            "logs/market_data_core.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{name}:{function}:{line} | {extra}",
            level=os.getenv("LOG_LEVEL", "INFO"),
            rotation="1 day",
            retention="30 days",
            serialize=True,
        )

        # Add console logging for development
        logger.add(
            lambda msg: print(msg, end=""),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def log_request(self, request: Request, **extra: Any) -> None:
        """Log HTTP request with context."""
        logger.bind(
            request_id=getattr(request.state, "request_id", None),
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            **extra,
        ).info("HTTP request")

    def log_response(self, request: Request, response: Response, **extra: Any) -> None:
        """Log HTTP response with context."""
        logger.bind(
            request_id=getattr(request.state, "request_id", None),
            status_code=response.status_code,
            **extra,
        ).info("HTTP response")

    def log_error(self, request: Request, error: Exception, **extra: Any) -> None:
        """Log error with context."""
        logger.bind(
            request_id=getattr(request.state, "request_id", None),
            error_type=type(error).__name__,
            error_message=str(error),
            **extra,
        ).error("Request error")

    def log_ibkr_operation(self, operation: str, symbol: str | None = None, **extra: Any) -> None:
        """Log IBKR operation with context."""
        logger.bind(operation=operation, symbol=symbol, **extra).info("IBKR operation")

    def log_websocket_event(self, event: str, stream_type: str, **extra: Any) -> None:
        """Log WebSocket event with context."""
        logger.bind(event=event, stream_type=stream_type, **extra).info("WebSocket event")


# Global logger instance
structured_logger = StructuredLogger()


@asynccontextmanager
async def log_operation(operation: str, **context: Any) -> AsyncIterator[str]:
    """Context manager for logging operations with timing."""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    logger.bind(request_id=request_id, operation=operation, **context).info(f"Starting {operation}")

    try:
        yield request_id
    except Exception as e:
        duration = time.time() - start_time
        logger.bind(
            request_id=request_id, operation=operation, duration=duration, error=str(e), **context
        ).error(f"Failed {operation}")
        raise
    else:
        duration = time.time() - start_time
        logger.bind(request_id=request_id, operation=operation, duration=duration, **context).info(
            f"Completed {operation}"
        )


def get_metrics_response() -> StarletteResponse:
    """Get Prometheus metrics response."""
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def setup_observability(app: FastAPI) -> None:
    """Setup observability middleware and logging."""
    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)

    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint() -> Response:
        """Prometheus metrics endpoint."""
        return get_metrics_response()

    # Add health endpoint with metrics
    @app.get("/health/detailed")
    async def detailed_health() -> dict[str, Any]:
        """Detailed health endpoint with metrics."""
        return {
            "status": "ok",
            "version": "0.1.0",
            "metrics": {
                "requests_total": 0,  # Simplified for now
                "provider_errors_total": 0,
                "ws_clients_total": 0,
            },
        }
