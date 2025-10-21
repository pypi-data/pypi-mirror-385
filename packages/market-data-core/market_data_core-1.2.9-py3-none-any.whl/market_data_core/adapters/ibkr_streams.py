"""Real-time streaming adapter for IBKR with async generators."""

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from ib_async import Stock
from loguru import logger

from ..models.errors import IBKRPacingError, IBKRUnavailable
from ..schemas.models import MarketDepth, PortfolioUpdate, Quote


class IBKRStreams:
    """Real-time streaming adapter using async generators and shared tickers."""

    def __init__(self, ib_client: Any):
        self.ib_client = ib_client
        self._quote_tickers: dict[str, Any] = {}
        self._depth_tickers: dict[str, Any] = {}
        self._portfolio_tickers: dict[str, Any] = {}
        self._active_streams: set[str] = set()

    async def stream_quotes(self, symbol: str) -> AsyncIterator[Quote]:
        """Stream real-time quotes using shared ticker subscriptions."""
        stream_key = f"quotes_{symbol}"
        self._active_streams.add(stream_key)

        try:
            # Reuse existing ticker or create new one
            ticker = self._quote_tickers.get(symbol)
            if ticker is None:
                await self.ib_client.ensure_connection()
                contract = Stock(symbol, "SMART", "USD")
                ticker = self.ib_client.ib.reqMktData(contract)
                self._quote_tickers[symbol] = ticker
                logger.info(f"Created new quote ticker for {symbol}")

            # Stream updates
            while stream_key in self._active_streams:
                try:
                    # Wait for any IB update
                    await self.ib_client.ib.waitOnUpdate(timeout=1.0)

                    # Yield latest quote data
                    yield Quote(
                        symbol=symbol,
                        bid=ticker.bid,
                        ask=ticker.ask,
                        last=ticker.last,
                        volume=ticker.volume or 0,
                        timestamp=datetime.now(UTC),
                        delayed=False,
                    )
                except TimeoutError:
                    # No updates, continue waiting
                    continue
                except Exception as e:
                    if "pacing" in str(e).lower():
                        raise IBKRPacingError(f"Pacing violation for {symbol}: {e}") from e
                    elif "connection" in str(e).lower():
                        raise IBKRUnavailable(f"Connection lost for {symbol}: {e}") from e
                    logger.warning(f"Error in quote stream for {symbol}: {e}")
                    await asyncio.sleep(1)

        finally:
            self._active_streams.discard(stream_key)

    async def stream_depth(self, symbol: str) -> AsyncIterator[MarketDepth]:
        """Stream market depth using shared ticker subscriptions."""
        stream_key = f"depth_{symbol}"
        self._active_streams.add(stream_key)

        try:
            # Reuse existing ticker or create new one
            ticker = self._depth_tickers.get(symbol)
            if ticker is None:
                await self.ib_client.ensure_connection()
                contract = Stock(symbol, "SMART", "USD")
                ticker = self.ib_client.ib.reqMktDepth(contract)
                self._depth_tickers[symbol] = ticker
                logger.info(f"Created new depth ticker for {symbol}")

            # Stream updates
            while stream_key in self._active_streams:
                try:
                    # Wait for any IB update
                    await self.ib_client.ib.waitOnUpdate(timeout=2.0)

                    # Convert IBKR depth data to our format
                    bids = [(level.price, level.size) for level in ticker.domBids]
                    asks = [(level.price, level.size) for level in ticker.domAsks]

                    yield MarketDepth(
                        symbol=symbol,
                        bids=bids,
                        asks=asks,
                        timestamp=datetime.now(UTC),
                        delayed=False,
                    )
                except TimeoutError:
                    # No updates, continue waiting
                    continue
                except Exception as e:
                    if "pacing" in str(e).lower():
                        raise IBKRPacingError(f"Pacing violation for {symbol}: {e}") from e
                    elif "connection" in str(e).lower():
                        raise IBKRUnavailable(f"Connection lost for {symbol}: {e}") from e
                    logger.warning(f"Error in depth stream for {symbol}: {e}")
                    await asyncio.sleep(2)

        finally:
            self._active_streams.discard(stream_key)

    async def stream_portfolio(self, account_id: str) -> AsyncIterator[PortfolioUpdate]:
        """Stream portfolio updates using account value subscriptions."""
        stream_key = f"portfolio_{account_id}"
        self._active_streams.add(stream_key)

        try:
            # Reuse existing subscription or create new one
            if account_id not in self._portfolio_tickers:
                await self.ib_client.ensure_connection()
                # Subscribe to account updates
                self.ib_client.ib.reqAccountUpdates(True, account_id)
                self._portfolio_tickers[account_id] = True
                logger.info(f"Created portfolio subscription for {account_id}")

            # Stream updates
            while stream_key in self._active_streams:
                try:
                    # Wait for account updates
                    await self.ib_client.ib.waitOnUpdate(timeout=5.0)

                    # Get current positions and account values
                    positions = self.ib_client.ib.positions()
                    account_values = self.ib_client.ib.accountValues()

                    # Calculate totals
                    net_liquidation = 0.0

                    for av in account_values:
                        if av.tag == "NetLiquidation":
                            net_liquidation = float(av.value)

                    # Convert positions
                    from ..schemas.models import Position

                    position_list = [
                        Position(
                            symbol=pos.contract.symbol,
                            position=pos.position,
                            avg_cost=pos.avgCost,
                            market_price=pos.marketPrice,
                            market_value=pos.marketValue,
                            unrealized_pnl=pos.unrealizedPNL,
                            realized_pnl=pos.realizedPNL,
                        )
                        for pos in positions
                    ]

                    # Calculate P&L
                    total_unrealized = sum(pos.unrealized_pnl for pos in position_list)
                    total_realized = sum(pos.realized_pnl for pos in position_list)

                    yield PortfolioUpdate(
                        account_id=account_id,
                        net_liquidation=Decimal(str(net_liquidation)),
                        unrealized_pnl=Decimal(str(total_unrealized)),
                        realized_pnl=Decimal(str(total_realized)),
                        positions=position_list,
                        timestamp=datetime.now(UTC),
                    )
                except TimeoutError:
                    # No updates, continue waiting
                    continue
                except Exception as e:
                    if "pacing" in str(e).lower():
                        raise IBKRPacingError(f"Pacing violation for {account_id}: {e}") from e
                    elif "connection" in str(e).lower():
                        raise IBKRUnavailable(f"Connection lost for {account_id}: {e}") from e
                    logger.warning(f"Error in portfolio stream for {account_id}: {e}")
                    await asyncio.sleep(5)

        finally:
            self._active_streams.discard(stream_key)

    async def stop_stream(self, stream_type: str, identifier: str) -> None:
        """Stop a specific stream."""
        stream_key = f"{stream_type}_{identifier}"
        self._active_streams.discard(stream_key)

        # Clean up tickers if no more streams
        if stream_type == "quotes" and identifier in self._quote_tickers:
            # Cancel market data subscription
            ticker = self._quote_tickers[identifier]
            self.ib_client.ib.cancelMktData(ticker.contract)
            del self._quote_tickers[identifier]
        elif stream_type == "depth" and identifier in self._depth_tickers:
            # Cancel depth subscription
            ticker = self._depth_tickers[identifier]
            self.ib_client.ib.cancelMktDepth(ticker.contract)
            del self._depth_tickers[identifier]
        elif stream_type == "portfolio" and identifier in self._portfolio_tickers:
            # Cancel account updates
            self.ib_client.ib.reqAccountUpdates(False, identifier)
            del self._portfolio_tickers[identifier]

        logger.info(f"Stopped {stream_type} stream for {identifier}")

    async def stop_all_streams(self) -> None:
        """Stop all active streams and clean up tickers."""
        # Stop all streams
        self._active_streams.clear()

        # Cancel all market data subscriptions
        for symbol, ticker in self._quote_tickers.items():
            try:
                self.ib_client.ib.cancelMktData(ticker.contract)
            except Exception as e:
                logger.warning(f"Error canceling quote ticker for {symbol}: {e}")

        # Cancel all depth subscriptions
        for symbol, ticker in self._depth_tickers.items():
            try:
                self.ib_client.ib.cancelMktDepth(ticker.contract)
            except Exception as e:
                logger.warning(f"Error canceling depth ticker for {symbol}: {e}")

        # Cancel all account subscriptions
        for account_id in self._portfolio_tickers:
            try:
                self.ib_client.ib.reqAccountUpdates(False, account_id)
            except Exception as e:
                logger.warning(f"Error canceling portfolio subscription for {account_id}: {e}")

        # Clear all tickers
        self._quote_tickers.clear()
        self._depth_tickers.clear()
        self._portfolio_tickers.clear()

        logger.info("Stopped all streams and cleaned up tickers")

    def get_active_streams(self) -> set[str]:
        """Get set of active stream keys."""
        return self._active_streams.copy()

    async def rehydrate_streams(self, stream_type: str, subscription_ids: list[str]) -> None:
        """Rehydrate streams after reconnection."""
        logger.info(f"Rehydrating {len(subscription_ids)} {stream_type} streams")

        for subscription_id in subscription_ids:
            # Extract symbol/account from subscription ID
            if stream_type == "quotes":
                # subscription_id format: "quotes_{symbol}"
                symbol = subscription_id.replace("quotes_", "")
                if symbol not in self._quote_tickers:
                    # Recreate ticker
                    await self.ib_client.ensure_connection()
                    contract = Stock(symbol, "SMART", "USD")
                    ticker = self.ib_client.ib.reqMktData(contract)
                    self._quote_tickers[symbol] = ticker
                    logger.info(f"Rehydrated quote ticker for {symbol}")

            elif stream_type == "depth":
                # subscription_id format: "depth_{symbol}"
                symbol = subscription_id.replace("depth_", "")
                if symbol not in self._depth_tickers:
                    # Recreate ticker
                    await self.ib_client.ensure_connection()
                    contract = Stock(symbol, "SMART", "USD")
                    ticker = self.ib_client.ib.reqMktDepth(contract)
                    self._depth_tickers[symbol] = ticker
                    logger.info(f"Rehydrated depth ticker for {symbol}")

            elif stream_type == "portfolio":
                # subscription_id format: "portfolio_{account_id}"
                account_id = subscription_id.replace("portfolio_", "")
                if account_id not in self._portfolio_tickers:
                    # Recreate subscription
                    await self.ib_client.ensure_connection()
                    self.ib_client.ib.reqAccountUpdates(True, account_id)
                    self._portfolio_tickers[account_id] = True
                    logger.info(f"Rehydrated portfolio subscription for {account_id}")

    def get_ticker_stats(self) -> dict[str, int]:
        """Get statistics about active tickers."""
        return {
            "quote_tickers": len(self._quote_tickers),
            "depth_tickers": len(self._depth_tickers),
            "portfolio_tickers": len(self._portfolio_tickers),
            "active_streams": len(self._active_streams),
        }
