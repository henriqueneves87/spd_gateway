"""
Invoice service - Business logic for invoice management.
"""
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from src.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from src.core.exceptions import InvoiceNotFoundError, InvalidStateTransitionError
from src.core.state_machine import validate_invoice_transition
from src.core.logger import get_logger
from src.db.client import supabase

logger = get_logger(__name__)


class InvoiceService:
    """Service for invoice operations."""
    
    async def create(self, data: InvoiceCreate, merchant_id: UUID) -> InvoiceResponse:
        """
        Create a new invoice.
        
        Args:
            data: Invoice creation data
            merchant_id: Merchant ID from API key
            
        Returns:
            Created invoice
        """
        invoice_data = {
            "merchant_id": str(merchant_id),
            "customer_id": str(data.customer_id),
            "amount": data.amount,
            "currency": data.currency,
            "description": data.description,
            "status": "PENDING"
        }
        
        try:
            result = supabase.table("invoices").insert(invoice_data).execute()
            invoice = result.data[0]
            
            logger.info(f"invoice_created - invoice_id={invoice['id']}, merchant_id={str(merchant_id)}, amount={invoice['amount']}")
            
            return InvoiceResponse(**invoice)
            
        except Exception as e:
            logger.error(f"invoice_creation_failed - error={str(e)}")
            raise
    
    async def get(self, invoice_id: UUID, merchant_id: UUID) -> InvoiceResponse:
        """
        Get invoice by ID.
        
        Args:
            invoice_id: Invoice ID
            merchant_id: Merchant ID (for authorization)
            
        Returns:
            Invoice data
            
        Raises:
            InvoiceNotFoundError: If invoice not found
        """
        try:
            result = supabase.table("invoices")\
                .select("*")\
                .eq("id", str(invoice_id))\
                .eq("merchant_id", str(merchant_id))\
                .execute()
            
            if not result.data:
                raise InvoiceNotFoundError(str(invoice_id))
            
            return InvoiceResponse(**result.data[0])
            
        except InvoiceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"invoice_get_failed - invoice_id={str(invoice_id)}, error={str(e)}")
            raise
    
    async def list(
        self,
        merchant_id: UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[InvoiceResponse]:
        """
        List invoices for a merchant.
        
        Args:
            merchant_id: Merchant ID
            status: Optional status filter
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of invoices
        """
        try:
            query = supabase.table("invoices")\
                .select("*")\
                .eq("merchant_id", str(merchant_id))\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)
            
            if status:
                query = query.eq("status", status)
            
            result = query.execute()
            
            return [InvoiceResponse(**invoice) for invoice in result.data]
            
        except Exception as e:
            logger.error(f"invoice_list_failed - merchant_id={str(merchant_id)}, error={str(e)}")
            raise
    
    async def update_status(
        self,
        invoice_id: UUID,
        new_status: str,
        merchant_id: Optional[UUID] = None
    ) -> InvoiceResponse:
        """
        Update invoice status with state machine validation.
        
        Args:
            invoice_id: Invoice ID
            new_status: New status
            merchant_id: Optional merchant ID for authorization
            
        Returns:
            Updated invoice
            
        Raises:
            InvoiceNotFoundError: If invoice not found
            InvalidStateTransitionError: If transition is invalid
        """
        # Get current invoice
        query = supabase.table("invoices")\
            .select("*")\
            .eq("id", str(invoice_id))
        
        if merchant_id:
            query = query.eq("merchant_id", str(merchant_id))
        
        result = query.execute()
        
        if not result.data:
            raise InvoiceNotFoundError(str(invoice_id))
        
        invoice = result.data[0]
        current_status = invoice["status"]
        
        # Validate state transition
        validate_invoice_transition(current_status, new_status)
        
        # Update status
        try:
            update_data = {
                "status": new_status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("invoices")\
                .update(update_data)\
                .eq("id", str(invoice_id))\
                .execute()
            
            logger.info(f"invoice_status_updated - invoice_id={str(invoice_id)}, from_status={current_status}, to_status={new_status}")
            
            return InvoiceResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"invoice_status_update_failed - invoice_id={str(invoice_id)}, error={str(e)}")
            raise
