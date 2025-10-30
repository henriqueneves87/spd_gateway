"""
Webhook schemas for Adiq notifications.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WebhookPayload(BaseModel):
    """Schema for incoming webhook payload."""
    event_type: str
    payment_id: str
    authorization_code: Optional[str] = None
    status: str
    amount: int
    timestamp: datetime
    nsu: Optional[str] = None
    tid: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Schema for webhook response."""
    success: bool = True
    message: str = "Webhook processed successfully"
    webhook_id: Optional[str] = None


class WebhookLog(BaseModel):
    """Schema for webhook log."""
    id: str
    merchant_id: str
    event_type: str
    payment_id: str
    payload: Dict[str, Any]
    signature: str
    processed: bool = False
    processed_at: Optional[datetime] = None
    error: Optional[str] = None
    received_at: datetime
    
    class Config:
        from_attributes = True
