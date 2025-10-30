"""
Merchant domain model.
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Merchant:
    """Merchant entity with Adiq credentials."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    api_key_hash: str = ""
    is_active: bool = True
    
    # Adiq credentials (per merchant)
    adiq_seller_id: Optional[str] = None
    adiq_client_id: Optional[str] = None
    adiq_client_secret: Optional[str] = None
    adiq_environment: str = "hml"
    
    # Banking info
    bank_code: Optional[str] = None
    agency: Optional[str] = None
    account: Optional[str] = None
    
    # Webhook
    webhook_url: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "id": str(self.id),
            "name": self.name,
            "is_active": self.is_active,
            "adiq_seller_id": self.adiq_seller_id,
            "adiq_environment": self.adiq_environment,
            "has_adiq_credentials": bool(self.adiq_client_id and self.adiq_client_secret),
            "webhook_url": self.webhook_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
