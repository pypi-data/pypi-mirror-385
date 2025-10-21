"""IBKR error code mapping to Core canonical errors.

IBKR Error Codes (from documentation and experience):
- 2104: "Market data farm connection is OK" (informational)
- 162: Ambiguous umbrella code (permissions, pacing, invalid request)
- 200: "No security definition has been found" (invalid instrument)
- 354: "Requested market data is not subscribed" (permissions)
- 420: "Pacing violation" (rate limit)
- 504: "Not connected" (connection error)
- 1100: "Connectivity between IB and TWS has been lost" (connection error)
- 2110: "Connectivity between TWS and server is broken" (farm transient)
"""

from loguru import logger
from market_data_core import (
    ConnectionFailed,
    FarmTransient,
    InvalidInstrument,
    MarketDataError,
    PacingViolation,
    PermissionsMissing,
    RetryableProviderError,
)


# Error code mapping table
ERROR_CODE_MAP: dict[int, type[MarketDataError] | None] = {
    # Informational (not errors)
    2104: None,  # "Farm OK" - handled separately
    
    # Pacing violations
    420: PacingViolation,
    
    # Invalid instruments
    200: InvalidInstrument,
    
    # Permissions
    354: PermissionsMissing,
    
    # Connection issues
    504: ConnectionFailed,
    1100: ConnectionFailed,
    
    # Farm transient
    2110: FarmTransient,
}


def map_ibkr_error(code: int, message: str) -> MarketDataError | None:
    """Map IBKR error code and message to Core canonical error.
    
    Args:
        code: IBKR error code
        message: Error message from IBKR
        
    Returns:
        Canonical error instance, or None if informational only
        
    Examples:
        >>> map_ibkr_error(2104, "Market data farm connection is OK")
        None  # Just log, not an error
        
        >>> map_ibkr_error(420, "Pacing violation")
        PacingViolation("IBKR 420: Pacing violation")
        
        >>> map_ibkr_error(162, "No market data permissions for AAPL")
        PermissionsMissing("No market data permissions for AAPL")
    """
    
    # Check if code is in explicit mapping
    if code in ERROR_CODE_MAP:
        error_class = ERROR_CODE_MAP[code]
        
        if error_class is None:
            # Informational message, just log
            logger.info(f"IBKR {code}: {message}")
            return None
        
        # Create error instance
        return error_class(message, code=f"IBKR_{code}")
    
    # Special handling for error 162 (ambiguous)
    if code == 162:
        return _parse_error_162(message)
    
    # Unknown error - default to retryable
    logger.warning(f"Unknown IBKR error code {code}: {message}")
    return RetryableProviderError(f"IBKR {code}: {message}", code=f"IBKR_{code}")


def _parse_error_162(message: str) -> MarketDataError:
    """Parse ambiguous error 162 by inspecting message text.
    
    Error 162 is used for multiple scenarios:
    - "No market data permissions" → PermissionsMissing
    - "exceeds max duration" → PacingViolation
    - "Historical market data Service error" → Could be various
    
    Args:
        message: Error message text
        
    Returns:
        Appropriate canonical error
    """
    msg_lower = message.lower()
    
    # Check for permissions issues
    if any(keyword in msg_lower for keyword in [
        "no market data permissions",
        "not subscribed",
        "no subscription",
    ]):
        return PermissionsMissing(message, code="IBKR_162")
    
    # Check for pacing violations
    if any(keyword in msg_lower for keyword in [
        "exceeds",
        "pace",
        "max duration",
        "rate limit",
    ]):
        return PacingViolation(message, code="IBKR_162")
    
    # Check for invalid requests
    if any(keyword in msg_lower for keyword in [
        "invalid",
        "not found",
        "unknown",
    ]):
        return InvalidInstrument(message, code="IBKR_162")
    
    # Unknown 162 variant - default to retryable
    logger.warning(f"Ambiguous error 162: {message}")
    return RetryableProviderError(f"IBKR 162: {message}", code="IBKR_162")


def handle_ib_error(error: Exception) -> MarketDataError:
    """Handle any exception from ib_insync.
    
    Args:
        error: Exception from ib_insync
        
    Returns:
        Canonical error instance
    """
    # Extract code and message from ib_insync error
    error_code = getattr(error, "code", 0)
    error_message = str(error)
    
    # Map to canonical error
    canonical_error = map_ibkr_error(error_code, error_message)
    
    if canonical_error is None:
        # Informational only, return generic retryable
        return RetryableProviderError(error_message)
    
    return canonical_error


__all__ = [
    "map_ibkr_error",
    "handle_ib_error",
    "ERROR_CODE_MAP",
]

