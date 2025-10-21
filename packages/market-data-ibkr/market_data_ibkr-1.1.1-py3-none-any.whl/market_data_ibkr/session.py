"""IBKR connection session management."""

import asyncio
from typing import Any

from ib_insync import IB
from loguru import logger
from market_data_core import ConnectionFailed

from .settings import IBKRSettings


class IBKRSessionManager:
    """Manages IBKR connection lifecycle with auto-reconnection.
    
    Responsibilities:
    - Connect to IBKR Gateway/TWS
    - Handle reconnection with exponential backoff
    - Track connection state
    - Clean shutdown
    """
    
    def __init__(self, settings: IBKRSettings):
        """Initialize session manager.
        
        Args:
            settings: IBKR connection settings
        """
        self.settings = settings
        self.ib = IB()
        self._connected = False
        self._reconnect_attempts = 0
        self._connection_lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Connect to IBKR.
        
        Raises:
            ConnectionFailed: If connection fails
        """
        async with self._connection_lock:
            if self._connected and self.ib.isConnected():
                logger.debug("Already connected to IBKR")
                return
            
            try:
                logger.info(
                    f"Connecting to IBKR at {self.settings.host}:{self.settings.port} "
                    f"(client_id={self.settings.client_id})"
                )
                
                await self.ib.connectAsync(
                    host=self.settings.host,
                    port=self.settings.port,
                    clientId=self.settings.client_id,
                    timeout=self.settings.read_timeout_sec,
                )
                
                # Set market data type
                self.ib.reqMarketDataType(self.settings.market_data_type)
                
                self._connected = True
                self._reconnect_attempts = 0
                
                logger.info(
                    f"Connected to IBKR successfully (market_data_type={self.settings.market_data_type})"
                )
                
            except Exception as e:
                self._connected = False
                logger.error(f"Failed to connect to IBKR: {e}")
                raise ConnectionFailed(f"IBKR connection failed: {e}") from e
    
    async def ensure_connected(self) -> None:
        """Ensure connection is active, reconnect if needed.
        
        Raises:
            ConnectionFailed: If connection cannot be established
        """
        if not self.is_connected():
            if self.settings.reconnect_enabled:
                await self.reconnect()
            else:
                await self.connect()
    
    async def reconnect(self) -> None:
        """Reconnect with exponential backoff.
        
        Raises:
            ConnectionFailed: If max reconnection attempts exceeded
        """
        if (
            self.settings.max_reconnect_attempts > 0 
            and self._reconnect_attempts >= self.settings.max_reconnect_attempts
        ):
            raise ConnectionFailed(
                f"Max reconnection attempts ({self.settings.max_reconnect_attempts}) exceeded"
            )
        
        # Calculate backoff
        backoff_ms = min(
            self.settings.reconnect_backoff_ms * (2 ** self._reconnect_attempts),
            self.settings.reconnect_backoff_max_ms
        )
        backoff_sec = backoff_ms / 1000.0
        
        logger.warning(
            f"Reconnecting to IBKR (attempt {self._reconnect_attempts + 1}), "
            f"waiting {backoff_sec:.2f}s"
        )
        
        await asyncio.sleep(backoff_sec)
        self._reconnect_attempts += 1
        
        try:
            await self.disconnect()  # Clean disconnect first
        except Exception:
            pass  # Ignore disconnect errors
        
        await self.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from IBKR."""
        async with self._connection_lock:
            if self._connected:
                try:
                    self.ib.disconnect()
                    logger.info("Disconnected from IBKR")
                except Exception as e:
                    logger.warning(f"Error during disconnect: {e}")
                finally:
                    self._connected = False
    
    def is_connected(self) -> bool:
        """Check if currently connected.
        
        Returns:
            True if connected and responsive
        """
        return self._connected and self.ib.isConnected()
    
    def get_connection_stats(self) -> dict[str, Any]:
        """Get connection statistics.
        
        Returns:
            Dictionary with connection stats
        """
        return {
            "connected": self.is_connected(),
            "reconnect_attempts": self._reconnect_attempts,
            "host": self.settings.host,
            "port": self.settings.port,
            "client_id": self.settings.client_id,
            "market_data_type": self.settings.market_data_type,
        }


__all__ = ["IBKRSessionManager"]

