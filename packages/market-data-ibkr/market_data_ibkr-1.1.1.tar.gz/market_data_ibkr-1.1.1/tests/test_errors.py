"""Test error mapping."""

import pytest
from market_data_core import (
    ConnectionFailed,
    FarmTransient,
    InvalidInstrument,
    PacingViolation,
    PermissionsMissing,
    RetryableProviderError,
)
from market_data_ibkr.errors import map_ibkr_error, handle_ib_error


def test_error_code_2104():
    """Test informational message (not an error)."""
    result = map_ibkr_error(2104, "Market data farm connection is OK")
    assert result is None  # Not an error


def test_error_code_420():
    """Test pacing violation."""
    result = map_ibkr_error(420, "Pacing violation")
    assert isinstance(result, PacingViolation)
    assert "Pacing violation" in str(result)


def test_error_code_200():
    """Test invalid instrument."""
    result = map_ibkr_error(200, "No security definition found")
    assert isinstance(result, InvalidInstrument)


def test_error_code_354():
    """Test permissions missing."""
    result = map_ibkr_error(354, "Requested market data is not subscribed")
    assert isinstance(result, PermissionsMissing)


def test_error_code_504():
    """Test connection error."""
    result = map_ibkr_error(504, "Not connected")
    assert isinstance(result, ConnectionFailed)


def test_error_code_1100():
    """Test connection lost."""
    result = map_ibkr_error(1100, "Connectivity between IB and TWS has been lost")
    assert isinstance(result, ConnectionFailed)


def test_error_code_2110():
    """Test farm transient."""
    result = map_ibkr_error(2110, "Connectivity between TWS and server is broken")
    assert isinstance(result, FarmTransient)


def test_error_162_permissions():
    """Test error 162 with permissions message."""
    result = map_ibkr_error(162, "No market data permissions for AAPL")
    assert isinstance(result, PermissionsMissing)


def test_error_162_pacing():
    """Test error 162 with pacing message."""
    result = map_ibkr_error(162, "Request exceeds max duration")
    assert isinstance(result, PacingViolation)


def test_error_162_invalid():
    """Test error 162 with invalid instrument message."""
    result = map_ibkr_error(162, "Symbol not found in database")
    assert isinstance(result, InvalidInstrument)


def test_error_162_ambiguous():
    """Test error 162 with ambiguous message."""
    result = map_ibkr_error(162, "Some random error message")
    assert isinstance(result, RetryableProviderError)


def test_unknown_error_code():
    """Test unknown error code defaults to retryable."""
    result = map_ibkr_error(9999, "Unknown error")
    assert isinstance(result, RetryableProviderError)


def test_handle_ib_error_with_code():
    """Test handling exception with code attribute."""
    class MockError(Exception):
        def __init__(self, code, message):
            self.code = code
            super().__init__(message)
    
    exc = MockError(420, "Pacing violation")
    result = handle_ib_error(exc)
    assert isinstance(result, PacingViolation)


def test_handle_ib_error_without_code():
    """Test handling exception without code attribute."""
    exc = Exception("Generic error")
    result = handle_ib_error(exc)
    assert isinstance(result, RetryableProviderError)

