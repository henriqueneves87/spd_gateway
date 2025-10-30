"""
Payment API endpoints.
"""
from uuid import UUID
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from src.schemas.payment import PaymentCreate, PaymentResponse
from src.services.payment_service import PaymentService
from src.api.dependencies import get_current_merchant
from src.core.exceptions import InvoiceNotFoundError, AdiqPaymentError
from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Process a payment for an invoice.
    
    ## 🎴 Option 1: Use PAN (Recommended)
    Send the card number directly - we tokenize it automatically:
    ```json
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
    ```
    
    ## 🎴 Option 2: Use Token
    If you already have a token (generate with `python gerar_token.py`):
    ```json
    {
      "invoice_id": "2f520f49-6b64-4529-b8c1-cf586c7e73d7",
      "card_token": "YOUR-TOKEN-HERE",
      "brand": "visa",
      "cardholder_name": "JOSE DA SILVA",
      "expiration_month": "12",
      "expiration_year": "25",
      "security_code": "123",
      "installments": 1,
      "capture_type": "ac"
    }
    ```
    
    ## 🎴 Test Cards
    - **Visa:** 4761739001010036 (12/25, CVV: 123)
    - **Mastercard:** 5201561050025011 (12/25, CVV: 123)
    
    ## 📝 Fields
    - **invoice_id**: Invoice UUID (create one first at POST /v1/invoices)
    - **pan**: Card number (use this OR card_token)
    - **card_token**: Pre-tokenized card (use this OR pan)
    - **brand**: visa, mastercard, elo, amex, hipercard (required with pan)
    - **cardholder_name**: Name on card
    - **expiration_month**: MM (2 digits)
    - **expiration_year**: YY (2 digits)
    - **security_code**: CVV (3-4 digits)
    - **installments**: 1-12 (default: 1)
    - **capture_type**: "ac" (auto-capture) or "pa" (pre-auth)
    """
    service = PaymentService()
    try:
        payment = await service.process_payment(data, merchant_id, customer_data=None)
        return payment
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AdiqPaymentError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"create_payment_failed - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.get("/{transaction_id}", response_model=PaymentResponse)
async def get_payment(
    transaction_id: UUID,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Get payment details by transaction ID.
    
    - **transaction_id**: Transaction UUID
    """
    service = PaymentService()
    try:
        payment = await service.get_payment(transaction_id, merchant_id)
        return payment
    except Exception as e:
        logger.error("get_payment_failed", transaction_id=str(transaction_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment not found: {str(e)}"
        )
