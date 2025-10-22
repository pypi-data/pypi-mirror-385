"""IBKR interval and parameter mapping utilities."""

from collections.abc import Callable

# Interval mapping from clean API to IBKR format
INTERVAL_MAP = {
    "1s": "1 secs",
    "5s": "5 secs",
    "1m": "1 min",
    "5m": "5 mins",
    "15m": "15 mins",
    "30m": "30 mins",
    "1h": "1 hour",
    "1d": "1 day",
    "1w": "1 week",
    "1M": "1 month",
}

# WhatToShow mapping for market data
WHAT_TO_SHOW_MAP = {
    "TRADES": "TRADES",
    "MIDPOINT": "MIDPOINT",
    "BID": "BID",
    "ASK": "ASK",
}

# Valid intervals for validation
VALID_INTERVALS = set(INTERVAL_MAP.keys())

# Valid whatToShow values for validation
VALID_WHAT_TO_SHOW = set(WHAT_TO_SHOW_MAP.keys())

# Default values
DEFAULT_INTERVAL = "1d"
DEFAULT_WHAT_TO_SHOW = "TRADES"


def map_interval(interval: str) -> str:
    """
    Map clean interval format to IBKR bar size setting.

    Args:
        interval: Clean interval (e.g., "1m", "5m", "1h", "1d")

    Returns:
        IBKR bar size setting (e.g., "1 min", "5 mins", "1 hour", "1 day")

    Raises:
        ValueError: If interval is not supported
    """
    if interval not in INTERVAL_MAP:
        raise ValueError(f"Unsupported interval: {interval}. Supported: {sorted(VALID_INTERVALS)}")

    return INTERVAL_MAP[interval]


def map_what_to_show(what: str) -> str:
    """
    Map whatToShow parameter to IBKR format.

    Args:
        what: What to show (e.g., "TRADES", "MIDPOINT", "BID", "ASK")

    Returns:
        IBKR whatToShow value

    Raises:
        ValueError: If whatToShow is not supported
    """
    if what not in WHAT_TO_SHOW_MAP:
        raise ValueError(f"Unsupported whatToShow: {what}. Supported: {sorted(VALID_WHAT_TO_SHOW)}")

    return WHAT_TO_SHOW_MAP[what]


def validate_interval(interval: str) -> str:
    """
    Validate and normalize interval parameter.

    Args:
        interval: Input interval string

    Returns:
        Normalized interval string

    Raises:
        ValueError: If interval is invalid
    """
    if not interval:
        return DEFAULT_INTERVAL

    # Handle special case for "1M" (month) - keep uppercase
    if interval == "1M":
        return "1M"

    interval = interval.lower()
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval: {interval}. Supported: {sorted(VALID_INTERVALS)}")

    return interval


def validate_what_to_show(what: str) -> str:
    """
    Validate and normalize whatToShow parameter.

    Args:
        what: Input whatToShow string

    Returns:
        Normalized whatToShow string

    Raises:
        ValueError: If whatToShow is invalid
    """
    if not what:
        return DEFAULT_WHAT_TO_SHOW

    what = what.upper()
    if what not in VALID_WHAT_TO_SHOW:
        raise ValueError(f"Invalid whatToShow: {what}. Supported: {sorted(VALID_WHAT_TO_SHOW)}")

    return what


def get_duration_string(interval: str, limit: int) -> str:
    """
    Calculate IBKR duration string based on interval and limit.

    Args:
        interval: Clean interval string
        limit: Number of bars to request

    Returns:
        IBKR duration string (e.g., "1 D", "5 D", "1 W")
    """
    # Map intervals to duration calculation
    duration_map: dict[str, Callable[[int], str]] = {
        "1s": lambda x: f"{x * 5} S",  # 5 seconds per bar
        "5s": lambda x: f"{x * 5} S",  # 5 seconds per bar
        "1m": lambda x: f"{x * 5} D",  # 5 minutes per bar, request in days
        "5m": lambda x: f"{x * 5} D",  # 25 minutes per bar
        "15m": lambda x: f"{x * 5} D",  # 1.25 hours per bar
        "30m": lambda x: f"{x * 5} D",  # 2.5 hours per bar
        "1h": lambda x: f"{x * 5} D",  # 5 hours per bar
        "1d": lambda x: f"{x} D",  # 1 day per bar
        "1w": lambda x: f"{x} W",  # 1 week per bar
        "1M": lambda x: f"{x} M",  # 1 month per bar
    }

    if interval not in duration_map:
        # Default to days for unknown intervals
        return f"{limit} D"

    return duration_map[interval](limit)
