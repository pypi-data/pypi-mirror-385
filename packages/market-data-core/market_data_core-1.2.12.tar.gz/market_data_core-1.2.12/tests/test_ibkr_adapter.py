"""Tests for IBKR adapter."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from market_data_core.adapters.ibkr_adapter import IBKRPriceAdapter
from market_data_core.models.market_data import PriceBar, Quote
from market_data_core.models.options import OptionChain
from market_data_core.models.portfolio import AccountSummary, Position


class TestIBKRPriceAdapter:
    """Test cases for IBKR price adapter."""

    @pytest.fixture  # type: ignore[misc]
    def adapter(self) -> IBKRPriceAdapter:
        """Create adapter instance for testing."""
        return IBKRPriceAdapter(host="127.0.0.1", port=4001, client_id=1)

    @pytest.fixture  # type: ignore[misc]
    def mock_ib(self) -> AsyncMock:
        """Mock IB connection."""
        mock_ib = AsyncMock()
        mock_ib.isConnected.return_value = True
        mock_ib.connectAsync = AsyncMock()
        return mock_ib

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_connection(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test IBKR connection."""
        with patch.object(adapter, "ib", mock_ib):
            await adapter._ensure_connection()
            assert adapter._connected
            mock_ib.connectAsync.assert_called_once()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_price_bars_success(
        self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock
    ) -> None:
        """Test successful price bars retrieval."""
        # Mock bar data
        mock_bar = MagicMock()
        mock_bar.date = datetime.now()
        mock_bar.open = 100.0
        mock_bar.high = 101.0
        mock_bar.low = 99.0
        mock_bar.close = 100.5
        mock_bar.volume = 1000

        mock_ib.reqHistoricalDataAsync = AsyncMock(return_value=[mock_bar])

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            bars = await adapter.get_price_bars("AAPL", "1d", 10)
            bars_list = list(bars)

            assert len(bars_list) == 1
            assert isinstance(bars_list[0], PriceBar)
            assert bars_list[0].symbol == "AAPL"
            assert bars_list[0].open == Decimal("100.0")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_price_bars_fallback(
        self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock
    ) -> None:
        """Test fallback to synthetic data."""
        mock_ib.reqHistoricalDataAsync = AsyncMock(side_effect=Exception("IBKR error"))

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            # This test is now expected to raise an exception since we removed silent fallbacks
            with pytest.raises(Exception, match="IBKR error"):
                await adapter.get_price_bars("AAPL", "1d", 5)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_options_chain(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test options chain retrieval."""
        # Mock ticker data
        mock_ticker = MagicMock()
        mock_ticker.last = 150.0
        mock_ticker.bid = 149.9
        mock_ticker.ask = 150.1
        mock_ticker.volume = 1000
        mock_ticker.openInterest = 500
        mock_ticker.impliedVolatility = 0.25
        mock_ticker.delta = 0.5
        mock_ticker.gamma = 0.01
        mock_ticker.theta = -0.05
        mock_ticker.vega = 0.1

        mock_ib.reqMktData = MagicMock(return_value=mock_ticker)
        mock_ib.sleep = AsyncMock()

        # Mock options data
        mock_opt_contract = MagicMock()
        mock_opt_contract.expirations = ["20241220"]
        mock_opt_contract.strikes = [150.0]

        mock_ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_contract])

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            chain = await adapter.get_options_chain("AAPL")

            assert isinstance(chain, OptionChain)
            assert chain.underlying_symbol == "AAPL"
            assert chain.underlying_price == Decimal("150.0")
            assert len(chain.contracts) > 0

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_positions(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test positions retrieval."""
        # Mock position data
        mock_position = MagicMock()
        mock_position.contract.symbol = "AAPL"
        mock_position.position = 100.0
        mock_position.avgCost = 150.0
        mock_position.marketPrice = 155.0
        mock_position.marketValue = 15500.0
        mock_position.unrealizedPNL = 500.0
        mock_position.realizedPNL = 0.0

        mock_ib.positions = MagicMock(return_value=[mock_position])

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            positions = await adapter.get_positions()

            assert len(positions) == 1
            assert isinstance(positions[0], Position)
            assert positions[0].symbol == "AAPL"
            assert positions[0].position == Decimal("100.0")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_account_summary(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test account summary retrieval."""
        # Mock account values
        mock_av1 = MagicMock()
        mock_av1.tag = "NetLiquidation"
        mock_av1.value = "100000.0"

        mock_av2 = MagicMock()
        mock_av2.tag = "TotalCashValue"
        mock_av2.value = "50000.0"

        mock_av3 = MagicMock()
        mock_av3.tag = "BuyingPower"
        mock_av3.value = "200000.0"

        mock_ib.accountValues = MagicMock(return_value=[mock_av1, mock_av2, mock_av3])
        mock_ib.positions = MagicMock(return_value=[])

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            summary = await adapter.get_account_summary("DU123456")

            assert isinstance(summary, AccountSummary)
            assert summary.account_id == "DU123456"
            assert summary.net_liquidation == Decimal("100000.0")
            assert summary.total_cash == Decimal("50000.0")
            assert summary.buying_power == Decimal("200000.0")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_start_quote_stream(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test quote streaming."""
        # Mock ticker data
        mock_ticker = MagicMock()
        mock_ticker.bid = 149.9
        mock_ticker.ask = 150.1
        mock_ticker.last = 150.0
        mock_ticker.volume = 1000

        mock_ib.reqMktData = MagicMock(return_value=mock_ticker)
        mock_ib.sleep = AsyncMock()

        with patch.object(adapter, "ib", mock_ib):
            adapter._connected = True
            quote = await adapter.start_quote_stream("AAPL")

            assert isinstance(quote, Quote)
            assert quote.symbol == "AAPL"
            assert quote.bid == Decimal("149.9")
            assert quote.ask == Decimal("150.1")
            assert quote.last == Decimal("150.0")

    def test_convert_bar(self, adapter: IBKRPriceAdapter) -> None:
        """Test bar conversion."""
        # Mock bar data
        mock_bar = MagicMock()
        mock_bar.date = datetime.now()
        mock_bar.open = 100.0
        mock_bar.high = 101.0
        mock_bar.low = 99.0
        mock_bar.close = 100.5
        mock_bar.volume = 1000

        result = adapter._convert_bar(mock_bar, "AAPL")

        assert isinstance(result, PriceBar)
        assert result.symbol == "AAPL"
        assert result.open == Decimal("100.0")
        assert result.high == Decimal("101.0")
        assert result.low == Decimal("99.0")
        assert result.close == Decimal("100.5")
        assert result.volume == Decimal("1000")

    def test_synthetic_bars(self, adapter: IBKRPriceAdapter) -> None:
        """Test synthetic bars generation."""
        bars = adapter._get_synthetic_bars("AAPL", 3)

        assert len(bars) == 3
        assert all(isinstance(bar, PriceBar) for bar in bars)
        assert all(bar.symbol == "AAPL" for bar in bars)
        assert all(bar.open == 100.0 for bar in bars)

    def test_is_connected(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test connection status check."""
        adapter._connected = True
        mock_ib.isConnected.return_value = True

        with patch.object(adapter, "ib", mock_ib):
            assert adapter.is_connected()

        mock_ib.isConnected.return_value = False
        assert not adapter.is_connected()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_disconnect(self, adapter: IBKRPriceAdapter, mock_ib: AsyncMock) -> None:
        """Test disconnection."""
        adapter._connected = True
        mock_ib.disconnect = MagicMock()

        with patch.object(adapter, "ib", mock_ib):
            await adapter.disconnect()

            assert not adapter._connected
            mock_ib.disconnect.assert_called_once()
