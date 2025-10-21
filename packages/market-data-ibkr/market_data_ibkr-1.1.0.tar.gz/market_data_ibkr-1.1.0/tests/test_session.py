"""Test session management."""

import pytest
from unittest.mock import AsyncMock, patch
from market_data_core import ConnectionFailed

from market_data_ibkr import IBKRSettings, IBKRSessionManager


@pytest.mark.asyncio
async def test_connect_success(mock_ib):
    """Test successful connection."""
    settings = IBKRSettings(host="127.0.0.1", port=4002, client_id=17)
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        manager = IBKRSessionManager(settings)
        manager.ib = mock_ib
        
        await manager.connect()
        
        assert mock_ib.connectAsync.called
        assert mock_ib.reqMarketDataType.called
        assert manager.is_connected()


@pytest.mark.asyncio
async def test_connect_failure(mock_ib):
    """Test connection failure."""
    settings = IBKRSettings()
    mock_ib.connectAsync.side_effect = Exception("Connection refused")
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        manager = IBKRSessionManager(settings)
        manager.ib = mock_ib
        
        with pytest.raises(ConnectionFailed):
            await manager.connect()


@pytest.mark.asyncio
async def test_disconnect(mock_ib):
    """Test disconnection."""
    settings = IBKRSettings()
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        manager = IBKRSessionManager(settings)
        manager.ib = mock_ib
        manager._connected = True
        
        await manager.disconnect()
        
        assert mock_ib.disconnect.called


@pytest.mark.asyncio
async def test_ensure_connected_when_connected(mock_ib):
    """Test ensure_connected when already connected."""
    settings = IBKRSettings()
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        manager = IBKRSessionManager(settings)
        manager.ib = mock_ib
        manager._connected = True
        
        await manager.ensure_connected()
        
        # Should not try to reconnect
        assert mock_ib.connectAsync.call_count == 0


def test_get_connection_stats(mock_ib):
    """Test getting connection statistics."""
    settings = IBKRSettings(host="192.168.1.1", port=7497, client_id=42)
    
    with patch('market_data_ibkr.session.IB', return_value=mock_ib):
        manager = IBKRSessionManager(settings)
        manager.ib = mock_ib
        manager._connected = True
        
        stats = manager.get_connection_stats()
        
        assert stats["host"] == "192.168.1.1"
        assert stats["port"] == 7497
        assert stats["client_id"] == 42
        assert stats["connected"] is True

