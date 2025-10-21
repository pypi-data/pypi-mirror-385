"""Consolidated data models - provider-agnostic DTOs.

All timestamps should be timezone-aware (UTC).
All prices should use Decimal for precision.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================================
# Instruments
# ============================================================================

class Instrument(BaseModel):
    """Unified instrument representation.
    
    Providers should map their internal instrument identifiers to this format.
    """
    
    symbol: str = Field(..., description="Primary symbol identifier")
    exchange: str = Field(default="SMART", description="Exchange code")
    currency: str = Field(default="USD", description="Currency code")
    sec_type: str = Field(default="STK", description="Security type: STK, OPT, FUT, CASH, etc.")
    
    # Optional provider-specific fields
    conid: int | None = Field(default=None, description="IBKR contract ID (if applicable)")
    primary_exchange: str | None = Field(default=None, description="Primary listing exchange")
    local_symbol: str | None = Field(default=None, description="Local/native symbol")
    trading_class: str | None = Field(default=None, description="Trading class")
    multiplier: str | None = Field(default=None, description="Contract multiplier")
    
    class Config:
        frozen = True  # Immutable


# ============================================================================
# Market Data
# ============================================================================

class Bar(BaseModel):
    """OHLCV bar (renamed from PriceBar for clarity).
    
    Used for both real-time and historical bar data.
    """
    
    symbol: str = Field(..., description="Symbol")
    ts: datetime = Field(..., description="Bar timestamp (UTC, bar end time)")
    open: Decimal = Field(..., description="Open price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Close price")
    volume: Decimal = Field(..., description="Volume")
    resolution: str = Field(default="1d", description="Bar resolution (e.g., '1s', '1m', '1h', '1d')")
    delayed: bool = Field(default=False, description="Whether data is delayed")
    
    class Config:
        frozen = True


# Backward compatibility alias
PriceBar = Bar


class Quote(BaseModel):
    """Real-time quote snapshot (Level 1).
    
    Contains best bid/ask prices and last trade.
    """
    
    symbol: str = Field(..., description="Symbol")
    bid: Decimal | None = Field(default=None, description="Bid price")
    ask: Decimal | None = Field(default=None, description="Ask price")
    last: Decimal | None = Field(default=None, description="Last trade price")
    bid_size: int | None = Field(default=None, description="Bid size")
    ask_size: int | None = Field(default=None, description="Ask size")
    volume: int = Field(default=0, description="Cumulative volume")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Quote timestamp (UTC)"
    )
    delayed: bool = Field(default=False, description="Whether data is delayed")
    
    class Config:
        frozen = True


class Trade(BaseModel):
    """Tick-by-tick trade (Time & Sales).
    
    Individual trade execution, not aggregated.
    """
    
    symbol: str = Field(..., description="Symbol")
    ts: datetime = Field(..., description="Trade timestamp (UTC)")
    price: Decimal = Field(..., description="Trade price")
    size: int = Field(..., description="Trade size")
    exchange: str | None = Field(default=None, description="Execution exchange")
    conditions: list[str] = Field(
        default_factory=list,
        description="Trade conditions/flags"
    )
    
    class Config:
        frozen = True


class MarketDepth(BaseModel):
    """Market depth (Level 2) data.
    
    Full order book with multiple price levels.
    """
    
    symbol: str = Field(..., description="Symbol")
    bids: list[tuple[Decimal, int]] = Field(
        default_factory=list,
        description="Bid levels (price, size)"
    )
    asks: list[tuple[Decimal, int]] = Field(
        default_factory=list,
        description="Ask levels (price, size)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Depth snapshot timestamp (UTC)"
    )
    delayed: bool = Field(default=False, description="Whether data is delayed")
    
    class Config:
        frozen = True


# ============================================================================
# Options
# ============================================================================

class OptionSnapshot(BaseModel):
    """Option contract snapshot (renamed from OptionContract).
    
    Contains pricing, volume, and optionally greeks.
    """
    
    symbol: str = Field(..., description="Underlying symbol")
    expiry: datetime = Field(..., description="Expiration date")
    strike: Decimal = Field(..., description="Strike price")
    option_type: Literal["C", "P"] = Field(..., description="Call or Put")
    
    # Pricing
    bid: Decimal | None = Field(default=None, description="Bid price")
    ask: Decimal | None = Field(default=None, description="Ask price")
    last: Decimal | None = Field(default=None, description="Last trade price")
    
    # Volume & interest
    volume: int = Field(default=0, description="Trading volume")
    open_interest: int = Field(default=0, description="Open interest")
    
    # Greeks (optional - may not always be available)
    implied_volatility: Decimal | None = Field(default=None, description="Implied volatility")
    delta: Decimal | None = Field(default=None, description="Delta")
    gamma: Decimal | None = Field(default=None, description="Gamma")
    theta: Decimal | None = Field(default=None, description="Theta")
    vega: Decimal | None = Field(default=None, description="Vega")
    
    delayed: bool = Field(default=False, description="Whether data is delayed")
    
    class Config:
        frozen = True


# Backward compatibility alias
OptionContract = OptionSnapshot


class OptionGreeks(BaseModel):
    """Option Greeks (separate from snapshot for clarity).
    
    Used when Greeks are calculated/updated independently from price.
    """
    
    symbol: str = Field(..., description="Underlying symbol")
    expiry: datetime = Field(..., description="Expiration date")
    strike: Decimal = Field(..., description="Strike price")
    option_type: Literal["C", "P"] = Field(..., description="Call or Put")
    
    implied_volatility: Decimal | None = Field(default=None, description="Implied volatility")
    delta: Decimal | None = Field(default=None, description="Delta")
    gamma: Decimal | None = Field(default=None, description="Gamma")
    theta: Decimal | None = Field(default=None, description="Theta (per day)")
    vega: Decimal | None = Field(default=None, description="Vega (per 1% vol)")
    rho: Decimal | None = Field(default=None, description="Rho (per 1% rate)")
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Greeks calculation timestamp (UTC)"
    )
    
    class Config:
        frozen = True


class OptionChain(BaseModel):
    """Options chain for an underlying.
    
    Collection of option contracts for a single underlying.
    """
    
    underlying_symbol: str = Field(..., description="Underlying symbol")
    underlying_price: Decimal = Field(..., description="Current underlying price")
    contracts: list[OptionSnapshot] = Field(
        default_factory=list,
        description="List of option contracts"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Chain snapshot timestamp (UTC)"
    )
    delayed: bool = Field(default=False, description="Whether data is delayed")


# ============================================================================
# Portfolio & Account
# ============================================================================

class Position(BaseModel):
    """Account position in a single instrument."""
    
    symbol: str = Field(..., description="Symbol")
    position: Decimal = Field(..., description="Position quantity (+ long, - short)")
    avg_cost: Decimal = Field(..., description="Average cost basis")
    market_price: Decimal = Field(..., description="Current market price")
    market_value: Decimal = Field(..., description="Current market value")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    realized_pnl: Decimal = Field(..., description="Realized P&L")


class AccountSummary(BaseModel):
    """Account summary snapshot."""
    
    account_id: str = Field(..., description="Account identifier")
    net_liquidation: Decimal = Field(..., description="Net liquidation value")
    total_cash: Decimal = Field(..., description="Total cash balance")
    buying_power: Decimal = Field(..., description="Available buying power")
    positions: list[Position] = Field(
        default_factory=list,
        description="Current positions"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Summary timestamp (UTC)"
    )


class PortfolioUpdate(BaseModel):
    """Portfolio update event (real-time)."""
    
    account_id: str = Field(..., description="Account identifier")
    net_liquidation: Decimal = Field(..., description="Net liquidation value")
    unrealized_pnl: Decimal = Field(..., description="Total unrealized P&L")
    realized_pnl: Decimal = Field(..., description="Total realized P&L")
    positions: list[Position] = Field(
        default_factory=list,
        description="Updated positions"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Update timestamp (UTC)"
    )


# ============================================================================
# Metadata & Health
# ============================================================================

class EventMeta(BaseModel):
    """Metadata for all events.
    
    Used for observability, sequencing, and latency tracking.
    """
    
    seq: int | None = Field(default=None, description="Sequence number")
    provider: str = Field(..., description="Provider name (e.g., 'ibkr', 'synthetic')")
    source_ts: datetime | None = Field(
        default=None,
        description="Timestamp from provider (if available)"
    )
    received_ts: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when received by system"
    )
    latency_ms: float | None = Field(
        default=None,
        description="Latency in milliseconds (source_ts to received_ts)"
    )
    
    class Config:
        frozen = True


class Health(BaseModel):
    """Health status for components."""
    
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Health status"
    )
    component: str | None = Field(default=None, description="Component name")
    message: str | None = Field(default=None, description="Status message")
    details: dict | None = Field(default=None, description="Additional details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp (UTC)"
    )


# ============================================================================
# Contract Resolution (IBKR-specific, but commonly needed)
# ============================================================================

class Contract(BaseModel):
    """Contract resolution result (primarily for IBKR).
    
    Maps symbols to provider-specific contract identifiers.
    """
    
    conid: int = Field(..., description="Interactive Brokers contract ID")
    symbol: str = Field(..., description="Ticker symbol")
    primary_exchange: str = Field(..., description="Primary exchange")
    currency: str = Field(..., description="Currency code")
    sec_type: str = Field(..., description="Security type (STK, OPT, etc.)")
    exchange: str = Field(..., description="Exchange")
    local_symbol: str | None = Field(default=None, description="Local symbol")
    trading_class: str | None = Field(default=None, description="Trading class")


__all__ = [
    # Instruments
    "Instrument",
    # Market Data
    "Bar",
    "PriceBar",  # Alias
    "Quote",
    "Trade",
    "MarketDepth",
    # Options
    "OptionSnapshot",
    "OptionContract",  # Alias
    "OptionGreeks",
    "OptionChain",
    # Portfolio
    "Position",
    "AccountSummary",
    "PortfolioUpdate",
    # Metadata
    "EventMeta",
    "Health",
    # Contract
    "Contract",
]

