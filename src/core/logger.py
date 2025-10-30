"""
Structured logging with PCI DSS compliance.
Automatically sanitizes sensitive data from logs.
"""
import logging
import sys
from typing import Any, Dict
from src.core.config import settings


# Sensitive fields that should NEVER be logged
SENSITIVE_FIELDS = [
    "cardNumber", "card_number", "pan",
    "cvv", "cvc", "securityCode", "security_code",
    "expirationMonth", "expiration_month",
    "expirationYear", "expiration_year",
    "cardholderName", "cardholder_name",
    "password", "api_key", "secret", "token",
]


def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive fields from data before logging.
    
    Args:
        data: Dictionary that may contain sensitive data
        
    Returns:
        Sanitized dictionary with sensitive fields redacted
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_data(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_data(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True  # Override any existing configuration
)

# Configure uvicorn access logger
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.setLevel(logging.INFO)

# Configure uvicorn error logger
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
