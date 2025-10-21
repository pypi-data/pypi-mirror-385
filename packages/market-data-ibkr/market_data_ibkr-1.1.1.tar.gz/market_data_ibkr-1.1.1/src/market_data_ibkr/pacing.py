"""Rate limiting and pacing management for IBKR.

IBKR has strict rate limits:
- Historical data: Max 60 requests per 10 minutes
- Market data: Varies by subscription tier
- After pacing violation: 10-minute cooldown for same scope

This module provides:
- TokenBucket: Generic rate limiter
- PacingManager: Cooldown tracking per scope
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict

from loguru import logger


class TokenBucket:
    """Token bucket rate limiter.
    
    Implements the token bucket algorithm for rate limiting.
    Tokens are added at a fixed rate and consumed per request.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self._last_refill = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1, timeout: float | None = None) -> bool:
        """Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum wait time in seconds (None = wait forever)
            
        Returns:
            True if tokens acquired, False if timeout
        """
        start_time = datetime.now()
        
        while True:
            async with self._lock:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
            
            # Check timeout
            if timeout is not None:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    return False
            
            # Wait before retry
            await asyncio.sleep(0.1)
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = datetime.now()
        elapsed = (now - self._last_refill).total_seconds()
        
        if elapsed > 0:
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self._last_refill = now
    
    async def get_available_tokens(self) -> float:
        """Get current available tokens.
        
        Returns:
            Number of tokens available
        """
        async with self._lock:
            self._refill()
            return self.tokens


class PacingManager:
    """Manages pacing violations and cooldown periods.
    
    Tracks scopes (e.g., "historical_AAPL") and enforces cooldown
    periods after pacing violations.
    """
    
    def __init__(self, default_cooldown_sec: int = 600):
        """Initialize pacing manager.
        
        Args:
            default_cooldown_sec: Default cooldown period (10 min for IBKR)
        """
        self.default_cooldown_sec = default_cooldown_sec
        self._cooldowns: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
    
    async def check_cooldown(self, scope: str) -> bool:
        """Check if scope is in cooldown.
        
        Args:
            scope: Scope identifier (e.g., "historical_AAPL")
            
        Returns:
            True if available (not in cooldown), False if in cooldown
        """
        async with self._lock:
            if scope in self._cooldowns:
                cooldown_until = self._cooldowns[scope]
                if datetime.now() < cooldown_until:
                    remaining = (cooldown_until - datetime.now()).total_seconds()
                    logger.warning(
                        f"Scope '{scope}' in cooldown for {remaining:.0f} more seconds"
                    )
                    return False
                else:
                    # Cooldown expired
                    del self._cooldowns[scope]
            
            return True
    
    async def trigger_cooldown(
        self,
        scope: str,
        duration_sec: int | None = None
    ) -> None:
        """Put scope into cooldown.
        
        Args:
            scope: Scope identifier
            duration_sec: Cooldown duration (None = use default)
        """
        duration = duration_sec if duration_sec is not None else self.default_cooldown_sec
        cooldown_until = datetime.now() + timedelta(seconds=duration)
        
        async with self._lock:
            self._cooldowns[scope] = cooldown_until
            logger.warning(
                f"Triggered cooldown for scope '{scope}' until "
                f"{cooldown_until.strftime('%H:%M:%S')} ({duration}s)"
            )
    
    async def get_cooldown_status(self, scope: str) -> dict:
        """Get cooldown status for scope.
        
        Args:
            scope: Scope identifier
            
        Returns:
            Dictionary with status information
        """
        async with self._lock:
            if scope in self._cooldowns:
                cooldown_until = self._cooldowns[scope]
                remaining = (cooldown_until - datetime.now()).total_seconds()
                
                return {
                    "in_cooldown": remaining > 0,
                    "remaining_sec": max(0, remaining),
                    "cooldown_until": cooldown_until.isoformat(),
                }
            
            return {
                "in_cooldown": False,
                "remaining_sec": 0,
                "cooldown_until": None,
            }
    
    async def clear_cooldown(self, scope: str) -> None:
        """Manually clear cooldown for scope.
        
        Args:
            scope: Scope identifier
        """
        async with self._lock:
            if scope in self._cooldowns:
                del self._cooldowns[scope]
                logger.info(f"Cleared cooldown for scope '{scope}'")
    
    async def clear_all_cooldowns(self) -> None:
        """Clear all cooldowns."""
        async with self._lock:
            count = len(self._cooldowns)
            self._cooldowns.clear()
            logger.info(f"Cleared all {count} cooldowns")


__all__ = [
    "TokenBucket",
    "PacingManager",
]

