"""DEPRECATED: Services module contains application-layer code.

Application orchestration should be in separate application packages or examples.

Core should only contain contracts (protocols, models, errors, settings).
"""

import warnings

warnings.warn(
    "market_data_core.services contains application code that doesn't belong in Core. "
    "Core should only contain contracts. Move application logic to your own service layer.",
    DeprecationWarning,
    stacklevel=2
)

