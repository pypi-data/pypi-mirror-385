"""Tests for IBKR mapping utilities."""

import pytest

from market_data_core.utils.ibkr_mapping import (
    INTERVAL_MAP,
    VALID_INTERVALS,
    VALID_WHAT_TO_SHOW,
    get_duration_string,
    map_interval,
    map_what_to_show,
    validate_interval,
    validate_what_to_show,
)


class TestIBKRMapping:
    """Test cases for IBKR mapping utilities."""

    def test_map_interval_valid(self) -> None:
        """Test valid interval mapping."""
        assert map_interval("1s") == "1 secs"
        assert map_interval("5s") == "5 secs"
        assert map_interval("1m") == "1 min"
        assert map_interval("5m") == "5 mins"
        assert map_interval("15m") == "15 mins"
        assert map_interval("1h") == "1 hour"
        assert map_interval("1d") == "1 day"
        assert map_interval("1w") == "1 week"
        assert map_interval("1M") == "1 month"

    def test_map_interval_invalid(self) -> None:
        """Test invalid interval mapping."""
        with pytest.raises(ValueError, match="Unsupported interval"):
            map_interval("invalid")

        with pytest.raises(ValueError, match="Unsupported interval"):
            map_interval("2h")

    def test_map_what_to_show_valid(self) -> None:
        """Test valid whatToShow mapping."""
        assert map_what_to_show("TRADES") == "TRADES"
        assert map_what_to_show("MIDPOINT") == "MIDPOINT"
        assert map_what_to_show("BID") == "BID"
        assert map_what_to_show("ASK") == "ASK"

    def test_map_what_to_show_invalid(self) -> None:
        """Test invalid whatToShow mapping."""
        with pytest.raises(ValueError, match="Unsupported whatToShow"):
            map_what_to_show("INVALID")

    def test_validate_interval_valid(self) -> None:
        """Test valid interval validation."""
        assert validate_interval("1m") == "1m"
        assert validate_interval("5m") == "5m"
        assert validate_interval("1h") == "1h"
        assert validate_interval("1d") == "1d"
        assert validate_interval("") == "1d"  # Default
        assert validate_interval("1M") == "1M"

    def test_validate_interval_invalid(self) -> None:
        """Test invalid interval validation."""
        with pytest.raises(ValueError, match="Invalid interval"):
            validate_interval("invalid")

        with pytest.raises(ValueError, match="Invalid interval"):
            validate_interval("2h")

    def test_validate_what_to_show_valid(self) -> None:
        """Test valid whatToShow validation."""
        assert validate_what_to_show("TRADES") == "TRADES"
        assert validate_what_to_show("trades") == "TRADES"  # Case insensitive
        assert validate_what_to_show("MIDPOINT") == "MIDPOINT"
        assert validate_what_to_show("midpoint") == "MIDPOINT"
        assert validate_what_to_show("") == "TRADES"  # Default

    def test_validate_what_to_show_invalid(self) -> None:
        """Test invalid whatToShow validation."""
        with pytest.raises(ValueError, match="Invalid whatToShow"):
            validate_what_to_show("invalid")

    def test_get_duration_string(self) -> None:
        """Test duration string calculation."""
        # Test different intervals
        assert get_duration_string("1s", 10) == "50 S"
        assert get_duration_string("5s", 10) == "50 S"
        assert get_duration_string("1m", 10) == "50 D"
        assert get_duration_string("5m", 10) == "50 D"
        assert get_duration_string("1h", 10) == "50 D"
        assert get_duration_string("1d", 10) == "10 D"
        assert get_duration_string("1w", 5) == "5 W"
        assert get_duration_string("1M", 3) == "3 M"

        # Test unknown interval (should default to days)
        assert get_duration_string("unknown", 5) == "5 D"

    def test_interval_map_completeness(self) -> None:
        """Test that all valid intervals are in the map."""
        for interval in VALID_INTERVALS:
            assert interval in INTERVAL_MAP
            assert map_interval(interval) is not None

    def test_what_to_show_map_completeness(self) -> None:
        """Test that all valid whatToShow values are in the map."""
        for what in VALID_WHAT_TO_SHOW:
            assert what in VALID_WHAT_TO_SHOW
            assert map_what_to_show(what) is not None

    def test_constants_consistency(self) -> None:
        """Test that constants are consistent."""
        # All intervals in map should be valid
        for interval in INTERVAL_MAP:
            assert interval in VALID_INTERVALS

        # All whatToShow values should be valid
        for what in VALID_WHAT_TO_SHOW:
            assert what in VALID_WHAT_TO_SHOW
