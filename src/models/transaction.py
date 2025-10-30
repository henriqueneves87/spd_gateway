"""
Transaction domain model.
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Transaction:
    """Transaction entity."""
    id: UUID = field(default_factory=uuid4)
    invoice_id: UUID = None
    merchant_id: UUID = None
    
    # Adiq IDs
    payment_id: Optional[str] = None  # Adiq payment ID
    authorization_code: Optional[str] = None
    nsu: Optional[str] = None
    tid: Optional[str] = None
    
    # Payment details
    amount: int = 0  # in cents
    currency: str = "BRL"
    installments: int = 1
    
    # Card info (safe - no sensitive data)
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    
    # Status
    status: str = "CREATED"  # CREATED, AUTHORIZED, CAPTURED, SETTLED, DECLINED, CANCELLED
    
    # 3DS
    eci: Optional[str] = None
    cavv: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    authorized_at: Optional[datetime] = None
    captured_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "invoice_id": str(self.invoice_id),
            "merchant_id": str(self.merchant_id),
            "payment_id": self.payment_id,
            "authorization_code": self.authorization_code,
            "nsu": self.nsu,
            "tid": self.tid,
            "amount": self.amount,
            "currency": self.currency,
            "installments": self.installments,
            "card_brand": self.card_brand,
            "card_last4": self.card_last4,
            "status": self.status,
            "eci": self.eci,
            "cavv": self.cavv,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "authorized_at": self.authorized_at.isoformat() if self.authorized_at else None,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "settled_at": self.settled_at.isoformat() if self.settled_at else None
        }
