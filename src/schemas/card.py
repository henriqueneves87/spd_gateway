"""
Card schemas for tokenization and vault operations.
WARNING: Never store raw card data in database!
"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class CardTokenizeRequest(BaseModel):
    """
    Schema for card tokenization request.
    WARNING: This data should NEVER be stored in database.
    """
    card_number: str = Field(..., min_length=13, max_length=19)
    
    @validator('card_number')
    def validate_card_number(cls, v):
        # Remove spaces and dashes
        clean = v.replace(' ', '').replace('-', '')
        if not clean.isdigit():
            raise ValueError('Card number must contain only digits')
        return clean


class CardTokenizeResponse(BaseModel):
    """Schema for card tokenization response."""
    number_token: str = Field(..., description="Token from Adiq")


class CardVaultRequest(BaseModel):
    """
    Schema for creating card vault.
    WARNING: Sensitive data - never log this!
    """
    number_token: str
    brand: str = Field(..., max_length=20)
    cardholder_name: str = Field(..., max_length=100)
    expiration_month: str = Field(..., regex=r'^\d{2}$')
    expiration_year: str = Field(..., regex=r'^\d{2}$')
    security_code: str = Field(..., min_length=3, max_length=4)
    verify_card: bool = Field(default=True)


class CardVaultResponse(BaseModel):
    """Schema for card vault response."""
    vault_id: str
    brand: str
    last4: str
    status: str = "ACTIVE"


class CardResponse(BaseModel):
    """
    Schema for card response (safe to store/display).
    Only contains non-sensitive data.
    """
    id: str
    vault_id: str
    brand: str
    last4: str
    is_active: bool
    
    class Config:
        from_attributes = True
