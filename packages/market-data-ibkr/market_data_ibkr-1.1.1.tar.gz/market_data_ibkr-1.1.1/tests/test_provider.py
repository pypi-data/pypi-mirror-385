"""Test IBKRProvider implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from market_data_core import Instrument
from market_data_ibkr import IBKRProvider, IBKRSettings


@pytest.mark.asyncio
async def test_provider_context_manager(mock_ib):
    """Test provider as async context manager."""
    settings = IBKRSettings()
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        async with IBKRProvider(settings) as provider:
            assert provider.session.ib == mock_ib
        
        # Should disconnect on exit
        assert mock_ib.disconnect.called


@pytest.mark.asyncio
async def test_close(mock_ib):
    """Test provider close."""
    settings = IBKRSettings()
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        provider = IBKRProvider(settings)
        provider.session.ib = mock_ib
        provider.session._connected = True
        
        await provider.close()
        
        assert mock_ib.disconnect.called


def test_instrument_to_contract_caching():
    """Test that contracts are cached."""
    settings = IBKRSettings()
    provider = IBKRProvider(settings)
    
    instrument = Instrument(symbol="AAPL", exchange="SMART", currency="USD")
    
    # First call
    contract1 = provider._instrument_to_contract(instrument)
    
    # Second call should return cached contract
    contract2 = provider._instrument_to_contract(instrument)
    
    assert contract1 is contract2  # Same object reference


def test_instrument_to_contract_stock():
    """Test converting instrument to stock contract."""
    settings = IBKRSettings()
    provider = IBKRProvider(settings)
    
    instrument = Instrument(symbol="AAPL", exchange="NASDAQ", currency="USD")
    contract = provider._instrument_to_contract(instrument)
    
    assert contract.symbol == "AAPL"
    assert contract.exchange == "NASDAQ"
    assert contract.currency == "USD"


def test_instrument_to_contract_defaults():
    """Test contract creation with defaults."""
    settings = IBKRSettings()
    provider = IBKRProvider(settings)
    
    instrument = Instrument(symbol="MSFT")  # No exchange/currency specified
    contract = provider._instrument_to_contract(instrument)
    
    assert contract.symbol == "MSFT"
    assert contract.exchange == "SMART"  # Default
    assert contract.currency == "USD"  # Default


@pytest.mark.asyncio
async def test_stream_trades_not_implemented():
    """Test that stream_trades raises NotImplementedError."""
    settings = IBKRSettings()
    provider = IBKRProvider(settings)
    
    with pytest.raises(NotImplementedError):
        async for _ in provider.stream_trades([]):
            pass


@pytest.mark.asyncio
async def test_stream_options_not_implemented():
    """Test that stream_options raises NotImplementedError."""
    settings = IBKRSettings()
    provider = IBKRProvider(settings)
    
    instrument = Instrument(symbol="AAPL")
    
    with pytest.raises(NotImplementedError):
        async for _ in provider.stream_options(instrument):
            pass

