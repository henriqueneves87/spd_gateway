"""
Tokenization endpoints - Internal use only
IMPORTANTE: Este endpoint processa PANs e requer PCI DSS compliance
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from src.core.logger import get_logger
from src.api.dependencies import get_current_merchant
from src.adapters.adiq import AdiqAdapter
from src.db.client import supabase

logger = get_logger(__name__)

router = APIRouter(prefix="/tokenization", tags=["tokenization"])


class TokenizeCardRequest(BaseModel):
    """Request to tokenize a card"""
    pan: str = Field(..., description="Card PAN (will be tokenized immediately)")
    expiration_month: str = Field(..., pattern=r"^\d{2}$")
    expiration_year: str = Field(..., pattern=r"^\d{2}$")
    brand: str = Field(..., description="Card brand (visa, mastercard, etc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pan": "4761739001010036",
                "expiration_month": "12",
                "expiration_year": "25",
                "brand": "visa"
            }
        }


class TokenizeCardResponse(BaseModel):
    """Response with tokenized card"""
    number_token: str
    brand: str
    last4: str
    expiration_month: str
    expiration_year: str


@router.post("/cards", response_model=TokenizeCardResponse)
async def tokenize_card(
    data: TokenizeCardRequest,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Tokenize a card using merchant's Adiq credentials.
    
    ⚠️ SECURITY WARNING:
    - This endpoint receives PANs and requires PCI DSS compliance
    - PANs are immediately tokenized and never stored
    - Use HTTPS only
    - Log access for audit
    
    The merchant must have Adiq credentials configured.
    """
    logger.info(f"tokenization_request - merchant_id={merchant_id}, brand={data.brand}, last4={data.pan[-4:]}")
    
    try:
        # Get merchant credentials
        result = supabase.table("merchants").select("*").eq("id", str(merchant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant not found"
            )
        
        merchant = result.data[0]
        
        # Validate merchant has Adiq credentials
        if not merchant.get("adiq_client_id") or not merchant.get("adiq_client_secret"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Merchant does not have Adiq credentials configured"
            )
        
        # Create Adiq adapter with merchant credentials
        adiq_env = merchant.get("adiq_environment", "hml")
        base_url = "https://ecommerce.adiq.io" if adiq_env == "prd" else "https://ecommerce-hml.adiq.io"
        
        adapter = AdiqAdapter(
            client_id=merchant["adiq_client_id"],
            client_secret=merchant["adiq_client_secret"],
            seller_id=merchant["adiq_seller_id"],
            base_url=base_url
        )
        
        # Tokenize card at Adiq
        token_result = await adapter.tokenize_card(
            pan=data.pan,
            expiration_month=data.expiration_month,
            expiration_year=data.expiration_year,
            brand=data.brand
        )
        
        logger.info(f"tokenization_success - merchant_id={merchant_id}, last4={data.pan[-4:]}")
        
        return TokenizeCardResponse(
            number_token=token_result["numberToken"],
            brand=token_result["brand"],
            last4=data.pan[-4:],
            expiration_month=data.expiration_month,
            expiration_year=data.expiration_year
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"tokenization_failed - merchant_id={merchant_id}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tokenize card: {str(e)}"
        )
