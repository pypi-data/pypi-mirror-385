from pydantic import BaseModel, Field


# Exception classes for proper error handling
class MarketDataException(Exception):
    """Base exception for market data operations."""

    pass


class ValidationException(MarketDataException):
    """Validation error exception."""

    pass


class ConnectionException(MarketDataException):
    """Connection error exception."""

    pass


class ProviderException(MarketDataException):
    """Provider error exception."""

    pass


class RateLimitException(MarketDataException):
    """Rate limit error exception."""

    pass


class IBKRPacingError(MarketDataException):
    """IBKR pacing violation error."""

    pass


class IBKRUnavailable(MarketDataException):
    """IBKR service unavailable error."""

    pass


class ErrorDetail(BaseModel):
    """Standardized error response."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    provider_code: str | None = Field(None, description="Provider-specific error code")
    retry_after: int | None = Field(None, description="Retry after seconds (for rate limiting)")


class APIError(BaseModel):
    """API error response wrapper."""

    error: ErrorDetail = Field(..., description="Error details")


# Common error types
class ValidationError(APIError):
    """Validation error (422)."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            type="validation_error",
            message="Invalid request parameters",
            provider_code=None,
            retry_after=None,
        ),
        description="Validation error details",
    )


class RateLimitError(APIError):
    """Rate limit error (429)."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            type="rate_limit_error",
            message="Rate limit exceeded",
            provider_code=None,
            retry_after=60,
        ),
        description="Rate limit error details",
    )


class ProviderError(APIError):
    """Provider error (502)."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            type="provider_error",
            message="Data provider error",
            provider_code="IBKR_ERROR",
            retry_after=None,
        ),
        description="Provider error details",
    )


class ConnectionError(APIError):
    """Connection error (503)."""

    error: ErrorDetail = Field(
        default_factory=lambda: ErrorDetail(
            type="connection_error",
            message="Unable to connect to data provider",
            provider_code=None,
            retry_after=None,
        ),
        description="Connection error details",
    )
