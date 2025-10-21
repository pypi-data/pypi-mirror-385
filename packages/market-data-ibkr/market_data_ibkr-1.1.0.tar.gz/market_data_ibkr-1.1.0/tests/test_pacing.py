"""Test pacing and rate limiting."""

import pytest
import asyncio
from datetime import datetime, timedelta

from market_data_ibkr.pacing import TokenBucket, PacingManager


class TestTokenBucket:
    """Tests for TokenBucket rate limiter."""
    
    @pytest.mark.asyncio
    async def test_acquire_immediately_when_tokens_available(self):
        """Test that tokens are acquired immediately when available."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        result = await bucket.acquire(tokens=5, timeout=1.0)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_acquire_fails_on_timeout(self):
        """Test that acquire fails when timeout is exceeded."""
        bucket = TokenBucket(capacity=1, refill_rate=0.1)
        # Take all tokens
        await bucket.acquire(tokens=1)
        # Try to acquire more, should timeout
        result = await bucket.acquire(tokens=1, timeout=0.5)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_token_refill(self):
        """Test that tokens refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens per second
        
        # Take all tokens
        await bucket.acquire(tokens=10)
        
        # Wait for refill
        await asyncio.sleep(0.2)  # Should refill ~2 tokens
        
        # Should be able to acquire 1 token
        result = await bucket.acquire(tokens=1, timeout=0.1)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_available_tokens(self):
        """Test getting available token count."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        await bucket.acquire(tokens=5)
        available = await bucket.get_available_tokens()
        assert 4.0 <= available <= 6.0  # Allow some timing variation


class TestPacingManager:
    """Tests for PacingManager cooldown tracking."""
    
    @pytest.mark.asyncio
    async def test_check_cooldown_initially_available(self):
        """Test that scope is initially available."""
        manager = PacingManager(default_cooldown_sec=60)
        result = await manager.check_cooldown("test_scope")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_trigger_cooldown(self):
        """Test triggering a cooldown."""
        manager = PacingManager(default_cooldown_sec=60)
        await manager.trigger_cooldown("test_scope", duration_sec=1)
        result = await manager.check_cooldown("test_scope")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cooldown_expires(self):
        """Test that cooldown expires after duration."""
        manager = PacingManager(default_cooldown_sec=1)
        await manager.trigger_cooldown("test_scope", duration_sec=1)
        
        # Should be in cooldown
        assert await manager.check_cooldown("test_scope") is False
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be available again
        assert await manager.check_cooldown("test_scope") is True
    
    @pytest.mark.asyncio
    async def test_get_cooldown_status(self):
        """Test getting cooldown status."""
        manager = PacingManager()
        await manager.trigger_cooldown("test_scope", duration_sec=60)
        
        status = await manager.get_cooldown_status("test_scope")
        assert status["in_cooldown"] is True
        assert 50 < status["remaining_sec"] < 61  # Allow some timing variation
        assert status["cooldown_until"] is not None
    
    @pytest.mark.asyncio
    async def test_clear_cooldown(self):
        """Test manually clearing a cooldown."""
        manager = PacingManager()
        await manager.trigger_cooldown("test_scope", duration_sec=60)
        
        # Should be in cooldown
        assert await manager.check_cooldown("test_scope") is False
        
        # Clear it
        await manager.clear_cooldown("test_scope")
        
        # Should be available now
        assert await manager.check_cooldown("test_scope") is True
    
    @pytest.mark.asyncio
    async def test_clear_all_cooldowns(self):
        """Test clearing all cooldowns."""
        manager = PacingManager()
        await manager.trigger_cooldown("scope1", duration_sec=60)
        await manager.trigger_cooldown("scope2", duration_sec=60)
        
        # Both should be in cooldown
        assert await manager.check_cooldown("scope1") is False
        assert await manager.check_cooldown("scope2") is False
        
        # Clear all
        await manager.clear_all_cooldowns()
        
        # Both should be available
        assert await manager.check_cooldown("scope1") is True
        assert await manager.check_cooldown("scope2") is True

