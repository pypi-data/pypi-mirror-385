"""IBKR provider implementation of MarketDataProvider protocol."""

import asyncio
from datetime import datetime
from typing import AsyncIterable, Iterable

from ib_insync import Stock
from loguru import logger
from market_data_core import (
    Bar,
    Instrument,
    OptionSnapshot,
    Quote,
    Trade,
)

from .errors import handle_ib_error
from .mapping import (
    ibkr_bar_to_bar,
    ibkr_ticker_to_quote,
    parse_ibkr_resolution,
)
from .pacing import PacingManager, TokenBucket
from .session import IBKRSessionManager
from .settings import IBKRSettings


class IBKRProvider:
    """IBKR implementation of MarketDataProvider protocol.
    
    This provider connects to Interactive Brokers Gateway/TWS and implements
    all market data streaming methods defined in the Core protocol.
    
    Features:
    - Real-time quote streaming
    - Real-time bar streaming  
    - Historical bar requests with pacing
    - Options chain streaming (TODO)
    - Automatic reconnection
    - Rate limiting and cooldown management
    
    Example:
        ```python
        from market_data_core import Instrument
        from market_data_ibkr import IBKRProvider, IBKRSettings
        
        settings = IBKRSettings(host="127.0.0.1", port=4002)
        
        async with IBKRProvider(settings) as provider:
            instruments = [Instrument(symbol="AAPL")]
            async for quote in provider.stream_quotes(instruments):
                print(quote)
        ```
    """
    
    def __init__(self, settings: IBKRSettings):
        """Initialize IBKR provider.
        
        Args:
            settings: IBKR connection and behavior settings
        """
        self.settings = settings
        self.session = IBKRSessionManager(settings)
        self.pacing = PacingManager(settings.hist_pacing_window_sec)
        
        # Rate limiters
        self._hist_rate_limiter = TokenBucket(
            capacity=60,  # IBKR allows ~60 requests per 10 min
            refill_rate=0.1,  # 6 per minute = 0.1 per second
        )
        
        # Active subscriptions tracking
        self._quote_subscriptions: dict[str, any] = {}
        self._bar_subscriptions: dict[str, any] = {}
        
        # Contract cache for performance
        self._contract_cache: dict[tuple[str, str, str], any] = {}
    
    # ========================================================================
    # Context Manager Support
    # ========================================================================
    
    async def __aenter__(self):
        """Enter async context manager."""
        await self.session.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        await self.close()
    
    # ========================================================================
    # Quote Streaming
    # ========================================================================
    
    async def stream_quotes(
        self,
        instruments: Iterable[Instrument],
    ) -> AsyncIterable[Quote]:
        """Stream real-time quotes for instruments.
        
        Args:
            instruments: Instruments to subscribe to
            
        Yields:
            Quote objects as they arrive
            
        Raises:
            ConnectionFailed: Cannot connect to IBKR
            PermissionsMissing: No market data permissions
            PacingViolation: Too many subscriptions
        """
        await self.session.ensure_connected()
        
        # Convert instruments to IBKR contracts and subscribe
        for instrument in instruments:
            try:
                contract = self._instrument_to_contract(instrument)
                ticker = self.session.ib.reqMktData(
                    contract, 
                    "", 
                    self.settings.snapshot_mode, 
                    False
                )
                self._quote_subscriptions[instrument.symbol] = ticker
                
                logger.info(f"Subscribed to quotes for {instrument.symbol}")
                
            except Exception as e:
                error = handle_ib_error(e)
                logger.error(f"Failed to subscribe to {instrument.symbol}: {error}")
                raise error
        
        # Stream updates
        try:
            while True:
                await self.session.ensure_connected()
                
                # Wait for any update from IBKR
                try:
                    await asyncio.wait_for(
                        self.session.ib.waitOnUpdateEvent(),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue  # No updates, check connection and retry
                
                # Yield quotes for all subscribed instruments
                for symbol, ticker in self._quote_subscriptions.items():
                    if getattr(ticker, "time", None):  # Has data
                        try:
                            quote = ibkr_ticker_to_quote(ticker, symbol)
                            yield quote
                        except Exception as e:
                            logger.warning(f"Error converting ticker for {symbol}: {e}")
                
        except asyncio.CancelledError:
            logger.info("Quote streaming cancelled")
            await self._cleanup_quote_subscriptions()
            raise
        
        except Exception as e:
            logger.error(f"Quote streaming error: {e}")
            await self._cleanup_quote_subscriptions()
            raise handle_ib_error(e)
    
    # ========================================================================
    # Bar Streaming
    # ========================================================================
    
    async def stream_bars(
        self,
        resolution: str,
        instruments: Iterable[Instrument],
    ) -> AsyncIterable[Bar]:
        """Stream real-time bars for instruments.
        
        Note: IBKR reqRealTimeBars only supports 5-second bars.
        For other resolutions, consider using reqHistoricalData with keepUpToDate=True
        or aggregating from ticks.
        
        Args:
            resolution: Bar resolution (e.g., "1s", "5s", "1m", "5m")
            instruments: Instruments to subscribe to
            
        Yields:
            Bar objects as they complete
            
        Raises:
            ConnectionFailed: Cannot connect to IBKR
            PermissionsMissing: No market data permissions
        """
        await self.session.ensure_connected()
        
        # Parse resolution (for logging)
        bar_size, _ = parse_ibkr_resolution(resolution)
        logger.info(f"Requested real-time bars: {resolution} (IBKR real-time is fixed at 5s) → {bar_size}")
        
        # Subscribe to real-time bars for each instrument
        for instrument in instruments:
            try:
                contract = self._instrument_to_contract(instrument)
                
                # IBKR reqRealTimeBars only supports 5-second bars
                bars = self.session.ib.reqRealTimeBars(
                    contract,
                    5,  # 5-second bars only
                    "TRADES",
                    False  # Regular trading hours only
                )
                
                self._bar_subscriptions[instrument.symbol] = bars
                logger.info(f"Subscribed to {resolution} bars for {instrument.symbol}")
                
            except Exception as e:
                error = handle_ib_error(e)
                logger.error(f"Failed to subscribe to bars for {instrument.symbol}: {error}")
                raise error
        
        # Stream bar updates
        try:
            while True:
                await self.session.ensure_connected()
                
                # Wait for updates
                try:
                    await asyncio.wait_for(
                        self.session.ib.waitOnUpdateEvent(),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check all bar subscriptions for new bars
                for symbol, bars in self._bar_subscriptions.items():
                    if bars and len(bars) > 0:
                        latest_bar = bars[-1]
                        try:
                            bar = ibkr_bar_to_bar(latest_bar, symbol, resolution)
                            yield bar
                        except Exception as e:
                            logger.warning(f"Error converting bar for {symbol}: {e}")
        
        except asyncio.CancelledError:
            logger.info("Bar streaming cancelled")
            await self._cleanup_bar_subscriptions()
            raise
        
        except Exception as e:
            logger.error(f"Bar streaming error: {e}")
            await self._cleanup_bar_subscriptions()
            raise handle_ib_error(e)
    
    # ========================================================================
    # Historical Data
    # ========================================================================
    
    async def request_historical_bars(
        self,
        instrument: Instrument,
        start: datetime,
        end: datetime,
        resolution: str,
    ) -> AsyncIterable[Bar]:
        """Request historical bars with pacing control.
        
        Args:
            instrument: Single instrument
            start: Start datetime (UTC)
            end: End datetime (UTC)
            resolution: Bar resolution (e.g., "1m", "1h", "1d")
            
        Yields:
            Bar objects in chronological order
            
        Raises:
            PacingViolation: Rate limit exceeded or in cooldown
            PermissionsMissing: No historical data permissions
            InvalidInstrument: Unknown instrument
        """
        await self.session.ensure_connected()
        
        # Check cooldown
        scope = f"hist_{instrument.symbol}"
        if not await self.pacing.check_cooldown(scope):
            from market_data_core import PacingViolation
            raise PacingViolation(
                f"Historical data for {instrument.symbol} is in cooldown"
            )
        
        # Acquire rate limit token
        acquired = await self._hist_rate_limiter.acquire(
            tokens=1,
            timeout=30.0
        )
        if not acquired:
            from market_data_core import PacingViolation
            raise PacingViolation("Historical data rate limit exceeded")
        
        # Parse resolution
        bar_size, duration_str = parse_ibkr_resolution(resolution)
        
        try:
            contract = self._instrument_to_contract(instrument)
            
            # Request historical data
            bars = await self.session.ib.reqHistoricalDataAsync(
                contract,
                endDateTime=end,
                durationStr=duration_str,
                barSizeSetting=bar_size,
                whatToShow="TRADES",
                useRTH=True,  # Regular trading hours
                formatDate=1,  # Return as datetime
            )
            
            # Yield bars in chronological order
            for bar in bars:
                yield ibkr_bar_to_bar(bar, instrument.symbol, resolution)
        
        except Exception as e:
            error = handle_ib_error(e)
            
            # If pacing violation, trigger cooldown
            from market_data_core import PacingViolation
            if isinstance(error, PacingViolation):
                await self.pacing.trigger_cooldown(
                    scope,
                    self.settings.hist_pacing_window_sec
                )
            
            logger.error(f"Historical data request failed for {instrument.symbol}: {error}")
            raise error
    
    # ========================================================================
    # Trade Streaming (Tick-by-Tick)
    # ========================================================================
    
    async def stream_trades(
        self,
        instruments: Iterable[Instrument],
    ) -> AsyncIterable[Trade]:
        """Stream tick-by-tick trades.
        
        Note: IBKR tick-by-tick data requires additional permissions
        and is subject to strict rate limits.
        
        TODO: Implement tick-by-tick streaming using reqTickByTickData()
        
        Args:
            instruments: Instruments to subscribe to
            
        Yields:
            Trade objects as they occur
            
        Raises:
            NotImplementedError: Not yet implemented
            PermissionsMissing: No tick-by-tick permissions
            PacingViolation: Too many subscriptions
        """
        raise NotImplementedError(
            "Tick-by-tick streaming not yet implemented. "
            "Use reqTickByTickData() from ib_insync to implement."
        )
    
    # ========================================================================
    # Options Chain
    # ========================================================================
    
    async def stream_options(
        self,
        instrument: Instrument,
        expiry: str | None = None,
        strike_range: tuple[float, float] | None = None,
        moneyness_range: float = 0.2,
    ) -> AsyncIterable[OptionSnapshot]:
        """Stream options chain snapshots.
        
        TODO: Implement options chain streaming
        
        Implementation steps:
        1. Use reqSecDefOptParams() to get available strikes/expiries
        2. Filter by moneyness_range and expiry
        3. Request market data for each contract
        4. Apply pacing controls (options_semaphore_size, options_base_delay)
        5. Yield OptionSnapshot objects
        
        Args:
            instrument: Underlying instrument
            expiry: Optional expiry filter (YYYYMMDD)
            strike_range: Optional (min_strike, max_strike)
            moneyness_range: Filter by moneyness (default ±20%)
            
        Yields:
            OptionSnapshot objects
            
        Raises:
            NotImplementedError: Not yet implemented
            PermissionsMissing: No options data permissions
            PacingViolation: Options request rate limit
        """
        raise NotImplementedError(
            "Options chain streaming not yet implemented. "
            "Implementation requires: reqSecDefOptParams(), option contract "
            "creation, and pacing management."
        )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _instrument_to_contract(self, instrument: Instrument):
        """Convert Core Instrument to ib_insync Contract.
        
        Uses caching for performance.
        
        TODO: Support other security types (options, futures, forex, etc.)
        based on instrument.sec_type field.
        
        Args:
            instrument: Core instrument
            
        Returns:
            ib_insync Contract object
        """
        # Create cache key
        cache_key = (
            instrument.symbol,
            instrument.sec_type or "STK",
            instrument.exchange or "SMART"
        )
        
        # Check cache
        if cache_key in self._contract_cache:
            return self._contract_cache[cache_key]
        
        # For now, assume stocks
        # TODO: Route by sec_type when Core protocol supports it
        contract = Stock(
            symbol=instrument.symbol,
            exchange=instrument.exchange or "SMART",
            currency=instrument.currency or "USD"
        )
        
        # Cache it
        self._contract_cache[cache_key] = contract
        
        return contract
    
    async def _cleanup_quote_subscriptions(self) -> None:
        """Cancel all quote subscriptions."""
        for symbol, ticker in list(self._quote_subscriptions.items()):
            try:
                self.session.ib.cancelMktData(ticker.contract)
                logger.debug(f"Cancelled quote subscription for {symbol}")
            except Exception as e:
                logger.warning(f"Error cancelling quote subscription for {symbol}: {e}")
        
        self._quote_subscriptions.clear()
    
    async def _cleanup_bar_subscriptions(self) -> None:
        """Cancel all bar subscriptions."""
        for symbol, bars in list(self._bar_subscriptions.items()):
            try:
                self.session.ib.cancelRealTimeBars(bars)
                logger.debug(f"Cancelled bar subscription for {symbol}")
            except Exception as e:
                logger.warning(f"Error cancelling bar subscription for {symbol}: {e}")
        
        self._bar_subscriptions.clear()
    
    async def close(self) -> None:
        """Clean shutdown of provider."""
        logger.info("Closing IBKR provider")
        
        await self._cleanup_quote_subscriptions()
        await self._cleanup_bar_subscriptions()
        await self.session.disconnect()
        
        logger.info("IBKR provider closed")


__all__ = ["IBKRProvider"]

