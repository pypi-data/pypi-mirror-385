"""Normalized Pydantic models for market data core.

DEPRECATED: This module is deprecated. Import from market_data_core.models directly.

For backward compatibility, this re-exports everything from the new models.py structure.
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "Importing from market_data_core.models.* is deprecated. "
    "Import from market_data_core directly instead. "
    "Example: from market_data_core import Quote, Bar",
    DeprecationWarning,
    stacklevel=2
)

# Import from parent package (the new models.py file is at ..models)
# But we need to avoid circular imports, so we'll keep the old imports working
# by importing from the individual files

from .contracts import Contract
from .health import Health
from .market_data import MarketDepth, PriceBar, Quote
from .options import OptionChain, OptionContract
from .portfolio import AccountSummary, PortfolioUpdate, Position
from .registry import (
    EnforcementMode,
    SchemaDeprecatedEvent,
    SchemaDriftEvent,
    SchemaPublishedEvent,
    SchemaValidationResult,
)

__all__ = [
    "Contract",
    "PriceBar",
    "Quote",
    "MarketDepth",
    "OptionContract",
    "OptionChain",
    "Position",
    "AccountSummary",
    "PortfolioUpdate",
    "Health",
    # Registry & Schema Lifecycle (Phase 11.1)
    "EnforcementMode",
    "SchemaPublishedEvent",
    "SchemaDeprecatedEvent",
    "SchemaDriftEvent",
    "SchemaValidationResult",
]
