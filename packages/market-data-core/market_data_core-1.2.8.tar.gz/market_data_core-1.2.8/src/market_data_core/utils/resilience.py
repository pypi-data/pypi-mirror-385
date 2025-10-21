"""Resilience patterns for IBKR integration."""

import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypeVar

from loguru import logger
from prometheus_client import Gauge
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for IBKR operations.
    Prevents cascading failures by opening the circuit after N failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitState.CLOSED

        # Prometheus metrics - simplified for testing
        self.metrics: dict[str, Any] = {}

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _record_success(self) -> None:
        """Record a successful operation."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        # self.metrics["circuit_breaker_state"].labels(name="ibkr").set(0)  # 0 = closed

    def _record_failure(self) -> None:
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        # self.metrics["circuit_breaker_failures"].labels(name="ibkr").inc()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            # self.metrics["circuit_breaker_state"].labels(name="ibkr").set(1)  # 1 = open
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    async def call(self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                # self.metrics["circuit_breaker_state"].labels(name="ibkr").set(2)  # 2 = half_open
                logger.info("Circuit breaker attempting reset")
            else:
                # self.metrics["circuit_breaker_requests"].labels(
                #     name="ibkr", result="circuit_open"
                # ).inc()
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            # self.metrics["circuit_breaker_requests"].labels(name="ibkr", result="success").inc()
            return result
        except self.expected_exception:
            self._record_failure()
            # self.metrics["circuit_breaker_requests"].labels(name="ibkr", result="failure").inc()
            raise


class RetryConfig:
    """Retry configuration for different operation types."""

    # Standard retry for most operations
    STANDARD = {
        "wait": wait_exponential(multiplier=1, min=1, max=30),
        "stop": stop_after_attempt(3),
        "retry": retry_if_exception_type((ConnectionError, TimeoutError)),
    }

    # Aggressive retry for critical operations
    AGGRESSIVE = {
        "wait": wait_exponential(multiplier=1, min=1, max=60),
        "stop": stop_after_attempt(5),
        "retry": retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    }

    # Light retry for non-critical operations
    LIGHT = {
        "wait": wait_exponential(multiplier=1, min=1, max=10),
        "stop": stop_after_attempt(2),
        "retry": retry_if_exception_type((ConnectionError,)),
    }


def with_retry(config: dict[str, Any] | None = None) -> Any:
    """Decorator for adding retry logic to functions."""
    if config is None:
        config = RetryConfig.STANDARD

    return retry(**config)


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type[Exception] = Exception,
) -> Any:
    """Decorator for adding circuit breaker to functions."""
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception,
    )

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await circuit_breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


class AutoDowngrade:
    """
    Auto-downgrade from realtime to delayed data on permission errors.
    """

    def __init__(self) -> None:
        self.downgraded = False
        self.metrics = {
            "data_downgrade": Gauge("data_downgrade", "Data downgrade status"),
        }

    async def execute_with_downgrade(
        self,
        realtime_func: Callable[..., Awaitable[Any]],
        delayed_func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function with automatic downgrade on permission errors."""
        if self.downgraded:
            # Already downgraded, use delayed function
            logger.info("Using delayed data due to previous downgrade")
            return await delayed_func(*args, **kwargs)

        try:
            # Try realtime first
            result = await realtime_func(*args, **kwargs)
            return result
        except Exception as e:
            if "permission" in str(e).lower() or "subscription" in str(e).lower():
                # Permission error, downgrade to delayed
                logger.warning(f"Permission error detected, downgrading to delayed data: {e}")
                self.downgraded = True
                self.metrics["data_downgrade"].set(1)

                # Retry with delayed data
                result = await delayed_func(*args, **kwargs)
                # Mark result as delayed
                if hasattr(result, "delayed"):
                    result.delayed = True
                return result
            else:
                # Re-raise non-permission errors
                raise


# Global instances
circuit_breaker = CircuitBreaker()
auto_downgrade = AutoDowngrade()
