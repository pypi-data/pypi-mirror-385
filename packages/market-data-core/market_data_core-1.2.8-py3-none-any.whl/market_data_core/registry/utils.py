"""Utility functions for registry enforcement and drift detection."""

from __future__ import annotations

import os

from market_data_core.models.registry import EnforcementMode


def get_enforcement_mode() -> EnforcementMode:
    """Get the current enforcement mode from environment.
    
    Reads from REGISTRY_ENFORCEMENT environment variable.
    Defaults to 'warn' if not set or invalid.
    
    Returns:
        EnforcementMode enum value
        
    Example:
        >>> import os
        >>> os.environ['REGISTRY_ENFORCEMENT'] = 'strict'
        >>> mode = get_enforcement_mode()
        >>> assert mode == EnforcementMode.strict
    """
    mode_str = os.getenv("REGISTRY_ENFORCEMENT", "warn").lower()
    try:
        return EnforcementMode(mode_str)
    except ValueError:
        # Invalid mode, default to warn
        return EnforcementMode.warn


def should_enforce_strict() -> bool:
    """Check if strict enforcement is enabled.
    
    Returns:
        True if REGISTRY_ENFORCEMENT=strict, False otherwise
        
    Example:
        >>> if should_enforce_strict():
        ...     raise SchemaValidationError("Invalid payload")
        ... else:
        ...     logger.warning("Invalid payload (warn mode)")
    """
    return get_enforcement_mode() == EnforcementMode.strict


def should_log_warning() -> bool:
    """Check if warning mode is enabled.
    
    Returns:
        True if REGISTRY_ENFORCEMENT=warn (or default), False if strict
        
    Example:
        >>> if should_log_warning():
        ...     logger.warning("Schema validation failed")
    """
    return get_enforcement_mode() == EnforcementMode.warn

