"""
Utility functions for SiliconPulse backend
"""
from datetime import datetime
from typing import Any

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or len(api_key) < 10:
        return False
    return True

def format_error_response(message: str, code: str = "ERROR") -> dict[str, Any]:
    """Format error response"""
    return {
        "error": code,
        "message": message,
        "timestamp": get_current_timestamp()
    }
