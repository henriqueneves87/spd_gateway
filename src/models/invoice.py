"""
Invoice domain model.
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Invoice:
    """Invoice entity."""
    id: UUID = field(default_factory=uuid4)
    merchant_id: UUID = None
    customer_id: UUID = None
    amount: int = 0  # in cents
    currency: str = "BRL"
    status: str = "PENDING"  # PENDING, PROCESSING, PAID, FAILED
    description: Optional[str] = None
    order_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "merchant_id": str(self.merchant_id),
            "customer_id": str(self.customer_id),
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "description": self.description,
            "order_number": self.order_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
