"""Canonical exception hierarchy - provider-agnostic errors.

This module defines the canonical error types that all providers should map to.
Provider-specific error codes (e.g., IBKR error 162, 420) should be mapped to
these canonical types.

Error Hierarchy:
    MarketDataError (base)
    ├── RetryableProviderError (transient, should retry)
    │   ├── PacingViolation
    │   ├── FarmTransient
    │   ├── ConnectionFailed
    │   └── TemporaryUnavailable
    └── NonRetryableProviderError (fatal, don't retry)
        ├── PermissionsMissing
        ├── InvalidInstrument
        ├── ConfigurationError
        └── AuthenticationFailed
"""


# ============================================================================
# Base Errors
# ============================================================================

class MarketDataError(Exception):
    """Base exception for all market data errors.
    
    All custom exceptions in the market data system should inherit from this.
    """
    
    def __init__(self, message: str, code: str | None = None, details: dict | None = None):
        """Initialize error.
        
        Args:
            message: Human-readable error message
            code: Optional error code (e.g., "IBKR_162", "PACING_VIOLATION")
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __repr__(self) -> str:
        if self.code:
            return f"{self.__class__.__name__}(code={self.code}, message={self.message!r})"
        return f"{self.__class__.__name__}({self.message!r})"


# ============================================================================
# Retryable Errors (transient failures)
# ============================================================================

class RetryableProviderError(MarketDataError):
    """Transient error that should be retried.
    
    These errors are temporary and may succeed if retried after a backoff period.
    Examples: network issues, temporary service unavailability, rate limits.
    """
    pass


class PacingViolation(RetryableProviderError):
    """Rate limit or pacing violation from provider.
    
    Provider has throttled requests due to excessive rate.
    Should retry after cooldown period (often 10+ minutes for historical data).
    
    Examples:
    - IBKR error 162 with "exceeds max duration/pace"
    - IBKR error 420 (pacing violation)
    - HTTP 429 Too Many Requests
    """
    
    def __init__(
        self,
        message: str,
        retry_after_sec: int | None = None,
        scope: str | None = None,
        code: str | None = None,
    ):
        """Initialize pacing violation.
        
        Args:
            message: Error message
            retry_after_sec: Recommended retry delay in seconds
            scope: Scope of the violation (e.g., "historical", "realtime", "options")
            code: Optional error code
        """
        super().__init__(message, code=code)
        self.retry_after_sec = retry_after_sec
        self.scope = scope


class FarmTransient(RetryableProviderError):
    """Transient farm/server issue.
    
    Data farm or server is temporarily unavailable but expected to recover.
    
    Examples:
    - IBKR error 2104 followed by disconnection
    - "Market data farm connection is broken"
    """
    pass


class ConnectionFailed(RetryableProviderError):
    """Failed to connect to provider.
    
    Network connectivity issue or provider is unreachable.
    Should retry with exponential backoff.
    
    Examples:
    - TCP connection timeout
    - DNS resolution failure
    - Provider service down
    """
    pass


class TemporaryUnavailable(RetryableProviderError):
    """Service temporarily unavailable.
    
    Provider or specific data feed is temporarily down.
    
    Examples:
    - Maintenance window
    - Service degradation
    - Partial outage
    """
    pass


# ============================================================================
# Non-Retryable Errors (fatal, don't retry)
# ============================================================================

class NonRetryableProviderError(MarketDataError):
    """Fatal error that should not be retried.
    
    These errors require user intervention or configuration changes.
    Examples: missing permissions, invalid configuration, authentication failure.
    """
    pass


class PermissionsMissing(NonRetryableProviderError):
    """User lacks required data permissions.
    
    User's account does not have subscription or permissions for requested data.
    Requires user to upgrade subscription or enable permissions.
    
    Examples:
    - IBKR error 162 with "No market data permissions"
    - "Insufficient market data subscriptions"
    - "Options data not enabled"
    """
    pass


class InvalidInstrument(NonRetryableProviderError):
    """Invalid or unknown instrument.
    
    The requested instrument is not recognized by the provider.
    
    Examples:
    - Unknown ticker symbol
    - Invalid contract specification
    - Delisted security
    """
    pass


class ConfigurationError(NonRetryableProviderError):
    """Invalid configuration.
    
    System or provider configuration is invalid.
    Requires configuration fix before proceeding.
    
    Examples:
    - Missing required settings
    - Invalid connection parameters
    - Incompatible settings
    """
    pass


class AuthenticationFailed(NonRetryableProviderError):
    """Authentication or authorization failed.
    
    Credentials are invalid or account is not authorized.
    
    Examples:
    - Invalid API key
    - Expired token
    - Account suspended
    """
    pass


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(MarketDataError):
    """Data validation failed.
    
    Received data does not match expected schema or constraints.
    
    Examples:
    - Missing required field
    - Invalid data type
    - Out of range value
    """
    
    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: object = None,
        code: str | None = None,
    ):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            code: Optional error code
        """
        super().__init__(message, code=code)
        self.field = field
        self.value = value


# ============================================================================
# Pipeline Errors (re-export or define if not in pipeline)
# ============================================================================

class PipelineError(MarketDataError):
    """Generic pipeline error."""
    pass


class SourceError(PipelineError):
    """Error in pipeline source."""
    pass


class TransformError(PipelineError):
    """Error in pipeline transform."""
    pass


class SinkError(PipelineError):
    """Error in pipeline sink."""
    pass


class BatcherError(PipelineError):
    """Error in pipeline batcher."""
    pass


# ============================================================================
# Backward Compatibility (map to new errors)
# ============================================================================

# Re-export old error names for backward compatibility
from .models.errors import (
    MarketDataException,
    ValidationException,
    ConnectionException,
    ProviderException,
    RateLimitException,
    IBKRPacingError,
    IBKRUnavailable,
)

# ============================================================================
# Registry & Contract Errors (NEW for v1.1.0)
# ============================================================================

class RegistryError(MarketDataError):
    """Error with provider/sink registry.
    
    Raised when:
    - Provider or sink not found
    - Duplicate registration
    - Invalid registry state
    """
    pass


class ContractValidationError(MarketDataError):
    """Contract validation failed.
    
    Raised when:
    - Settings validation fails
    - WiringPlan is invalid
    - DTO schema mismatch
    """
    pass


# Deprecated - use new canonical errors instead
__all__ = [
    # Base
    "MarketDataError",
    # Retryable
    "RetryableProviderError",
    "PacingViolation",
    "FarmTransient",
    "ConnectionFailed",
    "TemporaryUnavailable",
    # Non-retryable
    "NonRetryableProviderError",
    "PermissionsMissing",
    "InvalidInstrument",
    "ConfigurationError",
    "AuthenticationFailed",
    # Validation
    "ValidationError",
    # Pipeline
    "PipelineError",
    "SourceError",
    "TransformError",
    "SinkError",
    "BatcherError",
    # Backward compatibility (deprecated)
    "MarketDataException",
    "ValidationException",
    "ConnectionException",
    "ProviderException",
    "RateLimitException",
    "IBKRPacingError",
    "IBKRUnavailable",
    # NEW for v1.1.0
    "RegistryError",
    "ContractValidationError",
]

