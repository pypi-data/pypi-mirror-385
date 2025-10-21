"""Test IBKR settings."""

import pytest
from market_data_ibkr import IBKRSettings
from pydantic import ValidationError


def test_default_settings():
    """Test default settings values."""
    settings = IBKRSettings()
    
    assert settings.host == "127.0.0.1"
    assert settings.port == 4002
    assert settings.client_id == 17
    assert settings.market_data_type == 1
    assert settings.reconnect_enabled is True
    assert settings.hist_pacing_window_sec == 600


def test_custom_settings():
    """Test custom settings."""
    settings = IBKRSettings(
        host="192.168.1.100",
        port=7497,
        client_id=42,
        market_data_type=3,
    )
    
    assert settings.host == "192.168.1.100"
    assert settings.port == 7497
    assert settings.client_id == 42
    assert settings.market_data_type == 3


def test_settings_validation_invalid_port():
    """Test settings validation for invalid port."""
    with pytest.raises(ValidationError):
        IBKRSettings(port=99999)  # Port too high


def test_settings_validation_invalid_client_id():
    """Test settings validation for invalid client ID."""
    with pytest.raises(ValidationError):
        IBKRSettings(client_id=-1)  # Negative client ID


def test_settings_validation_invalid_market_data_type():
    """Test settings validation for invalid market data type."""
    with pytest.raises(ValidationError):
        IBKRSettings(market_data_type=5)  # Out of range


def test_settings_forbid_extra_fields():
    """Test that extra fields are forbidden."""
    with pytest.raises(ValidationError):
        IBKRSettings(invalid_field="value")

