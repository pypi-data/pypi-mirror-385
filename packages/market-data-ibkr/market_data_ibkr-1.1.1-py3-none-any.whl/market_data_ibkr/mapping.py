"""Data mapping utilities for converting IBKR objects to Core DTOs."""

from datetime import datetime
from decimal import Decimal

from ib_insync import BarData, Ticker
from market_data_core import Bar, Quote


def ibkr_ticker_to_quote(ticker: Ticker, symbol: str) -> Quote:
    """Convert IBKR Ticker to Core Quote.
    
    Args:
        ticker: ib_insync Ticker object
        symbol: Symbol string
        
    Returns:
        Core Quote DTO
    """
    return Quote(
        symbol=symbol,
        bid=Decimal(str(ticker.bid)) if getattr(ticker, "bid", None) and ticker.bid > 0 else None,
        ask=Decimal(str(ticker.ask)) if getattr(ticker, "ask", None) and ticker.ask > 0 else None,
        last=Decimal(str(ticker.last)) if getattr(ticker, "last", None) and ticker.last > 0 else None,
        bid_size=int(ticker.bidSize) if getattr(ticker, "bidSize", None) else None,
        ask_size=int(ticker.askSize) if getattr(ticker, "askSize", None) else None,
        volume=int(ticker.volume) if getattr(ticker, "volume", None) else 0,
        timestamp=datetime.utcnow(),
        delayed=getattr(ticker, 'delayed', False),
    )


def ibkr_bar_to_bar(bar: BarData, symbol: str, resolution: str) -> Bar:
    """Convert IBKR BarData to Core Bar.
    
    Args:
        bar: ib_insync BarData object
        symbol: Symbol string
        resolution: Bar resolution (e.g., "1m", "1h", "1d")
        
    Returns:
        Core Bar DTO
    """
    # Parse timestamp
    if isinstance(bar.date, datetime):
        ts = bar.date
    else:
        ts = datetime.fromisoformat(str(bar.date))
    
    return Bar(
        symbol=symbol,
        ts=ts,
        open=Decimal(str(bar.open)),
        high=Decimal(str(bar.high)),
        low=Decimal(str(bar.low)),
        close=Decimal(str(bar.close)),
        volume=Decimal(str(bar.volume)),
        resolution=resolution,
        delayed=False,
    )


def parse_ibkr_resolution(resolution: str) -> tuple[str, str]:
    """Parse Core resolution string to IBKR format.
    
    Args:
        resolution: Core resolution (e.g., "1s", "5m", "1h", "1d")
        
    Returns:
        Tuple of (bar_size, duration_str) for IBKR
        
    Examples:
        >>> parse_ibkr_resolution("1m")
        ("1 min", "1 D")
        
        >>> parse_ibkr_resolution("1d")
        ("1 day", "1 Y")
    """
    resolution_map = {
        "1s": ("1 secs", "1800 S"),  # 30 min of 1-sec bars
        "5s": ("5 secs", "3600 S"),  # 1 hour of 5-sec bars
        "10s": ("10 secs", "7200 S"),  # 2 hours of 10-sec bars
        "15s": ("15 secs", "14400 S"),  # 4 hours of 15-sec bars
        "30s": ("30 secs", "28800 S"),  # 8 hours of 30-sec bars
        "1m": ("1 min", "1 D"),
        "2m": ("2 mins", "2 D"),
        "3m": ("3 mins", "1 W"),
        "5m": ("5 mins", "1 W"),
        "10m": ("10 mins", "1 W"),
        "15m": ("15 mins", "1 W"),
        "20m": ("20 mins", "1 W"),
        "30m": ("30 mins", "1 M"),
        "1h": ("1 hour", "1 M"),
        "2h": ("2 hours", "1 M"),
        "3h": ("3 hours", "1 M"),
        "4h": ("4 hours", "1 M"),
        "8h": ("8 hours", "1 M"),
        "1d": ("1 day", "1 Y"),
        "1w": ("1 week", "2 Y"),
        "1M": ("1 month", "5 Y"),
    }
    
    if resolution in resolution_map:
        return resolution_map[resolution]
    
    # Default fallback
    return ("1 min", "1 D")


__all__ = [
    "ibkr_ticker_to_quote",
    "ibkr_bar_to_bar",
    "parse_ibkr_resolution",
]

