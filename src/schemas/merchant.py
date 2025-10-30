"""
Merchant schemas for API requests and responses.
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field
from src.schemas.base import TimestampSchema


class MerchantRegisterAdiq(BaseModel):
    """Schema for registering a merchant in Adiq."""
    legal_name: str = Field(..., min_length=1, max_length=255, description="Legal business name")
    document_number: str = Field(..., description="CNPJ")
    mcc: str = Field(..., description="Merchant Category Code")
    
    # Banking info
    bank_code: str = Field(..., description="Bank code (3 digits)")
    agency: str = Field(..., description="Agency number")
    account: str = Field(..., description="Account number")
    account_type: str = Field(default="checking", pattern=r'^(checking|savings)$')
    
    # Contact
    email: str = Field(..., description="Contact email")
    phone: str = Field(..., description="Contact phone")
    
    # Address
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str = Field(..., min_length=2, max_length=2, description="State code (UF)")
    zip_code: str = Field(..., description="CEP")
    
    # Environment
    adiq_environment: str = Field(default="hml", pattern=r'^(hml|prd)$')


class MerchantResponse(TimestampSchema):
    """Schema for merchant response."""
    id: UUID
    name: str
    is_active: bool
    adiq_seller_id: Optional[str] = None
    adiq_environment: str
    has_adiq_credentials: bool
    webhook_url: Optional[str] = None


class MerchantUpdate(BaseModel):
    """Schema for updating merchant."""
    name: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None
