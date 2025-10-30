"""
Security utilities for API Key validation and webhook signature verification.
"""
import hmac
import hashlib
from typing import Optional
from fastapi import Header, HTTPException, status
from src.core.config import settings
from src.core.exceptions import UnauthorizedError, InvalidWebhookSignatureError


async def validate_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.api_key_header)
) -> str:
    """
    Validate API key from request header.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    # TODO: Validate against database
    # For now, just check if it exists
    # In production: hash the key and compare with stored hash
    
    return x_api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for secure storage.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Validate webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw webhook payload
        signature: Signature from webhook header
        secret: Webhook secret key
        
    Returns:
        True if signature is valid
        
    Raises:
        InvalidWebhookSignatureError: If signature is invalid
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise InvalidWebhookSignatureError()
    
    return True


def mask_card_number(card_number: str) -> str:
    """
    Mask card number for safe display (show only last 4 digits).
    
    Args:
        card_number: Full card number
        
    Returns:
        Masked card number (e.g., "****1234")
    """
    if len(card_number) < 4:
        return "****"
    
    return f"****{card_number[-4:]}"
