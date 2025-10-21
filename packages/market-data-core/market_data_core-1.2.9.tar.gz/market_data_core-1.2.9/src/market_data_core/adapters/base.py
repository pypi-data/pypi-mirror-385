"""DEPRECATED: Use market_data_core.protocols.MarketDataProvider instead.

This module is deprecated and will be removed in v2.0.
Migrate to the new protocol-based architecture.
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterable

from ..schemas.models import PriceBar

warnings.warn(
    "market_data_core.adapters is deprecated. "
    "Use market_data_core.protocols.MarketDataProvider instead. "
    "Provider implementations should be in separate packages (e.g., market_data_ibkr).",
    DeprecationWarning,
    stacklevel=2
)


# ISP: keep interfaces small (price data for now).
class PriceDataProvider(ABC):
    """DEPRECATED: Use market_data_core.protocols.MarketDataProvider instead."""
    
    @abstractmethod
    async def get_price_bars(
        self, symbol: str, interval: str = "1d", limit: int = 100
    ) -> Iterable[PriceBar]:
        """Return recent bars for a symbol."""
        raise NotImplementedError
