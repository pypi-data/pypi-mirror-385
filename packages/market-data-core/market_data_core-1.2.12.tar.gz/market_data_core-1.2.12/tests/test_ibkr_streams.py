"""Tests for IBKR streaming functionality."""

import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from market_data_core.adapters.ibkr_streams import IBKRStreams
from market_data_core.models.errors import IBKRPacingError, IBKRUnavailable
from market_data_core.schemas.models import MarketDepth, PortfolioUpdate, Quote


class TestIBKRStreams:
    """Test cases for IBKR streaming functionality."""

    @pytest.fixture  # type: ignore[misc]
    def mock_ib_client(self) -> MagicMock:
        """Mock IB client."""
        mock_client = MagicMock()
        mock_client.ib = MagicMock()
        mock_client.ensure_connection = AsyncMock()
        return mock_client

    @pytest.fixture  # type: ignore[misc]
    def streams(self, mock_ib_client: MagicMock) -> IBKRStreams:
        """Create streams instance for testing."""
        return IBKRStreams(mock_ib_client)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stream_quotes_success(
        self, streams: IBKRStreams, mock_ib_client: MagicMock
    ) -> None:
        """Test successful quote streaming."""
        # Mock ticker data
        mock_ticker = MagicMock()
        mock_ticker.bid = 149.9
        mock_ticker.ask = 150.1
        mock_ticker.last = 150.0
        mock_ticker.volume = 1000

        mock_ib_client.ib.reqMktData.return_value = mock_ticker
        mock_ib_client.ib.waitOnUpdate = AsyncMock()

        # Test streaming
        quotes = []
        async for quote in streams.stream_quotes("AAPL"):
            quotes.append(quote)
            if len(quotes) >= 2:  # Stop after 2 quotes
                break

        assert len(quotes) == 2
        assert all(isinstance(quote, Quote) for quote in quotes)
        assert all(quote.symbol == "AAPL" for quote in quotes)
        assert quotes[0].bid == Decimal("149.9")
        assert quotes[0].ask == Decimal("150.1")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stream_quotes_pacing_error(
        self, streams: IBKRStreams, mock_ib_client: MagicMock
    ) -> None:
        """Test quote streaming with pacing error."""
        mock_ib_client.ib.reqMktData.return_value = MagicMock()
        mock_ib_client.ib.waitOnUpdate = AsyncMock(side_effect=Exception("pacing violation"))

        with pytest.raises(IBKRPacingError):
            async for _quote in streams.stream_quotes("AAPL"):
                break

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stream_quotes_connection_error(
        self, streams: IBKRStreams, mock_ib_client: MagicMock
    ) -> None:
        """Test quote streaming with connection error."""
        mock_ib_client.ib.reqMktData.return_value = MagicMock()
        mock_ib_client.ib.waitOnUpdate = AsyncMock(side_effect=Exception("connection lost"))

        with pytest.raises(IBKRUnavailable):
            async for _quote in streams.stream_quotes("AAPL"):
                break

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stream_depth_success(
        self, streams: IBKRStreams, mock_ib_client: MagicMock
    ) -> None:
        """Test successful depth streaming."""
        # Mock depth data
        mock_ticker = MagicMock()
        mock_bid = MagicMock()
        mock_bid.price = 149.9
        mock_bid.size = 100
        mock_ask = MagicMock()
        mock_ask.price = 150.1
        mock_ask.size = 150
        mock_ticker.domBids = [mock_bid]
        mock_ticker.domAsks = [mock_ask]

        mock_ib_client.ib.reqMktDepth.return_value = mock_ticker
        mock_ib_client.ib.waitOnUpdate = AsyncMock()

        # Test streaming
        depths = []
        async for depth in streams.stream_depth("AAPL"):
            depths.append(depth)
            if len(depths) >= 1:  # Stop after 1 depth
                break

        assert len(depths) == 1
        assert isinstance(depths[0], MarketDepth)
        assert depths[0].symbol == "AAPL"
        assert depths[0].bids == [(Decimal("149.9"), 100)]
        assert depths[0].asks == [(Decimal("150.1"), 150)]

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stream_portfolio_success(
        self, streams: IBKRStreams, mock_ib_client: MagicMock
    ) -> None:
        """Test successful portfolio streaming."""
        # Mock account data
        mock_av1 = MagicMock()
        mock_av1.tag = "NetLiquidation"
        mock_av1.value = "100000.0"
        mock_av2 = MagicMock()
        mock_av2.tag = "TotalCashValue"
        mock_av2.value = "50000.0"
        mock_av3 = MagicMock()
        mock_av3.tag = "BuyingPower"
        mock_av3.value = "200000.0"

        mock_ib_client.ib.accountValues.return_value = [mock_av1, mock_av2, mock_av3]
        mock_ib_client.ib.positions.return_value = []
        mock_ib_client.ib.reqAccountUpdates = MagicMock()
        mock_ib_client.ib.waitOnUpdate = AsyncMock()

        # Test streaming
        portfolios = []
        async for portfolio in streams.stream_portfolio("DU123456"):
            portfolios.append(portfolio)
            if len(portfolios) >= 1:  # Stop after 1 portfolio
                break

        assert len(portfolios) == 1
        assert isinstance(portfolios[0], PortfolioUpdate)
        assert portfolios[0].account_id == "DU123456"
        assert portfolios[0].net_liquidation == 100000.0

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_ticker_reuse(self, streams: IBKRStreams, mock_ib_client: MagicMock) -> None:
        """Test that tickers are reused for the same symbol."""
        # Mock ticker with proper values
        mock_ticker = MagicMock()
        mock_ticker.bid = 149.9
        mock_ticker.ask = 150.1
        mock_ticker.last = 150.0
        mock_ticker.volume = 1000
        mock_ib_client.ib.reqMktData.return_value = mock_ticker
        mock_ib_client.ib.waitOnUpdate = AsyncMock()

        # First stream
        stream1 = streams.stream_quotes("AAPL")
        async for _quote in stream1:
            break

        # Second stream should reuse the same ticker
        stream2 = streams.stream_quotes("AAPL")
        async for _quote in stream2:
            break

        # Should only call reqMktData once
        assert mock_ib_client.ib.reqMktData.call_count == 1

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stop_stream(self, streams: IBKRStreams, mock_ib_client: MagicMock) -> None:
        """Test stopping a stream."""
        mock_ticker = MagicMock()
        mock_ib_client.ib.reqMktData.return_value = mock_ticker
        mock_ib_client.ib.cancelMktData = MagicMock()

        # Start stream in background
        stream_task = asyncio.create_task(self._consume_stream(streams.stream_quotes("AAPL")))

        # Give it a moment to start
        await asyncio.sleep(0.1)

        # Stop stream
        await streams.stop_stream("quotes", "AAPL")

        # Cancel the task
        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass

        # Should cancel the market data subscription
        mock_ib_client.ib.cancelMktData.assert_called_once()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_stop_all_streams(self, streams: IBKRStreams, mock_ib_client: MagicMock) -> None:
        """Test stopping all streams."""
        mock_ticker = MagicMock()
        mock_ib_client.ib.reqMktData.return_value = mock_ticker
        mock_ib_client.ib.reqMktDepth.return_value = mock_ticker
        mock_ib_client.ib.reqAccountUpdates = MagicMock()
        mock_ib_client.ib.cancelMktData = MagicMock()
        mock_ib_client.ib.cancelMktDepth = MagicMock()

        # Start multiple streams in background
        quote_task = asyncio.create_task(self._consume_stream(streams.stream_quotes("AAPL")))
        depth_task = asyncio.create_task(self._consume_stream(streams.stream_depth("AAPL")))
        portfolio_task = asyncio.create_task(
            self._consume_stream(streams.stream_portfolio("DU123456"))
        )

        # Give them a moment to start
        await asyncio.sleep(0.1)

        # Stop all streams
        await streams.stop_all_streams()

        # Cancel all tasks
        for task in [quote_task, depth_task, portfolio_task]:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Should cancel all subscriptions
        mock_ib_client.ib.cancelMktData.assert_called()
        mock_ib_client.ib.cancelMktDepth.assert_called()
        mock_ib_client.ib.reqAccountUpdates.assert_called_with(False, "DU123456")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_rehydrate_streams(self, streams: IBKRStreams, mock_ib_client: MagicMock) -> None:
        """Test rehydrating streams after reconnection."""
        mock_ticker = MagicMock()
        mock_ib_client.ib.reqMktData.return_value = mock_ticker
        mock_ib_client.ib.reqMktDepth.return_value = mock_ticker
        mock_ib_client.ib.reqAccountUpdates = MagicMock()

        # Rehydrate different stream types
        await streams.rehydrate_streams("quotes", ["quotes_AAPL", "quotes_MSFT"])
        await streams.rehydrate_streams("depth", ["depth_AAPL"])
        await streams.rehydrate_streams("portfolio", ["portfolio_DU123456"])

        # Should create tickers for all symbols
        assert mock_ib_client.ib.reqMktData.call_count == 2  # AAPL, MSFT
        assert mock_ib_client.ib.reqMktDepth.call_count == 1  # AAPL
        assert mock_ib_client.ib.reqAccountUpdates.call_count == 1  # DU123456

    def test_get_ticker_stats(self, streams: IBKRStreams) -> None:
        """Test getting ticker statistics."""
        stats = streams.get_ticker_stats()

        assert "quote_tickers" in stats
        assert "depth_tickers" in stats
        assert "portfolio_tickers" in stats
        assert "active_streams" in stats

    async def _consume_stream(self, stream) -> None:
        """Helper to consume a stream."""
        try:
            async for _ in stream:
                # Just consume one item and break
                break
        except Exception:
            # Expected when stream is stopped
            pass
