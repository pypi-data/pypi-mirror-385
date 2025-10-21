"""Test data mapping utilities."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from market_data_ibkr.mapping import (
    ibkr_ticker_to_quote,
    ibkr_bar_to_bar,
    parse_ibkr_resolution,
)


def test_ibkr_ticker_to_quote():
    """Test converting IBKR Ticker to Quote."""
    # Mock ticker
    ticker = MagicMock()
    ticker.bid = 150.50
    ticker.ask = 150.55
    ticker.last = 150.52
    ticker.bidSize = 100
    ticker.askSize = 200
    ticker.volume = 1000000
    ticker.delayed = False
    ticker.time = datetime.utcnow()
    
    quote = ibkr_ticker_to_quote(ticker, "AAPL")
    
    assert quote.symbol == "AAPL"
    assert quote.bid == Decimal("150.50")
    assert quote.ask == Decimal("150.55")
    assert quote.last == Decimal("150.52")
    assert quote.bid_size == 100
    assert quote.ask_size == 200
    assert quote.volume == 1000000
    assert quote.delayed is False


def test_ibkr_ticker_to_quote_with_none_values():
    """Test converting ticker with None values."""
    ticker = MagicMock()
    ticker.bid = None
    ticker.ask = None
    ticker.last = None
    ticker.bidSize = None
    ticker.askSize = None
    ticker.volume = None
    ticker.delayed = False
    ticker.time = None
    
    quote = ibkr_ticker_to_quote(ticker, "TEST")
    
    assert quote.symbol == "TEST"
    assert quote.bid is None
    assert quote.ask is None
    assert quote.last is None
    assert quote.volume == 0


def test_ibkr_bar_to_bar():
    """Test converting IBKR BarData to Bar."""
    # Mock bar
    bar = MagicMock()
    bar.date = datetime(2025, 10, 15, 12, 0, 0)
    bar.open = 150.00
    bar.high = 151.00
    bar.low = 149.50
    bar.close = 150.75
    bar.volume = 500000
    
    result = ibkr_bar_to_bar(bar, "AAPL", "1m")
    
    assert result.symbol == "AAPL"
    assert result.ts == datetime(2025, 10, 15, 12, 0, 0)
    assert result.open == Decimal("150.00")
    assert result.high == Decimal("151.00")
    assert result.low == Decimal("149.50")
    assert result.close == Decimal("150.75")
    assert result.volume == Decimal("500000")
    assert result.resolution == "1m"
    assert result.delayed is False


def test_parse_ibkr_resolution_1m():
    """Test parsing 1m resolution."""
    bar_size, duration = parse_ibkr_resolution("1m")
    assert bar_size == "1 min"
    assert duration == "1 D"


def test_parse_ibkr_resolution_5m():
    """Test parsing 5m resolution."""
    bar_size, duration = parse_ibkr_resolution("5m")
    assert bar_size == "5 mins"
    assert duration == "1 W"


def test_parse_ibkr_resolution_1h():
    """Test parsing 1h resolution."""
    bar_size, duration = parse_ibkr_resolution("1h")
    assert bar_size == "1 hour"
    assert duration == "1 M"


def test_parse_ibkr_resolution_1d():
    """Test parsing 1d resolution."""
    bar_size, duration = parse_ibkr_resolution("1d")
    assert bar_size == "1 day"
    assert duration == "1 Y"


def test_parse_ibkr_resolution_1s():
    """Test parsing 1s resolution."""
    bar_size, duration = parse_ibkr_resolution("1s")
    assert bar_size == "1 secs"
    assert duration == "1800 S"


def test_parse_ibkr_resolution_unknown():
    """Test parsing unknown resolution defaults to 1m."""
    bar_size, duration = parse_ibkr_resolution("99z")
    assert bar_size == "1 min"
    assert duration == "1 D"

