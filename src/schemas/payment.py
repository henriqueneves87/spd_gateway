"""
Payment schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional
from datetime import datetime
from src.schemas.base import BaseSchema, TimestampSchema


class PaymentCreate(BaseModel):
    """
    Schema for creating a payment.
    
    **Option 1: Use PAN (Recommended)**
    Send the card number directly and we tokenize it automatically:
    ```json
    {
      "invoice_id": "uuid",
      "pan": "4761739001010036",
      "brand": "visa",
      "cardholder_name": "JOSE DA SILVA",
      "expiration_month": "12",
      "expiration_year": "25",
      "security_code": "123",
      "installments": 1,
      "capture_type": "ac"
    }
    ```
    
    **Option 2: Use Pre-generated Token**
    If you already have a token from Adiq:
    ```json
    {
      "invoice_id": "uuid",
      "card_token": "TOKEN-FROM-ADIQ",
      "brand": "visa",
      "cardholder_name": "JOSE DA SILVA",
      "expiration_month": "12",
      "expiration_year": "25",
      "security_code": "123",
      "installments": 1,
      "capture_type": "ac"
    }
    ```
    """
    invoice_id: UUID = Field(..., description="Invoice UUID to pay")
    
    # Option 1: Pre-tokenized card
    card_token: Optional[str] = Field(None, description="Pre-tokenized card from Adiq (use this OR pan)")
    
    # Option 2: PAN (we tokenize it)
    pan: Optional[str] = Field(None, description="Card PAN - will be tokenized automatically (use this OR card_token)", example="4761739001010036")
    brand: Optional[str] = Field(None, description="Card brand: visa, mastercard, elo, amex, hipercard (required if using PAN)", example="visa")
    
    # Common fields
    cardholder_name: str = Field(..., max_length=100, description="Name on card", example="JOSE DA SILVA")
    expiration_month: str = Field(..., pattern=r'^\d{2}$', description="Expiration month (MM)", example="12")
    expiration_year: str = Field(..., pattern=r'^\d{2}$', description="Expiration year (YY)", example="25")
    security_code: str = Field(..., min_length=3, max_length=4, description="CVV (3-4 digits)", example="123")
    installments: int = Field(default=1, ge=1, le=12, description="Number of installments (1-12)", example=1)
    capture_type: str = Field(default="ac", pattern=r'^(ac|pa)$', description="ac=auto-capture, pa=pre-auth", example="ac")
    
    @validator('pan')
    def validate_pan_or_token(cls, v, values):
        """Validate that either pan or card_token is provided."""
        card_token = values.get('card_token')
        if not v and not card_token:
            raise ValueError('Either pan or card_token must be provided')
        if v and card_token:
            raise ValueError('Provide either pan or card_token, not both')
        return v
    
    @validator('brand')
    def validate_brand_with_pan(cls, v, values):
        """Validate that brand is provided when using PAN."""
        pan = values.get('pan')
        if pan and not v:
            raise ValueError('brand is required when using pan')
        return v
    
    @validator('installments')
    def validate_installments(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Installments must be between 1 and 12')
        return v
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "invoice_id": "2f520f49-6b64-4529-b8c1-cf586c7e73d7",
                    "pan": "4761739001010036",
                    "brand": "visa",
                    "cardholder_name": "JOSE DA SILVA",
                    "expiration_month": "12",
                    "expiration_year": "25",
                    "security_code": "123",
                    "installments": 1,
                    "capture_type": "ac"
                }
            ]
        }


class PaymentResponse(TimestampSchema):
    """Schema for payment response."""
    id: UUID
    invoice_id: UUID
    transaction_id: UUID
    status: str
    amount: int
    installments: int
    authorization_code: Optional[str] = None
    payment_id: Optional[str] = None  # Adiq payment ID
    nsu: Optional[str] = None
    tid: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentStatusUpdate(BaseModel):
    """Schema for updating payment status."""
    status: str
    authorization_code: Optional[str] = None
    payment_id: Optional[str] = None
