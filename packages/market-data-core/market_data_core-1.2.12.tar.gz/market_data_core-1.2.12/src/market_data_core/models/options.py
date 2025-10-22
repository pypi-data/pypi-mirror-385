from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class OptionContract(BaseModel):
    """Option contract with Greeks."""

    symbol: str = Field(..., description="Underlying symbol")
    expiry: datetime = Field(..., description="Expiration date")
    strike: Decimal = Field(..., description="Strike price")
    option_type: Literal["C", "P"] = Field(..., description="Call or Put")
    bid: Decimal | None = Field(None, description="Bid price")
    ask: Decimal | None = Field(None, description="Ask price")
    last: Decimal | None = Field(None, description="Last trade price")
    volume: int = Field(0, description="Trading volume")
    open_interest: int = Field(0, description="Open interest")
    implied_volatility: Decimal | None = Field(None, description="Implied volatility")
    delta: Decimal | None = Field(None, description="Delta")
    gamma: Decimal | None = Field(None, description="Gamma")
    theta: Decimal | None = Field(None, description="Theta")
    vega: Decimal | None = Field(None, description="Vega")
    delayed: bool = Field(False, description="Whether data is delayed")


class OptionChain(BaseModel):
    """Options chain for an underlying."""

    underlying_symbol: str = Field(..., description="Underlying symbol")
    underlying_price: Decimal = Field(..., description="Current underlying price")
    contracts: list[OptionContract] = Field(default_factory=list, description="Option contracts")
    delayed: bool = Field(False, description="Whether data is delayed")
