"""Deprecated IBKR adapter module.

This module is deprecated and will be removed in v2.0.
For new projects, use market_data_ibkr package (separate provider implementation).
This module requires optional dependencies.

Install with: pip install 'market-data-core[compat]'
"""
import warnings

warnings.warn(
    "adapters.ibkr_adapter module is deprecated and will be removed in v2.0. "
    "Install optional dependencies with: pip install 'market-data-core[compat]'",
    DeprecationWarning,
    stacklevel=2,
)

import asyncio
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

try:
    from ib_async import IB, Option, Stock
    from loguru import logger
except ImportError as e:
    raise RuntimeError(
        "This deprecated module requires optional dependencies. "
        "Install with: pip install 'market-data-core[compat]'"
    ) from e

from ..schemas.models import (
    AccountSummary,
    MarketDepth,
    OptionChain,
    OptionContract,
    PortfolioUpdate,
    Position,
    PriceBar,
    Quote,
)
from ..utils.resilience import RetryConfig, with_circuit_breaker, with_retry
from .base import PriceDataProvider


class IBKRPriceAdapter(PriceDataProvider):
    """
    IBKR adapter using ib_async for real-time market data and trading.
    Replaces OpenBB with direct Interactive Brokers integration.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
        self._connected = False

    async def _ensure_connection(self) -> None:
        """Ensure IBKR connection is established."""
        if not self._connected:
            try:
                await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
                self._connected = True
            except Exception as e:
                raise ConnectionError(f"Failed to connect to IBKR: {e}") from e

    @with_retry(RetryConfig.STANDARD)  # type: ignore[misc]  # type: ignore[misc]
    @with_circuit_breaker(failure_threshold=3, recovery_timeout=30)  # type: ignore[misc]
    async def get_price_bars(
        self, symbol: str, interval: str = "1d", limit: int = 100
    ) -> Iterable[PriceBar]:
        """Get historical price bars from IBKR."""
        await self._ensure_connection()

        # Map interval to IBKR format
        bar_size_map = {
            "1m": "1 min",
            "5m": "5 mins",
            "15m": "15 mins",
            "30m": "30 mins",
            "1h": "1 hour",
            "1d": "1 day",
            "1w": "1 week",
            "1M": "1 month",
        }

        bar_size = bar_size_map.get(interval, "1 day")
        duration = f"{limit} D" if interval in ["1d", "1w", "1M"] else f"{limit * 5} D"

        try:
            contract = Stock(symbol, "SMART", "USD")
            bars = await self.ib.reqHistoricalDataAsync(
                contract,
                endDateTime="",
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow="TRADES",
                useRTH=True,
            )

            return [self._convert_bar(bar, symbol) for bar in bars]

        except Exception as e:
            # Log the error and re-raise instead of silent fallback
            logger.error(f"Failed to get price bars for {symbol}: {e}")
            raise

    @with_retry(RetryConfig.LIGHT)  # type: ignore[misc]
    @with_circuit_breaker(failure_threshold=2, recovery_timeout=60)  # type: ignore[misc]
    async def get_options_chain(self, symbol: str, expiry: str | None = None) -> OptionChain:
        """Get options chain for a symbol using the improved options adapter."""
        await self._ensure_connection()

        try:
            # Use the improved options adapter if available
            if hasattr(self, "_options_adapter"):
                result: OptionChain = await self._options_adapter.get_options_chain(symbol, expiry)
                return result

            # Fallback to original implementation
            return await self._get_options_chain_legacy(symbol, expiry)

        except Exception as e:
            # Log the error and re-raise instead of silent fallback
            logger.error(f"Failed to get options chain for {symbol}: {e}")
            raise

    async def _get_options_chain_legacy(
        self, symbol: str, expiry: str | None = None
    ) -> OptionChain:
        """Legacy options chain implementation."""
        # Get underlying price
        contract = Stock(symbol, "SMART", "USD")
        ticker = self.ib.reqMktData(contract)
        await asyncio.sleep(1)  # Wait for data

        underlying_price = ticker.last if ticker.last else 0.0

        # Get options chain
        option_contracts = await self.ib.reqSecDefOptParamsAsync(symbol, "", "", 0)

        contracts = []
        for opt_contract in option_contracts:
            if expiry and opt_contract.expirations:
                # Filter by expiry if specified
                if expiry not in opt_contract.expirations:
                    continue

            # Get option details
            for strike in opt_contract.strikes:
                for right in ["C", "P"]:  # Call and Put
                    option = Option(
                        symbol,
                        opt_contract.expirations[0] if opt_contract.expirations else "",
                        strike,
                        right,
                        "SMART",
                    )

                    try:
                        ticker = self.ib.reqMktData(option)
                        await asyncio.sleep(0.1)

                        contracts.append(
                            OptionContract(
                                symbol=symbol,
                                expiry=datetime.strptime(opt_contract.expirations[0], "%Y%m%d"),
                                strike=Decimal(str(strike)),
                                option_type=right,  # type: ignore
                                bid=Decimal(str(ticker.bid)) if ticker.bid else None,
                                ask=Decimal(str(ticker.ask)) if ticker.ask else None,
                                last=Decimal(str(ticker.last)) if ticker.last else None,
                                volume=int(ticker.volume) if ticker.volume else 0,
                                open_interest=getattr(ticker, "openInterest", 0),
                                implied_volatility=(
                                    Decimal(str(ticker.impliedVolatility))
                                    if getattr(ticker, "impliedVolatility", None)
                                    else None
                                ),
                                delta=(
                                    Decimal(str(getattr(ticker, "delta", 0)))
                                    if getattr(ticker, "delta", None)
                                    else None
                                ),
                                gamma=(
                                    Decimal(str(getattr(ticker, "gamma", 0)))
                                    if getattr(ticker, "gamma", None)
                                    else None
                                ),
                                theta=(
                                    Decimal(str(getattr(ticker, "theta", 0)))
                                    if getattr(ticker, "theta", None)
                                    else None
                                ),
                                vega=(
                                    Decimal(str(getattr(ticker, "vega", 0)))
                                    if getattr(ticker, "vega", None)
                                    else None
                                ),
                                delayed=False,
                            )
                        )
                    except Exception:
                        # Skip invalid options
                        continue

        return OptionChain(
            underlying_symbol=symbol,
            underlying_price=Decimal(str(underlying_price)),
            contracts=contracts,
            delayed=False,
        )

    @with_retry(RetryConfig.STANDARD)  # type: ignore[misc]
    async def get_positions(self) -> list[Position]:
        """Get current account positions."""
        await self._ensure_connection()

        try:
            positions = self.ib.positions()
            return [
                Position(
                    symbol=pos.contract.symbol,
                    position=Decimal(str(pos.position)),
                    avg_cost=Decimal(str(pos.avgCost)),
                    market_price=Decimal(str(getattr(pos, "marketPrice", 0))),
                    market_value=Decimal(str(getattr(pos, "marketValue", 0))),
                    unrealized_pnl=Decimal(str(getattr(pos, "unrealizedPNL", 0))),
                    realized_pnl=Decimal(str(getattr(pos, "realizedPNL", 0))),
                )
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise

    @with_retry(RetryConfig.STANDARD)  # type: ignore[misc]
    async def get_account_summary(self, account_id: str) -> AccountSummary:
        """Get account summary."""
        await self._ensure_connection()

        try:
            # Get account values
            account_values = self.ib.accountValues()

            net_liquidation = 0.0
            total_cash = 0.0
            buying_power = 0.0

            for av in account_values:
                if av.tag == "NetLiquidation":
                    net_liquidation = float(av.value)
                elif av.tag == "TotalCashValue":
                    total_cash = float(av.value)
                elif av.tag == "BuyingPower":
                    buying_power = float(av.value)

            positions = await self.get_positions()

            return AccountSummary(
                account_id=account_id,
                net_liquidation=Decimal(str(net_liquidation)),
                total_cash=Decimal(str(total_cash)),
                buying_power=Decimal(str(buying_power)),
                positions=positions,
            )
        except Exception as e:
            logger.error(f"Failed to get account summary for {account_id}: {e}")
            raise

    def _convert_bar(self, bar: Any, symbol: str) -> PriceBar:
        """Convert IBKR bar to PriceBar."""
        return PriceBar(
            symbol=symbol,
            ts=bar.date,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            delayed=False,
        )

    def _get_synthetic_bars(self, symbol: str, limit: int) -> list[PriceBar]:
        """Fallback synthetic data when IBKR is unavailable."""
        now = datetime.now(UTC)
        bars = []
        for i in range(limit):
            ts = now - timedelta(days=i)
            bars.append(
                PriceBar(
                    symbol=symbol,
                    ts=ts,
                    open=Decimal("100.0"),
                    high=Decimal("101.0"),
                    low=Decimal("99.0"),
                    close=Decimal("100.5"),
                    volume=Decimal("1000.0"),
                    delayed=False,
                )
            )
        return list(reversed(bars))

    async def disconnect(self) -> None:
        """Disconnect from IBKR."""
        if self._connected:
            self.ib.disconnect()
            self._connected = False

    def is_connected(self) -> bool:
        """Check if connected to IBKR."""
        return self._connected and self.ib.isConnected()

    async def start_quote_stream(self, symbol: str) -> Quote:
        """Start streaming real-time quotes for a symbol."""
        await self._ensure_connection()

        try:
            contract = Stock(symbol, "SMART", "USD")
            ticker = self.ib.reqMktData(contract)

            # Wait for initial data
            await asyncio.sleep(1)

            return Quote(
                symbol=symbol,
                bid=Decimal(str(ticker.bid)) if ticker.bid else None,
                ask=Decimal(str(ticker.ask)) if ticker.ask else None,
                last=Decimal(str(ticker.last)) if ticker.last else None,
                volume=int(ticker.volume) if ticker.volume else 0,
                delayed=False,
            )
        except Exception as e:
            logger.error(f"Failed to get quote stream for {symbol}: {e}")
            raise

    async def start_market_depth_stream(self, symbol: str) -> MarketDepth:
        """Start streaming market depth (Level 2) for a symbol."""
        await self._ensure_connection()

        try:
            contract = Stock(symbol, "SMART", "USD")
            ticker = self.ib.reqMktDepth(contract)

            # Wait for initial data
            await asyncio.sleep(1)

            # Convert IBKR depth data to our format
            bids = [(Decimal(str(level.price)), int(level.size)) for level in ticker.domBids]
            asks = [(Decimal(str(level.price)), int(level.size)) for level in ticker.domAsks]

            return MarketDepth(symbol=symbol, bids=bids, asks=asks, delayed=False)
        except Exception as e:
            logger.error(f"Failed to get depth stream for {symbol}: {e}")
            raise

    async def start_portfolio_stream(self, account_id: str) -> PortfolioUpdate:
        """Start streaming portfolio updates for an account."""
        await self._ensure_connection()

        try:
            # Get account summary
            summary = await self.get_account_summary(account_id)

            # Calculate total P&L
            total_unrealized = sum(pos.unrealized_pnl for pos in summary.positions)
            total_realized = sum(pos.realized_pnl for pos in summary.positions)

            return PortfolioUpdate(
                account_id=account_id,
                net_liquidation=summary.net_liquidation,
                unrealized_pnl=total_unrealized,
                realized_pnl=total_realized,
                positions=summary.positions,
            )
        except Exception as e:
            logger.error(f"Failed to get portfolio stream for {account_id}: {e}")
            raise
