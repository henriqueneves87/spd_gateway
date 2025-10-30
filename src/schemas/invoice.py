"""
Invoice schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional
from datetime import datetime
from src.schemas.base import BaseSchema, TimestampSchema


class InvoiceBase(BaseModel):
    """Base invoice fields."""
    merchant_id: UUID = Field(..., description="Merchant UUID", example="fb93c667-fbab-47ea-b3c7-9dd27231244a")
    customer_id: UUID = Field(..., description="Customer UUID", example="3b415031-7236-425e-bc8f-35c7a5f572ab")
    amount: int = Field(..., gt=0, description="Amount in cents (1000 = R$ 10.00)", example=1000)
    currency: str = Field(default="BRL", max_length=3, description="Currency code", example="BRL")
    description: Optional[str] = Field(None, max_length=500, description="Invoice description", example="Teste de pagamento")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class InvoiceCreate(InvoiceBase):
    """
    Schema for creating a new invoice.
    
    **Example:**
    ```json
    {
      "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
      "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
      "amount": 1000,
      "currency": "BRL",
      "description": "Teste de pagamento"
    }
    ```
    
    **Fields:**
    - **merchant_id**: UUID do merchant (use: fb93c667-fbab-47ea-b3c7-9dd27231244a)
    - **customer_id**: UUID do customer (use: 3b415031-7236-425e-bc8f-35c7a5f572ab)
    - **amount**: Valor em centavos (1000 = R$ 10,00)
    - **currency**: Moeda (sempre "BRL")
    - **description**: Descrição da cobrança
    """
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
                    "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
                    "amount": 1000,
                    "currency": "BRL",
                    "description": "Teste de pagamento"
                }
            ]
        }


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None


class InvoiceResponse(InvoiceBase, TimestampSchema):
    """Schema for invoice response."""
    id: UUID
    status: str
    order_number: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseSchema):
    """Schema for list of invoices."""
    invoices: list[InvoiceResponse]
    total: int
    page: int
    page_size: int
