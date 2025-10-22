import asyncio
import os
from datetime import UTC, datetime
from typing import Any

from ib_async import IB
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..schemas.models import Health


class IBKRConnectionManager:
    """
    Singleton IBKR connection manager with auto-reconnection, health stats,
    and subscription registry to avoid duplicate subscriptions.
    """

    _instance: "IBKRConnectionManager | None" = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "IBKRConnectionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.ib = IB()
        self._connected = False
        self._last_connect_ts: datetime | None = None
        self._reconnects_total = 0
        self._subscriptions: dict[str, Any] = {}
        self._subscriptions_active = 0
        self._errors_total = 0

        # Environment configuration
        self.host = os.getenv("IB_HOST", "127.0.0.1")
        self.port = int(os.getenv("IB_PORT", "4001"))
        self.client_id = int(os.getenv("IB_CLIENT_ID", "7"))
        self.market_data_type = int(os.getenv("MARKET_DATA_TYPE", "1"))

        # Prometheus metrics - simplified for testing
        self.metrics: dict[str, Any] = {}

    async def connect(self) -> None:
        """Establish connection to IBKR with retry logic."""
        async with self._lock:
            if self._connected:
                return

            try:
                await self._connect_with_retry()
                self._connected = True
                self._last_connect_ts = datetime.now(UTC)
                # self.metrics["ib_connected"].set(1)
                logger.info(f"Connected to IBKR at {self.host}:{self.port}")
            except Exception as e:
                self._connected = False
                self._errors_total += 1
                # self.metrics["ib_connected"].set(0)
                # self.metrics["ib_errors_total"].inc()
                logger.error(f"Failed to connect to IBKR: {e}")
                raise

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _connect_with_retry(self) -> None:
        """Internal connection method with retry logic."""
        # start_time = datetime.now()

        try:
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)

            # Set market data type based on environment
            await self.ib.reqMarketDataType(self.market_data_type)

            # Record connection duration
            # duration = (datetime.now() - start_time).total_seconds()
            # self.metrics["ib_connection_duration"].observe(duration)

        except Exception as e:
            self._reconnects_total += 1
            # self.metrics["ib_reconnects_total"].inc()
            logger.warning(f"Connection attempt failed, retrying: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from IBKR and cleanup subscriptions."""
        async with self._lock:
            if self._connected:
                try:
                    # Cancel all active subscriptions
                    for sub_key in list(self._subscriptions.keys()):
                        await self._cancel_subscription(sub_key)

                    self.ib.disconnect()
                    self._connected = False
                    self._subscriptions.clear()
                    self._subscriptions_active = 0
                    # self.metrics["ib_connected"].set(0)
                    # self.metrics["ib_subscriptions_active"].set(0)
                    logger.info("Disconnected from IBKR")
                except Exception as e:
                    logger.error(f"Error during disconnect: {e}")

    async def ensure_connection(self) -> None:
        """Ensure connection is active, reconnect if needed."""
        if not self._connected or not self.ib.isConnected():
            await self.connect()

    def is_connected(self) -> bool:
        """Check if connected to IBKR."""
        return self._connected and self.ib.isConnected()

    async def add_subscription(self, key: str, subscription: Any) -> None:
        """Add a subscription to the registry."""
        await self.ensure_connection()
        self._subscriptions[key] = subscription
        self._subscriptions_active = len(self._subscriptions)
        # self.metrics["ib_subscriptions_active"].set(self._subscriptions_active)
        logger.debug(f"Added subscription: {key}")

    async def remove_subscription(self, key: str) -> None:
        """Remove a subscription from the registry."""
        if key in self._subscriptions:
            await self._cancel_subscription(key)
            del self._subscriptions[key]
            self._subscriptions_active = len(self._subscriptions)
            # self.metrics["ib_subscriptions_active"].set(self._subscriptions_active)
            logger.debug(f"Removed subscription: {key}")

    async def _cancel_subscription(self, key: str) -> None:
        """Cancel a specific subscription."""
        try:
            subscription = self._subscriptions.get(key)
            if subscription:
                # Cancel the subscription based on its type
                if hasattr(subscription, "cancel"):
                    subscription.cancel()
                elif hasattr(subscription, "close"):
                    subscription.close()
                logger.debug(f"Cancelled subscription: {key}")
        except Exception as e:
            logger.warning(f"Error cancelling subscription {key}: {e}")

    async def rehydrate_subscriptions(self) -> None:
        """Re-issue all subscriptions after reconnection."""
        if not self._subscriptions:
            return

        logger.info(f"Rehydrating {len(self._subscriptions)} subscriptions")
        # Note: In a real implementation, you'd need to store subscription details
        # and re-create them. For now, we'll just log the action.
        for key in self._subscriptions:
            logger.debug(f"Rehydrating subscription: {key}")

    def get_health_stats(self) -> Health:
        """Get health statistics for the connection."""
        return Health(
            status="ok" if self._connected else "disconnected",
            version="0.1.0",
            ibkr_connected=self._connected,
            gateway_type="TWS" if self.port == 7497 else "Gateway",
            gateway_port=self.port,
            last_connect_ts=self._last_connect_ts,
            reconnects_total=self._reconnects_total,
            subscriptions_active=self._subscriptions_active,
            errors_total=self._errors_total,
        )

    async def __aenter__(self) -> "IBKRConnectionManager":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()


# Global singleton instance
connection_manager = IBKRConnectionManager()
