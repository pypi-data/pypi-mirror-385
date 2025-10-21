from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PriceBar(BaseModel):
    """Normalized price bar with timezone-aware timestamps."""

    symbol: str = Field(..., description="Ticker symbol")
    ts: datetime = Field(..., description="Timestamp (UTC)")
    open: Decimal = Field(..., description="Open price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Close price")
    volume: Decimal = Field(..., description="Volume")
    delayed: bool = Field(False, description="Whether data is delayed")


class Quote(BaseModel):
    """Real-time quote with timezone-aware timestamps."""

    symbol: str = Field(..., description="Symbol")
    bid: Decimal | None = Field(None, description="Bid price")
    ask: Decimal | None = Field(None, description="Ask price")
    last: Decimal | None = Field(None, description="Last trade price")
    volume: int = Field(0, description="Volume")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now().astimezone(), description="Quote timestamp"
    )
    delayed: bool = Field(False, description="Whether data is delayed")


class MarketDepth(BaseModel):
    """Market depth (Level 2) data."""

    symbol: str = Field(..., description="Symbol")
    bids: list[tuple[Decimal, int]] = Field(
        default_factory=list, description="Bid levels (price, size)"
    )
    asks: list[tuple[Decimal, int]] = Field(
        default_factory=list, description="Ask levels (price, size)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now().astimezone(), description="Depth timestamp"
    )
    delayed: bool = Field(False, description="Whether data is delayed")
