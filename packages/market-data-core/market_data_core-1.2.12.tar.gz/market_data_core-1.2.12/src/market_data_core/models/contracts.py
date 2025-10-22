from pydantic import BaseModel, Field


class Contract(BaseModel):
    """Minimal contract resolver model."""

    conid: int = Field(..., description="Interactive Brokers contract ID")
    symbol: str = Field(..., description="Ticker symbol")
    primary_exchange: str = Field(..., description="Primary exchange")
    currency: str = Field(..., description="Currency code")
    sec_type: str = Field(..., description="Security type (STK, OPT, etc.)")
    exchange: str = Field(..., description="Exchange")
    local_symbol: str | None = Field(None, description="Local symbol")
    trading_class: str | None = Field(None, description="Trading class")
