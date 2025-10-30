"""
Webhook API endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Header, Request
from src.schemas.webhook import WebhookResponse
from src.services.webhook_service import WebhookService
from src.core.exceptions import DuplicateWebhookError
from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/adiq", response_model=WebhookResponse)
async def adiq_webhook(
    request: Request,
    x_webhook_signature: str = Header(None, description="Webhook signature")
):
    """
    Receive webhook notifications from Adiq.
    
    This endpoint processes payment status updates from Adiq.
    
    **Webhook Events:**
    - payment.authorized
    - payment.captured
    - payment.settled
    - payment.declined
    - payment.cancelled
    - payment.refunded
    """
    service = WebhookService()
    
    try:
        # Get raw body
        body = await request.body()
        payload = await request.json()
        
        # TODO: Validate signature
        # validate_webhook_signature(body, x_webhook_signature, webhook_secret)
        
        # Process webhook
        response = await service.process_webhook(payload, x_webhook_signature or "")
        return response
        
    except DuplicateWebhookError as e:
        # Return 200 for duplicates (already processed)
        logger.info("duplicate_webhook_received", detail=str(e))
        return WebhookResponse(
            success=True,
            message="Webhook already processed"
        )
    except Exception as e:
        logger.error(f"webhook_processing_failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )
