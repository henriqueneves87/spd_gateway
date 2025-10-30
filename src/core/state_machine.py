"""
State machine for Invoice and Transaction status transitions.
Ensures only valid state transitions are allowed.
"""
from enum import Enum
from typing import Dict, List
from src.core.exceptions import InvalidStateTransitionError


class InvoiceStatus(str, Enum):
    """Allowed invoice statuses."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"


class TransactionStatus(str, Enum):
    """Allowed transaction statuses."""
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLED = "SETTLED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


# Allowed state transitions
INVOICE_TRANSITIONS: Dict[InvoiceStatus, List[InvoiceStatus]] = {
    InvoiceStatus.PENDING: [InvoiceStatus.PROCESSING],
    InvoiceStatus.PROCESSING: [InvoiceStatus.PAID, InvoiceStatus.FAILED],
    InvoiceStatus.PAID: [],  # Final state
    InvoiceStatus.FAILED: [],  # Final state
}

TRANSACTION_TRANSITIONS: Dict[TransactionStatus, List[TransactionStatus]] = {
    TransactionStatus.CREATED: [TransactionStatus.AUTHORIZED, TransactionStatus.DECLINED],
    TransactionStatus.AUTHORIZED: [TransactionStatus.CAPTURED, TransactionStatus.CANCELLED],
    TransactionStatus.CAPTURED: [TransactionStatus.SETTLED, TransactionStatus.REFUNDED],
    TransactionStatus.SETTLED: [TransactionStatus.REFUNDED],  # Can refund settled transactions
    TransactionStatus.DECLINED: [],  # Final state
    TransactionStatus.CANCELLED: [],  # Final state
    TransactionStatus.REFUNDED: [],  # Final state
}


def can_transition_invoice(from_status: InvoiceStatus, to_status: InvoiceStatus) -> bool:
    """
    Check if invoice can transition from one status to another.
    
    Args:
        from_status: Current invoice status
        to_status: Desired invoice status
        
    Returns:
        True if transition is allowed, False otherwise
    """
    allowed_transitions = INVOICE_TRANSITIONS.get(from_status, [])
    return to_status in allowed_transitions


def can_transition_transaction(from_status: TransactionStatus, to_status: TransactionStatus) -> bool:
    """
    Check if transaction can transition from one status to another.
    
    Args:
        from_status: Current transaction status
        to_status: Desired transaction status
        
    Returns:
        True if transition is allowed, False otherwise
    """
    allowed_transitions = TRANSACTION_TRANSITIONS.get(from_status, [])
    return to_status in allowed_transitions


def validate_invoice_transition(from_status: str, to_status: str) -> None:
    """
    Validate invoice status transition and raise exception if invalid.
    
    Args:
        from_status: Current invoice status
        to_status: Desired invoice status
        
    Raises:
        InvalidStateTransitionError: If transition is not allowed
    """
    try:
        from_enum = InvoiceStatus(from_status)
        to_enum = InvoiceStatus(to_status)
    except ValueError as e:
        raise InvalidStateTransitionError(from_status, to_status) from e
    
    if not can_transition_invoice(from_enum, to_enum):
        raise InvalidStateTransitionError(from_status, to_status)


def validate_transaction_transition(from_status: str, to_status: str) -> None:
    """
    Validate transaction status transition and raise exception if invalid.
    
    Args:
        from_status: Current transaction status
        to_status: Desired transaction status
        
    Raises:
        InvalidStateTransitionError: If transition is not allowed
    """
    try:
        from_enum = TransactionStatus(from_status)
        to_enum = TransactionStatus(to_status)
    except ValueError as e:
        raise InvalidStateTransitionError(from_status, to_status) from e
    
    if not can_transition_transaction(from_enum, to_enum):
        raise InvalidStateTransitionError(from_status, to_status)


def get_invoice_next_states(current_status: str) -> List[str]:
    """
    Get list of allowed next states for an invoice.
    
    Args:
        current_status: Current invoice status
        
    Returns:
        List of allowed next statuses
    """
    try:
        status_enum = InvoiceStatus(current_status)
        return [s.value for s in INVOICE_TRANSITIONS.get(status_enum, [])]
    except ValueError:
        return []


def get_transaction_next_states(current_status: str) -> List[str]:
    """
    Get list of allowed next states for a transaction.
    
    Args:
        current_status: Current transaction status
        
    Returns:
        List of allowed next statuses
    """
    try:
        status_enum = TransactionStatus(current_status)
        return [s.value for s in TRANSACTION_TRANSITIONS.get(status_enum, [])]
    except ValueError:
        return []
