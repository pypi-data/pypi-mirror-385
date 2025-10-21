from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Position(BaseModel):
    """Account position with Decimal precision for money values."""

    symbol: str = Field(..., description="Symbol")
    position: Decimal = Field(..., description="Position size")
    avg_cost: Decimal = Field(..., description="Average cost")
    market_price: Decimal = Field(..., description="Current market price")
    market_value: Decimal = Field(..., description="Market value")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    realized_pnl: Decimal = Field(..., description="Realized P&L")


class AccountSummary(BaseModel):
    """Account summary with Decimal precision."""

    account_id: str = Field(..., description="Account ID")
    net_liquidation: Decimal = Field(..., description="Net liquidation value")
    total_cash: Decimal = Field(..., description="Total cash")
    buying_power: Decimal = Field(..., description="Buying power")
    positions: list[Position] = Field(default_factory=list, description="Account positions")


class PortfolioUpdate(BaseModel):
    """Portfolio update with timezone-aware timestamps."""

    account_id: str = Field(..., description="Account ID")
    net_liquidation: Decimal = Field(..., description="Net liquidation value")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    realized_pnl: Decimal = Field(..., description="Realized P&L")
    positions: list[Position] = Field(default_factory=list, description="Current positions")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now().astimezone(), description="Update timestamp"
    )
