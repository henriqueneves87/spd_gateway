"""
Invoice API endpoints.
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceListResponse
from src.services.invoice_service import InvoiceService
from src.api.dependencies import get_current_merchant
from src.core.exceptions import InvoiceNotFoundError
from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Create a new invoice for payment.
    
    ## 📝 Example Request
    ```json
    {
      "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
      "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
      "amount": 1000,
      "currency": "BRL",
      "description": "Teste de pagamento"
    }
    ```
    
    ## 📊 Fields
    - **merchant_id**: UUID do merchant (use: `fb93c667-fbab-47ea-b3c7-9dd27231244a`)
    - **customer_id**: UUID do customer (use: `3b415031-7236-425e-bc8f-35c7a5f572ab`)
    - **amount**: Valor em centavos (1000 = R$ 10,00)
    - **currency**: Moeda (sempre "BRL")
    - **description**: Descrição da cobrança (opcional)
    
    ## 💡 Importante
    - O valor é em **centavos**: 1000 = R$ 10,00
    - Cada invoice pode ser paga apenas **uma vez**
    - Após criar, use o `id` retornado para processar o pagamento
    
    ## 🔄 Próximo Passo
    Após criar a invoice, use o `id` retornado no endpoint `POST /v1/payments/`
    """
    service = InvoiceService()
    try:
        invoice = await service.create(data, merchant_id)
        return invoice
    except Exception as e:
        logger.error(f"create_invoice_failed - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Get invoice by ID.
    
    - **invoice_id**: Invoice UUID
    """
    service = InvoiceService()
    try:
        invoice = await service.get(invoice_id, merchant_id)
        return invoice
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"get_invoice_failed - invoice_id={str(invoice_id)}, error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice: {str(e)}"
        )


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    merchant_id: UUID = Depends(get_current_merchant),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    List invoices for the authenticated merchant.
    
    - **status**: Optional status filter (PENDING, PROCESSING, PAID, FAILED)
    - **limit**: Maximum number of results (1-100)
    - **offset**: Pagination offset
    """
    service = InvoiceService()
    try:
        invoices = await service.list(merchant_id, status, limit, offset)
        return invoices
    except Exception as e:
        logger.error(f"list_invoices_failed - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invoices: {str(e)}"
        )
