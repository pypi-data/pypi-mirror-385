"""DEPRECATED: Schemas module is deprecated.

Import models directly from market_data_core instead:
    from market_data_core import Quote, Bar, OptionSnapshot
"""

import warnings

warnings.warn(
    "market_data_core.schemas is deprecated. "
    "Import models directly from market_data_core instead: from market_data_core import Quote, Bar",
    DeprecationWarning,
    stacklevel=2
)

