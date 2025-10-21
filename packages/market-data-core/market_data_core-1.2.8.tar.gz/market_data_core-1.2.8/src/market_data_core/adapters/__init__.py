"""DEPRECATED: Adapters module is deprecated.

Provider implementations have moved to separate packages:
- IBKR: market_data_ibkr package
- Synthetic: market_data_pipeline package

Use market_data_core.protocols.MarketDataProvider as the interface.
"""

import warnings

warnings.warn(
    "market_data_core.adapters is deprecated and will be removed in v2.0. "
    "Provider implementations are now in separate packages (market_data_ibkr, etc.). "
    "Use market_data_core.protocols.MarketDataProvider as the interface.",
    DeprecationWarning,
    stacklevel=2
)

from .base import PriceDataProvider
from .ibkr_adapter import IBKRPriceAdapter

__all__ = [
    "PriceDataProvider",
    "IBKRPriceAdapter",
]

