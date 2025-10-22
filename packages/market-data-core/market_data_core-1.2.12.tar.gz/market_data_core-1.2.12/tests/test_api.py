"""Tests for API endpoints."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from market_data_core.models.market_data import PriceBar, Quote
from market_data_core.models.options import OptionChain
from market_data_core.models.portfolio import AccountSummary, Position
from market_data_core.services.api import app


class TestAPI:
    """Test cases for API endpoints."""

    @pytest.fixture  # type: ignore[misc]
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    @pytest.fixture  # type: ignore[misc]
    def mock_adapter(self) -> MagicMock:
        """Mock IBKR adapter."""
        mock_adapter = AsyncMock()

        # Mock price bars
        mock_bars = [
            PriceBar(
                symbol="AAPL",
                ts=datetime.now(),
                open=Decimal("100.0"),
                high=Decimal("101.0"),
                low=Decimal("99.0"),
                close=Decimal("100.5"),
                volume=Decimal("1000"),
            )
        ]
        mock_adapter.get_price_bars.return_value = mock_bars

        # Mock quote
        mock_quote = Quote(
            symbol="AAPL",
            bid=Decimal("149.9"),
            ask=Decimal("150.1"),
            last=Decimal("150.0"),
            volume=1000,
        )
        mock_adapter.start_quote_stream.return_value = mock_quote

        # Mock positions
        mock_positions = [
            Position(
                symbol="AAPL",
                position=Decimal("100.0"),
                avg_cost=Decimal("150.0"),
                market_price=Decimal("155.0"),
                market_value=Decimal("15500.0"),
                unrealized_pnl=Decimal("500.0"),
                realized_pnl=Decimal("0.0"),
            )
        ]
        mock_adapter.get_positions.return_value = mock_positions

        # Mock account summary
        mock_summary = AccountSummary(
            account_id="DU123456",
            net_liquidation=Decimal("100000.0"),
            total_cash=Decimal("50000.0"),
            buying_power=Decimal("200000.0"),
            positions=mock_positions,
        )
        mock_adapter.get_account_summary.return_value = mock_summary

        # Mock options chain
        mock_chain = OptionChain(
            underlying_symbol="AAPL",
            underlying_price=Decimal("150.0"),
            contracts=[],
        )
        mock_adapter.get_options_chain.return_value = mock_chain

        return mock_adapter

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "ibkr_connected" in data

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.facade")
    def test_prices_endpoint_success(
        self, mock_facade: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test successful prices endpoint."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the facade
        mock_facade.get_price_bars = AsyncMock(
            return_value=[
                PriceBar(
                    symbol="AAPL",
                    ts=datetime.now(),
                    open=Decimal("100.0"),
                    high=Decimal("101.0"),
                    low=Decimal("99.0"),
                    close=Decimal("100.5"),
                    volume=Decimal("1000"),
                )
            ]
        )

        response = client.get("/prices?symbol=AAPL&interval=1d&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "AAPL"

    def test_prices_endpoint_validation_error(self, client: TestClient) -> None:
        """Test prices endpoint with validation error."""
        response = client.get("/prices?symbol=AAPL&interval=invalid")
        assert response.status_code == 422

        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "validation_error"

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.ibkr_adapter")
    def test_options_endpoint(
        self, mock_adapter: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test options endpoint."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the adapter
        mock_adapter.get_options_chain = AsyncMock(
            return_value=OptionChain(
                underlying_symbol="AAPL",
                underlying_price=Decimal("150.0"),
                contracts=[],
            )
        )

        response = client.get("/options?symbol=AAPL")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert data["data"]["underlying_symbol"] == "AAPL"

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.ibkr_adapter")
    def test_positions_endpoint(
        self, mock_adapter: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test positions endpoint."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the adapter
        mock_adapter.get_positions = AsyncMock(
            return_value=[
                Position(
                    symbol="AAPL",
                    position=Decimal("100.0"),
                    avg_cost=Decimal("150.0"),
                    market_price=Decimal("155.0"),
                    market_value=Decimal("15500.0"),
                    unrealized_pnl=Decimal("500.0"),
                    realized_pnl=Decimal("0.0"),
                )
            ]
        )

        response = client.get("/positions")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["symbol"] == "AAPL"

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.ibkr_adapter")
    def test_account_endpoint(
        self, mock_adapter: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test account endpoint."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the adapter
        mock_adapter.get_account_summary = AsyncMock(
            return_value=AccountSummary(
                account_id="DU123456",
                net_liquidation=Decimal("100000.0"),
                total_cash=Decimal("50000.0"),
                buying_power=Decimal("200000.0"),
                positions=[],
            )
        )

        response = client.get("/account?account_id=DU123456")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert data["data"]["account_id"] == "DU123456"
        assert data["data"]["net_liquidation"] == "100000.0"

    @patch("market_data_core.services.api.ib_client")
    def test_contracts_resolve_endpoint(self, mock_client: MagicMock, client: TestClient) -> None:
        """Test contract resolution endpoint."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        response = client.get("/contracts/resolve?symbol=AAPL")
        assert response.status_code == 200

        data = response.json()
        assert "conid" in data
        assert "symbol" in data
        assert data["symbol"] == "AAPL"

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.facade")
    def test_prices_endpoint_parameters(
        self, mock_facade: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test prices endpoint with various parameters."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the facade
        mock_facade.get_price_bars = AsyncMock(return_value=[])

        # Test with different intervals
        for interval in ["1m", "5m", "1h", "1d"]:
            response = client.get(f"/prices?symbol=AAPL&interval={interval}")
            # Should not return validation error for valid intervals
            assert response.status_code == 200

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.facade")
    def test_prices_endpoint_what_parameter(
        self, mock_facade: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test prices endpoint with what parameter."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the facade
        mock_facade.get_price_bars = AsyncMock(return_value=[])

        for what in ["TRADES", "MIDPOINT", "BID", "ASK"]:
            response = client.get(f"/prices?symbol=AAPL&what={what}")
            # Should not return validation error for valid what values
            assert response.status_code == 200

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.facade")
    def test_prices_endpoint_limit_validation(
        self, mock_facade: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test prices endpoint limit validation."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the facade
        mock_facade.get_price_bars = AsyncMock(return_value=[])

        # Test valid limit
        response = client.get("/prices?symbol=AAPL&limit=100")
        assert response.status_code == 200

        # Test invalid limit (too high)
        response = client.get("/prices?symbol=AAPL&limit=2000")
        assert response.status_code == 422

    @patch("market_data_core.services.api.ib_client")
    @patch("market_data_core.services.api.ibkr_adapter")
    def test_options_endpoint_with_expiry(
        self, mock_adapter: MagicMock, mock_client: MagicMock, client: TestClient
    ) -> None:
        """Test options endpoint with expiry parameter."""
        # Mock the connection check
        mock_client.ensure_connection = AsyncMock()

        # Mock the adapter
        mock_chain = OptionChain(
            underlying_symbol="AAPL", underlying_price=Decimal("150.0"), contracts=[], delayed=False
        )
        mock_adapter.get_options_chain = AsyncMock(return_value=mock_chain)

        response = client.get("/options?symbol=AAPL&expiry=20241220")
        assert response.status_code == 200

    def test_metrics_endpoint(self, client: TestClient) -> None:
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_detailed_health_endpoint(self, client: TestClient) -> None:
        """Test detailed health endpoint."""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "metrics" in data
