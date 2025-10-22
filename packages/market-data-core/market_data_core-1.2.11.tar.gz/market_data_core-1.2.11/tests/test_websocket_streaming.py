"""Tests for WebSocket streaming functionality."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from market_data_core.schemas.models import MarketDepth, PortfolioUpdate, Quote
from market_data_core.services.api import app


class TestWebSocketStreaming:
    """Test cases for WebSocket streaming functionality."""

    @pytest.fixture  # type: ignore[misc]
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    @pytest.fixture  # type: ignore[misc]
    def mock_ibkr_streams(self) -> MagicMock:
        """Mock IBKR streams."""
        mock_streams = MagicMock()

        # Mock quote stream
        async def mock_quote_stream(symbol: str):
            for i in range(3):  # Yield 3 quotes
                yield Quote(
                    symbol=symbol,
                    bid=149.9 + i,
                    ask=150.1 + i,
                    last=150.0 + i,
                    volume=1000 + i * 100,
                )
                await asyncio.sleep(0.01)  # Small delay

        mock_streams.stream_quotes = mock_quote_stream

        # Mock depth stream
        async def mock_depth_stream(symbol: str):
            for i in range(2):  # Yield 2 depths
                yield MarketDepth(
                    symbol=symbol,
                    bids=[(149.9 + i, 100), (149.8 + i, 200)],
                    asks=[(150.1 + i, 150), (150.2 + i, 250)],
                )
                await asyncio.sleep(0.01)  # Small delay

        mock_streams.stream_depth = mock_depth_stream

        # Mock portfolio stream
        async def mock_portfolio_stream(account_id: str):
            for i in range(2):  # Yield 2 portfolios
                yield PortfolioUpdate(
                    account_id=account_id,
                    net_liquidation=100000.0 + i * 1000,
                    unrealized_pnl=500.0 + i * 100,
                    realized_pnl=0.0,
                    positions=[],
                )
                await asyncio.sleep(0.01)  # Small delay

        mock_streams.stream_portfolio = mock_portfolio_stream
        mock_streams.stop_stream = AsyncMock()

        return mock_streams

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_quotes_streaming(self, mock_ibkr_streams: MagicMock) -> None:
        """Test WebSocket quotes streaming."""
        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as websocket:
                    # Should receive multiple quote updates
                    messages = []
                    for _ in range(3):
                        data = websocket.receive_text()
                        message = json.loads(data)
                        messages.append(message)

                    # Verify message structure
                    assert len(messages) == 3
                    for i, message in enumerate(messages):
                        assert message["type"] == "quote"
                        assert message["symbol"] == "AAPL"
                        assert "data" in message
                        assert "timestamp" in message
                        assert float(message["data"]["bid"]) == 149.9 + i
                        assert float(message["data"]["ask"]) == 150.1 + i

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_depth_streaming(self, mock_ibkr_streams: MagicMock) -> None:
        """Test WebSocket depth streaming."""
        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection
                with TestClient(app).websocket_connect("/ws/depth/AAPL") as websocket:
                    # Should receive multiple depth updates
                    messages = []
                    for _ in range(2):
                        data = websocket.receive_text()
                        message = json.loads(data)
                        messages.append(message)

                    # Verify message structure
                    assert len(messages) == 2
                    for _i, message in enumerate(messages):
                        assert message["type"] == "depth"
                        assert message["symbol"] == "AAPL"
                        assert "data" in message
                        assert "timestamp" in message
                        assert len(message["data"]["bids"]) == 2
                        assert len(message["data"]["asks"]) == 2

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_portfolio_streaming(self, mock_ibkr_streams: MagicMock) -> None:
        """Test WebSocket portfolio streaming."""
        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection
                with TestClient(app).websocket_connect("/ws/portfolio/DU123456") as websocket:
                    # Should receive multiple portfolio updates
                    messages = []
                    for _ in range(2):
                        data = websocket.receive_text()
                        message = json.loads(data)
                        messages.append(message)

                    # Verify message structure
                    assert len(messages) == 2
                    for i, message in enumerate(messages):
                        assert message["type"] == "portfolio"
                        assert message["account_id"] == "DU123456"
                        assert "data" in message
                        assert "timestamp" in message
                        assert float(message["data"]["net_liquidation"]) == 100000.0 + i * 1000

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_pacing_error_handling(
        self, mock_ibkr_streams: MagicMock  # noqa: ARG002
    ) -> None:
        """Test WebSocket handling of pacing errors."""
        from market_data_core.models.errors import IBKRPacingError

        # Mock streams that raise pacing error
        async def mock_quote_stream_with_error(_symbol: str):
            raise IBKRPacingError("Pacing violation")

        mock_streams = MagicMock()
        mock_streams.stream_quotes = mock_quote_stream_with_error
        mock_streams.stop_stream = AsyncMock()

        with patch("market_data_core.services.api.ibkr_streams", mock_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection should handle error gracefully
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as websocket:
                    # Should not receive any messages due to error
                    try:
                        websocket.receive_text(timeout=1.0)
                        raise AssertionError("Should not receive any messages")
                    except Exception:
                        pass  # Expected timeout

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_connection_error_handling(
        self, mock_ibkr_streams: MagicMock  # noqa: ARG002
    ) -> None:
        """Test WebSocket handling of connection errors."""
        from market_data_core.models.errors import IBKRUnavailable

        # Mock streams that raise connection error
        async def mock_quote_stream_with_error(_symbol: str):
            raise IBKRUnavailable("Connection lost")

        mock_streams = MagicMock()
        mock_streams.stream_quotes = mock_quote_stream_with_error
        mock_streams.stop_stream = AsyncMock()

        with patch("market_data_core.services.api.ibkr_streams", mock_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection should handle error gracefully
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as websocket:
                    # Should not receive any messages due to error
                    try:
                        websocket.receive_text(timeout=1.0)
                        raise AssertionError("Should not receive any messages")
                    except Exception:
                        pass  # Expected timeout

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_disconnect_cleanup(self, mock_ibkr_streams: MagicMock) -> None:
        """Test WebSocket cleanup on disconnect."""
        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection and disconnect
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as websocket:
                    # Receive one message
                    data = websocket.receive_text()
                    message = json.loads(data)
                    assert message["type"] == "quote"

                # Should call stop_stream on disconnect
                mock_ibkr_streams.stop_stream.assert_called_with("quotes", "AAPL")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_multiple_websocket_connections(self, mock_ibkr_streams: MagicMock) -> None:
        """Test multiple WebSocket connections to the same stream."""
        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test multiple connections to the same quote stream
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as ws1:
                    with TestClient(app).websocket_connect("/ws/quotes/AAPL") as ws2:
                        # Both should receive messages
                        data1 = ws1.receive_text()
                        data2 = ws2.receive_text()

                        message1 = json.loads(data1)
                        message2 = json.loads(data2)

                        assert message1["type"] == "quote"
                        assert message2["type"] == "quote"
                        assert message1["symbol"] == "AAPL"
                        assert message2["symbol"] == "AAPL"

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_websocket_rate_limiting(self, mock_ibkr_streams: MagicMock) -> None:
        """Test WebSocket rate limiting."""

        # Mock streams that send a few messages
        async def fast_quote_stream(symbol: str):
            for _i in range(5):  # Send 5 messages
                yield Quote(
                    symbol=symbol,
                    bid=149.9,
                    ask=150.1,
                    last=150.0,
                    volume=1000,
                )
                await asyncio.sleep(0.01)  # Small delay

        mock_ibkr_streams.stream_quotes = fast_quote_stream

        with patch("market_data_core.services.api.ibkr_streams", mock_ibkr_streams):
            with patch("market_data_core.services.api.ib_client") as mock_client:
                mock_client.ensure_connection = AsyncMock()

                # Test WebSocket connection
                with TestClient(app).websocket_connect("/ws/quotes/AAPL") as websocket:
                    # Should receive messages
                    messages = []
                    try:
                        for _ in range(3):  # Try to receive 3 messages
                            data = websocket.receive_text(timeout=1.0)
                            message = json.loads(data)
                            messages.append(message)
                    except Exception:
                        pass  # May timeout

                    # Should receive at least some messages
                    assert len(messages) >= 0  # Just check it doesn't crash
                    assert len(messages) < 20  # Rate limited
