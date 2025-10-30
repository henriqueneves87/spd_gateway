"""
FastAPI dependencies for authentication and validation.
"""
from typing import Optional
from uuid import UUID
from fastapi import Header, HTTPException, status
from src.core.config import settings
from src.core.security import hash_api_key
from src.core.logger import get_logger
from src.db.client import supabase

logger = get_logger(__name__)


async def get_current_merchant(
    x_api_key: Optional[str] = Header(None, alias=settings.api_key_header)
) -> UUID:
    """
    Validate API key and return merchant ID.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        Merchant UUID
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        logger.warning("missing_api_key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Hash the provided API key
    api_key_hash = hash_api_key(x_api_key)
    
    # Look up merchant by API key hash
    try:
        result = supabase.table("merchants")\
            .select("id, is_active")\
            .eq("api_key_hash", api_key_hash)\
            .execute()
        
        if not result.data:
            logger.warning(f"invalid_api_key - key_hash={api_key_hash[:10]}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        merchant = result.data[0]
        
        if not merchant["is_active"]:
            logger.warning(f"inactive_merchant - merchant_id={merchant['id']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Merchant account is inactive"
            )
        
        merchant_id = UUID(merchant["id"])
        logger.info(f"merchant_authenticated - merchant_id={str(merchant_id)}")
        
        return merchant_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"auth_error - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )
