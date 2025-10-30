"""
Webhook service - Process Adiq webhook notifications.
"""
from uuid import uuid4
from typing import Dict, Any
from datetime import datetime
from src.schemas.webhook import WebhookPayload, WebhookResponse
from src.core.exceptions import DuplicateWebhookError
from src.core.logger import get_logger
from src.db.client import supabase
from src.services.invoice_service import InvoiceService

logger = get_logger(__name__)


class WebhookService:
    """Service for webhook processing."""
    
    def __init__(self):
        self.invoice_service = InvoiceService()
    
    async def process_webhook(
        self,
        payload: Dict[str, Any],
        signature: str
    ) -> WebhookResponse:
        """
        Process incoming webhook from Adiq.
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            Webhook response
            
        Raises:
            DuplicateWebhookError: If webhook already processed
        """
        webhook_id = str(uuid4())
        payment_id = payload.get("paymentId")
        event_type = payload.get("eventType", "payment.status.changed")
        
        # 1. Log webhook receipt
        webhook_log = {
            "id": webhook_id,
            "event_type": event_type,
            "payment_id": payment_id,
            "payload": payload,
            "signature": signature,
            "processed": False,
            "merchant_id": None  # Será preenchido depois se encontrar a transaction
            # received_at usa default do banco (NOW())
        }
        
        try:
            supabase.table("webhook_logs").insert(webhook_log).execute()
        except Exception as e:
            logger.error("webhook_log_failed", error=str(e))
            # Continue processing even if log fails
        
        # 2. Check for duplicate
        try:
            existing = supabase.table("webhook_logs")\
                .select("id")\
                .eq("payment_id", payment_id)\
                .eq("processed", True)\
                .execute()
            
            if existing.data:
                logger.warning("duplicate_webhook", payment_id=payment_id)
                raise DuplicateWebhookError(payment_id)
        except DuplicateWebhookError:
            raise
        except Exception as e:
            logger.error("duplicate_check_failed", error=str(e))
        
        # 3. Process webhook
        try:
            # Process payment update
            await self._process_payment_update(payload)
            
            # Mark as processed
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            supabase.table("webhook_logs")\
                .update({
                    "processed": True,
                    "processed_at": now
                })\
                .eq("id", webhook_id)\
                .execute()
            
            logger.info(
                "webhook_processed",
                webhook_id=webhook_id,
                payment_id=payment_id,
                event_type=event_type
            )
            
            return WebhookResponse(
                success=True,
                message="Webhook processed successfully",
                webhook_id=webhook_id
            )
            
        except Exception as e:
            # Log error
            error_msg = str(e)
            logger.error(
                "webhook_processing_failed",
                webhook_id=webhook_id,
                payment_id=payment_id,
                error=error_msg
            )
            
            supabase.table("webhook_logs")\
                .update({"error": error_msg})\
                .eq("id", webhook_id)\
                .execute()
            
            raise
    
    async def _process_payment_update(self, payload: Dict[str, Any]) -> None:
        """
        Process payment status update from webhook.
        
        Args:
            payload: Webhook payload
        """
        payment_id = payload.get("paymentId")
        new_status = payload.get("status")
        authorization_code = payload.get("authorizationCode")
        
        if not payment_id:
            logger.warning("webhook_missing_payment_id")
            return
        
        # Find transaction by payment_id
        try:
            result = supabase.table("transactions")\
                .select("*")\
                .eq("payment_id", payment_id)\
                .execute()
            
            if not result.data:
                logger.warning(f"transaction_not_found_for_webhook - payment_id={payment_id}")
                return
            
            transaction = result.data[0]
            transaction_id = transaction["id"]
            invoice_id = transaction["invoice_id"]
            
            # Map Adiq status to internal status
            internal_status = self._map_adiq_status(new_status)
            
            # Update transaction - apenas campos básicos
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            update_data = {
                "status": internal_status,
                "updated_at": now
            }
            
            # Adicionar authorization_code se presente
            if authorization_code:
                update_data["authorization_code"] = authorization_code
            
            # Adicionar timestamps se aplicável
            if internal_status == "CAPTURED":
                update_data["captured_at"] = now
            elif internal_status == "SETTLED":
                update_data["settled_at"] = now
            
            supabase.table("transactions")\
                .update(update_data)\
                .eq("id", transaction_id)\
                .execute()
            
            # Update invoice status if needed
            if internal_status in ["CAPTURED", "SETTLED"]:
                await self.invoice_service.update_status(invoice_id, "PAID")
            elif internal_status in ["DECLINED", "CANCELLED"]:
                await self.invoice_service.update_status(invoice_id, "FAILED")
            
            logger.info(
                f"payment_updated_from_webhook - transaction_id={transaction_id}, "
                f"payment_id={payment_id}, status={internal_status}"
            )
            
        except Exception as e:
            logger.error(f"payment_update_failed - payment_id={payment_id}, error={str(e)}")
            raise
    
    def _map_adiq_status(self, adiq_status: str) -> str:
        """Map Adiq status to internal status."""
        status_map = {
            "Authorized": "AUTHORIZED",
            "Captured": "CAPTURED",
            "Settled": "SETTLED",
            "Declined": "DECLINED",
            "Cancelled": "CANCELLED",
            "Refunded": "REFUNDED"
        }
        return status_map.get(adiq_status, "CREATED")
