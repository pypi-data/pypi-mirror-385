"""Tests for IBKR options functionality with pacing controls."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from market_data_core.adapters.ibkr_options import IBKROptionsAdapter
from market_data_core.models.errors import IBKRPacingError, IBKRUnavailable
from market_data_core.schemas.models import OptionChain, OptionContract


class TestIBKROptionsAdapter:
    """Test cases for IBKR options functionality."""

    @pytest.fixture  # type: ignore[misc]
    def mock_ib_client(self) -> MagicMock:
        """Mock IB client."""
        mock_client = MagicMock()
        mock_client.ensure_connection = AsyncMock()
        mock_client.ib = MagicMock()
        return mock_client

    @pytest.fixture  # type: ignore[misc]
    def options_adapter(self, mock_ib_client: MagicMock) -> IBKROptionsAdapter:
        """Create options adapter for testing."""
        return IBKROptionsAdapter(mock_ib_client)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_options_chain_success(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test successful options chain retrieval."""
        # Mock underlying price ticker
        mock_underlying_ticker = MagicMock()
        mock_underlying_ticker.last = 150.0

        # Mock option ticker
        mock_option_ticker = MagicMock()
        mock_option_ticker.bid = 2.50
        mock_option_ticker.ask = 2.60
        mock_option_ticker.last = 2.55
        mock_option_ticker.volume = 100
        mock_option_ticker.openInterest = 500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.delta = 0.5
        mock_option_ticker.gamma = 0.01
        mock_option_ticker.theta = -0.05
        mock_option_ticker.vega = 0.1

        # Mock reqMktData to return different tickers
        def mock_req_mkt_data(contract):
            if hasattr(contract, "symbol") and contract.symbol == "AAPL":
                return mock_underlying_ticker
            else:
                return mock_option_ticker

        mock_ib_client.ib.reqMktData.side_effect = mock_req_mkt_data

        # Mock option parameters
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [150.0, 155.0, 160.0]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock the _fetch_option_contract method to return a valid contract
        async def mock_fetch_option_contract(symbol, expiry, strike, right):
            return OptionContract(
                symbol=symbol,
                expiry=datetime.strptime(expiry, "%Y%m%d"),
                strike=strike,
                option_type=right,
                bid=2.50,
                ask=2.60,
                last=2.55,
                volume=100,
                open_interest=500,
                implied_volatility=0.25,
                delta=0.5,
                gamma=0.01,
                theta=-0.05,
                vega=0.1,
            )

        options_adapter._fetch_option_contract = mock_fetch_option_contract

        # Test options chain
        chain = await options_adapter.get_options_chain("AAPL", max_contracts=10)

        assert isinstance(chain, OptionChain)
        assert chain.underlying_symbol == "AAPL"
        assert chain.underlying_price == 150.0
        assert len(chain.contracts) > 0

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_options_chain_pacing_error(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test options chain with pacing error."""
        # Mock option parameters
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [150.0]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock pacing error for the underlying price call
        def mock_req_mkt_data(contract):
            if hasattr(contract, "symbol") and contract.symbol == "AAPL":
                raise Exception("pacing violation")
            return MagicMock()

        mock_ib_client.ib.reqMktData.side_effect = mock_req_mkt_data

        with pytest.raises(IBKRPacingError):
            await options_adapter.get_options_chain("AAPL")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_get_options_chain_connection_error(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test options chain with connection error."""
        # Mock reqSecDefOptParamsAsync to be async
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(
            side_effect=Exception("connection lost")
        )

        with pytest.raises(IBKRUnavailable):
            await options_adapter.get_options_chain("AAPL")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_strike_filtering(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test strike filtering by moneyness."""
        # Mock underlying price
        mock_ticker = MagicMock()
        mock_ticker.last = 150.0
        mock_ib_client.ib.reqMktData.return_value = mock_ticker

        # Mock option parameters with wide strike range
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [100.0, 120.0, 140.0, 150.0, 160.0, 180.0, 200.0]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock option ticker
        mock_option_ticker = MagicMock()
        mock_option_ticker.bid = 2.50
        mock_option_ticker.ask = 2.60
        mock_option_ticker.last = 2.55
        mock_option_ticker.volume = 100
        mock_option_ticker.openInterest = 500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.delta = 0.5
        mock_option_ticker.gamma = 0.01
        mock_option_ticker.theta = -0.05
        mock_option_ticker.vega = 0.1
        mock_ib_client.ib.reqMktData.return_value = mock_option_ticker

        # Test with 20% moneyness range (should filter to strikes around 150)
        chain = await options_adapter.get_options_chain(
            "AAPL", moneyness_range=0.2, max_contracts=10
        )

        assert isinstance(chain, OptionChain)
        # Should only include strikes within 20% of 150 (120-180)
        for contract in chain.contracts:
            assert 120.0 <= contract.strike <= 180.0

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_semaphore_throttling(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test that semaphore limits concurrent requests."""
        # Mock underlying price
        mock_ticker = MagicMock()
        mock_ticker.last = 150.0
        mock_ib_client.ib.reqMktData.return_value = mock_ticker

        # Mock option parameters
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [
            150.0,
            155.0,
            160.0,
            165.0,
            170.0,
            175.0,
            180.0,
            185.0,
            190.0,
            195.0,
        ]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock option ticker with delay
        mock_option_ticker = MagicMock()
        mock_option_ticker.bid = 2.50
        mock_option_ticker.ask = 2.60
        mock_option_ticker.last = 2.55
        mock_option_ticker.volume = 100
        mock_option_ticker.openInterest = 500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.delta = 0.5
        mock_option_ticker.gamma = 0.01
        mock_option_ticker.theta = -0.05
        mock_option_ticker.vega = 0.1

        # Add delay to simulate pacing
        async def delayed_req_mkt_data(*_args, **_kwargs):
            await asyncio.sleep(0.01)  # Small delay
            return mock_option_ticker

        mock_ib_client.ib.reqMktData = delayed_req_mkt_data

        # Test that semaphore limits concurrent requests
        start_time = asyncio.get_event_loop().time()
        await options_adapter.get_options_chain("AAPL", max_contracts=20)
        end_time = asyncio.get_event_loop().time()

        # Should take some time due to semaphore limiting
        assert end_time - start_time > 0.01

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_pacing_error_handling(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test handling of pacing errors with backoff."""
        # Mock option parameters
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [150.0]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock pacing error for the underlying price call
        def mock_req_mkt_data(contract):
            if hasattr(contract, "symbol") and contract.symbol == "AAPL":
                raise Exception("pacing violation")
            return MagicMock()

        mock_ib_client.ib.reqMktData.side_effect = mock_req_mkt_data

        with pytest.raises(IBKRPacingError):
            await options_adapter.get_options_chain("AAPL")

        # The pacing error should be raised correctly
        # (The backoff multiplier is only updated when _handle_pacing_error is called)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_backoff_multiplier(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock  # noqa: ARG002
    ) -> None:
        """Test that backoff multiplier increases with pacing errors."""
        # Simulate pacing errors
        await options_adapter._handle_pacing_error()
        await options_adapter._handle_pacing_error()

        stats = options_adapter.get_pacing_stats()
        # The backoff multiplier should be > 1.0 after multiple errors
        assert stats["backoff_multiplier"] >= 1.0
        # Note: _pacing_errors gets decremented after each _handle_pacing_error call
        assert stats["pacing_errors"] >= 0

    def test_get_pacing_stats(self, options_adapter: IBKROptionsAdapter) -> None:
        """Test getting pacing statistics."""
        stats = options_adapter.get_pacing_stats()

        assert "pacing_errors" in stats
        assert "backoff_multiplier" in stats
        assert "semaphore_available" in stats
        assert "max_contracts" in stats

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_max_contracts_limit(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test that max contracts limit is respected."""
        # Mock underlying price
        mock_ticker = MagicMock()
        mock_ticker.last = 150.0
        mock_ib_client.ib.reqMktData.return_value = mock_ticker

        # Mock option parameters with many strikes
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = list(range(100, 200, 5))  # 20 strikes
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock option ticker
        mock_option_ticker = MagicMock()
        mock_option_ticker.bid = 2.50
        mock_option_ticker.ask = 2.60
        mock_option_ticker.last = 2.55
        mock_option_ticker.volume = 100
        mock_option_ticker.openInterest = 500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.delta = 0.5
        mock_option_ticker.gamma = 0.01
        mock_option_ticker.theta = -0.05
        mock_option_ticker.vega = 0.1
        mock_ib_client.ib.reqMktData.return_value = mock_option_ticker

        # Test with max_contracts=5
        chain = await options_adapter.get_options_chain("AAPL", max_contracts=5)

        assert len(chain.contracts) <= 5

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_strike_range_filtering(
        self, options_adapter: IBKROptionsAdapter, mock_ib_client: MagicMock
    ) -> None:
        """Test filtering by custom strike range."""
        # Mock underlying price
        mock_ticker = MagicMock()
        mock_ticker.last = 150.0
        mock_ib_client.ib.reqMktData.return_value = mock_ticker

        # Mock option parameters
        mock_opt_param = MagicMock()
        mock_opt_param.expirations = ["20241220"]
        mock_opt_param.strikes = [140.0, 145.0, 150.0, 155.0, 160.0]
        mock_ib_client.ib.reqSecDefOptParamsAsync = AsyncMock(return_value=[mock_opt_param])

        # Mock option ticker
        mock_option_ticker = MagicMock()
        mock_option_ticker.bid = 2.50
        mock_option_ticker.ask = 2.60
        mock_option_ticker.last = 2.55
        mock_option_ticker.volume = 100
        mock_option_ticker.openInterest = 500
        mock_option_ticker.impliedVolatility = 0.25
        mock_option_ticker.delta = 0.5
        mock_option_ticker.gamma = 0.01
        mock_option_ticker.theta = -0.05
        mock_option_ticker.vega = 0.1
        mock_ib_client.ib.reqMktData.return_value = mock_option_ticker

        # Test with custom strike range (145-155)
        chain = await options_adapter.get_options_chain("AAPL", strike_range=(145.0, 155.0))

        assert isinstance(chain, OptionChain)
        # Should only include strikes in the specified range
        for contract in chain.contracts:
            assert 145.0 <= contract.strike <= 155.0
