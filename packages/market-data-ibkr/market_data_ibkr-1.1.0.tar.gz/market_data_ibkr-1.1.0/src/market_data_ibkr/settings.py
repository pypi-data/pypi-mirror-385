"""IBKR-specific settings."""

from pydantic import BaseModel, Field


class IBKRSettings(BaseModel):
    """Interactive Brokers connection and behavior settings.
    
    These settings are passed via CoreSettings.provider_extras.
    
    Example:
        ```python
        from market_data_core import CoreSettings
        from market_data_ibkr import IBKRSettings
        
        core_settings = CoreSettings(
            provider_name="ibkr",
            provider_extras={
                "host": "127.0.0.1",
                "port": 4002,
                "client_id": 17,
            }
        )
        
        ibkr_settings = IBKRSettings(**core_settings.provider_extras)
        ```
    """
    
    # ========================================================================
    # Connection Settings
    # ========================================================================
    
    host: str = Field(
        default="127.0.0.1",
        description="IBKR Gateway/TWS host"
    )
    
    port: int = Field(
        default=4002,
        description="IBKR Gateway/TWS port (Paper: 4002, Live: 4001, TWS: 7497)",
        ge=1024,
        le=65535,
    )
    
    client_id: int = Field(
        default=17,
        description="Client ID for this connection",
        ge=0,
        le=9999,
    )
    
    read_timeout_sec: float = Field(
        default=30.0,
        description="Socket read timeout in seconds",
        ge=1.0,
        le=300.0,
    )
    
    # ========================================================================
    # Market Data Settings
    # ========================================================================
    
    market_data_type: int = Field(
        default=1,
        description="Market data type: 1=LIVE, 2=FROZEN, 3=DELAYED, 4=DELAYED_FROZEN",
        ge=1,
        le=4,
    )
    
    snapshot_mode: bool = Field(
        default=False,
        description="Request snapshot data instead of streaming"
    )
    
    # ========================================================================
    # Reconnection Settings
    # ========================================================================
    
    reconnect_enabled: bool = Field(
        default=True,
        description="Enable automatic reconnection"
    )
    
    reconnect_backoff_ms: int = Field(
        default=250,
        description="Initial reconnection backoff in milliseconds",
        ge=100,
        le=60000,
    )
    
    reconnect_backoff_max_ms: int = Field(
        default=5000,
        description="Maximum reconnection backoff in milliseconds",
        ge=1000,
        le=300000,
    )
    
    max_reconnect_attempts: int = Field(
        default=10,
        description="Maximum reconnection attempts (0 = infinite)",
        ge=0,
        le=100,
    )
    
    # ========================================================================
    # Historical Data Pacing
    # ========================================================================
    
    hist_pacing_window_sec: int = Field(
        default=600,
        description="Historical data pacing window (IBKR enforces 10-min cooldown)",
        ge=60,
        le=3600,
    )
    
    hist_max_bars_per_request: int = Field(
        default=2000,
        description="Maximum bars per historical request",
        ge=1,
        le=10000,
    )
    
    # ========================================================================
    # Options Settings
    # ========================================================================
    
    options_semaphore_size: int = Field(
        default=5,
        description="Concurrent options requests limit",
        ge=1,
        le=50,
    )
    
    options_base_delay: float = Field(
        default=0.1,
        description="Base delay between options requests (seconds)",
        ge=0.01,
        le=10.0,
    )
    
    options_max_contracts: int = Field(
        default=50,
        description="Maximum option contracts to fetch per chain",
        ge=1,
        le=500,
    )
    
    options_max_retries: int = Field(
        default=3,
        description="Maximum retries for failed options requests",
        ge=0,
        le=10,
    )
    
    options_backoff_multiplier: float = Field(
        default=1.5,
        description="Backoff multiplier for options pacing violations",
        ge=1.0,
        le=5.0,
    )
    
    class Config:
        extra = "forbid"  # Fail on unknown fields
        frozen = False  # Allow modification


__all__ = ["IBKRSettings"]

