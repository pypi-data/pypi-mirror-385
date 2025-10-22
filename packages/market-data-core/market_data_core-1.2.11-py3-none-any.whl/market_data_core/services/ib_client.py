"""IBKR Client with auto-reconnect and subscription registry."""

import asyncio
import os
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from ib_async import IB
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.health import Health
from ..utils.observability import metrics


class IBClient:
    """Singleton IBKR client with auto-reconnect and subscription management."""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "IBClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "initialized"):
            self.ib = IB()
            self._connected = False
            self._last_connect_ts: datetime | None = None
            self._reconnects_total = 0
            self._errors_total = 0
            self._subscriptions: dict[str, set[Any]] = defaultdict(set)
            self._subscriptions_active = 0

            # Configuration from environment
            self.host = os.getenv("IB_HOST", "127.0.0.1")
            self.port = int(os.getenv("IB_PORT", "4001"))
            self.client_id = int(os.getenv("IB_CLIENT_ID", "7"))
            self.market_data_type = int(os.getenv("MARKET_DATA_TYPE", "1"))

            # Prometheus metrics
            self.metrics: dict[str, Any] = {}
            self.initialized = True

    async def connect(self, streams_adapter: Any = None) -> None:
        """Establish connection to IBKR with retry logic."""
        async with self._lock:
            if self._connected:
                return

            try:
                await self._connect_with_retry()
                self._connected = True
                self._last_connect_ts = datetime.now(UTC)
                logger.info(f"Connected to IBKR at {self.host}:{self.port}")

                # Update metrics
                metrics.ib_connected.set(1)

                # Set market data type
                await self.ib.reqMarketDataType(self.market_data_type)
                logger.info(f"Set market data type to {self.market_data_type}")

                # Rehydrate subscriptions if we have a streams adapter
                if streams_adapter:
                    await self.rehydrate_subscriptions(streams_adapter)

            except Exception as e:
                self._errors_total += 1
                metrics.ib_errors.labels(error_type="connection").inc()
                logger.error(f"Failed to connect to IBKR: {e}")
                raise

    async def disconnect(self) -> None:
        """Disconnect from IBKR."""
        async with self._lock:
            if self._connected:
                self.ib.disconnect()
                self._connected = False
                metrics.ib_connected.set(0)
                logger.info("Disconnected from IBKR")

    async def ensure_connection(self) -> None:
        """Ensure connection is active, reconnect if needed."""
        if not self._connected or not self.ib.isConnected():
            await self.connect()

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _connect_with_retry(self) -> None:
        """Internal connection method with retry logic."""
        try:
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
            await self.ib.reqMarketDataType(self.market_data_type)
        except Exception as e:
            self._reconnects_total += 1
            metrics.ib_reconnects.inc()
            metrics.ib_errors.labels(error_type="reconnect").inc()
            logger.warning(f"Connection attempt failed, retrying: {e}")
            raise

    def get_health_stats(self) -> Health:
        """Get current health statistics."""
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

    def register_subscription(self, subscription_type: str, subscription_id: str) -> None:
        """Register a subscription for rehydration after reconnect."""
        self._subscriptions[subscription_type].add(subscription_id)
        self._subscriptions_active = sum(len(subs) for subs in self._subscriptions.values())
        metrics.ib_subscriptions.labels(type=subscription_type).set(
            len(self._subscriptions[subscription_type])
        )
        logger.debug(f"Registered {subscription_type} subscription: {subscription_id}")

    def unregister_subscription(self, subscription_type: str, subscription_id: str) -> None:
        """Unregister a subscription."""
        self._subscriptions[subscription_type].discard(subscription_id)
        self._subscriptions_active = sum(len(subs) for subs in self._subscriptions.values())
        metrics.ib_subscriptions.labels(type=subscription_type).set(
            len(self._subscriptions[subscription_type])
        )
        logger.debug(f"Unregistered {subscription_type} subscription: {subscription_id}")

    async def rehydrate_subscriptions(self, streams_adapter: Any = None) -> None:
        """Rehydrate subscriptions after reconnect."""
        if not self._connected:
            return

        logger.info(f"Rehydrating {self._subscriptions_active} subscriptions")

        # Rehydrate based on subscription types
        for sub_type, subs in self._subscriptions.items():
            if subs:
                logger.info(f"Rehydrating {len(subs)} {sub_type} subscriptions")

                # If we have a streams adapter, rehydrate active streams
                if streams_adapter and hasattr(streams_adapter, "rehydrate_streams"):
                    await streams_adapter.rehydrate_streams(sub_type, list(subs))

    @property
    def is_connected(self) -> bool:
        """Check if connected to IBKR."""
        return self._connected and self.ib.isConnected()

    async def is_connected_async(self) -> bool:
        """Async version of is_connected."""
        return self._connected and self.ib.isConnected()

    def get_last_heartbeat(self) -> datetime | None:
        """Get the timestamp of the last heartbeat."""
        return self._last_connect_ts

    def get_registry_status(self) -> dict[str, Any]:
        """Get the status of the subscription registry."""
        return {
            "rehydrated": self._connected,
            "total_subscriptions": sum(len(subs) for subs in self._subscriptions.values()),
            "subscription_types": list(self._subscriptions.keys()),
        }

    def get_active_subscriptions(self) -> dict[str, set[Any]]:
        """Get active subscriptions by type."""
        return dict(self._subscriptions)


# Global singleton instance
ib_client = IBClient()
