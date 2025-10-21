"""Interactive Brokers provider for market-data-core.

This package implements the MarketDataProvider protocol using ib_insync
to connect to Interactive Brokers Gateway/TWS.

Example:
    ```python
    from market_data_core import Instrument
    from market_data_ibkr import IBKRProvider, IBKRSettings
    
    # Configure
    settings = IBKRSettings(
        host="127.0.0.1",
        port=4002,  # Paper trading
        client_id=17,
    )
    
    # Create provider
    async with IBKRProvider(settings) as provider:
        # Stream quotes
        instruments = [Instrument(symbol="AAPL"), Instrument(symbol="MSFT")]
        async for quote in provider.stream_quotes(instruments):
            print(f"{quote.symbol}: {quote.last}")
    ```
"""

from .errors import ERROR_CODE_MAP, handle_ib_error, map_ibkr_error
from .mapping import ibkr_bar_to_bar, ibkr_ticker_to_quote, parse_ibkr_resolution
from .pacing import PacingManager, TokenBucket
from .provider import IBKRProvider
from .session import IBKRSessionManager
from .settings import IBKRSettings

# Server components (optional import for web service mode)
try:
    from .server import app as server_app
    _has_server = True
except ImportError:
    server_app = None
    _has_server = False

__version__ = "1.1.1"

__all__ = [
    # Main exports
    "IBKRProvider",
    "IBKRSettings",
    # Session management
    "IBKRSessionManager",
    # Error handling
    "map_ibkr_error",
    "handle_ib_error",
    "ERROR_CODE_MAP",
    # Pacing
    "PacingManager",
    "TokenBucket",
    # Mapping utilities
    "ibkr_ticker_to_quote",
    "ibkr_bar_to_bar",
    "parse_ibkr_resolution",
    # Server (if available)
    "server_app",
    # Version
    "__version__",
]

