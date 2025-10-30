"""
Custom exceptions for the Spdpay Gateway.
All exceptions should be specific and provide clear error messages.
"""


class SpdpayException(Exception):
    """Base exception for all Spdpay Gateway errors."""
    
    def __init__(self, message: str, code: str = "SPDPAY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# Authentication & Authorization
class UnauthorizedError(SpdpayException):
    """Raised when API key is invalid or missing."""
    
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenError(SpdpayException):
    """Raised when user doesn't have permission."""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="FORBIDDEN")


# Validation
class ValidationError(SpdpayException):
    """Raised when request data is invalid."""
    
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class InvalidAmountError(ValidationError):
    """Raised when payment amount is invalid."""
    
    def __init__(self, message: str = "Invalid amount"):
        super().__init__(message)


# Business Logic
class InvalidStateTransitionError(SpdpayException):
    """Raised when trying to transition to an invalid state."""
    
    def __init__(self, from_status: str, to_status: str):
        message = f"Cannot transition from {from_status} to {to_status}"
        super().__init__(message, code="INVALID_STATE_TRANSITION")


class InvoiceNotFoundError(SpdpayException):
    """Raised when invoice is not found."""
    
    def __init__(self, invoice_id: str):
        super().__init__(f"Invoice {invoice_id} not found", code="INVOICE_NOT_FOUND")


class PaymentNotFoundError(SpdpayException):
    """Raised when payment is not found."""
    
    def __init__(self, payment_id: str):
        super().__init__(f"Payment {payment_id} not found", code="PAYMENT_NOT_FOUND")


class MerchantNotFoundError(SpdpayException):
    """Raised when merchant is not found."""
    
    def __init__(self, merchant_id: str):
        super().__init__(f"Merchant {merchant_id} not found", code="MERCHANT_NOT_FOUND")


class InvalidMerchantError(SpdpayException):
    """Raised when merchant is inactive or invalid."""
    
    def __init__(self, message: str = "Merchant is not active"):
        super().__init__(message, code="INVALID_MERCHANT")


# External Services
class AdiqError(SpdpayException):
    """Raised when Adiq API returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message, code="ADIQ_ERROR")


class AdiqAuthenticationError(AdiqError):
    """Raised when Adiq OAuth fails."""
    
    def __init__(self, message: str = "Failed to authenticate with Adiq"):
        super().__init__(message)


class AdiqPaymentError(AdiqError):
    """Raised when Adiq payment processing fails."""
    
    def __init__(self, message: str):
        super().__init__(message)


class SupabaseError(SpdpayException):
    """Raised when Supabase operation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="DATABASE_ERROR")


# Security
class PCIViolationError(SpdpayException):
    """Raised when attempting to store prohibited card data."""
    
    def __init__(self, message: str = "PCI DSS violation: Cannot store sensitive card data"):
        super().__init__(message, code="PCI_VIOLATION")


# Webhooks
class InvalidWebhookSignatureError(SpdpayException):
    """Raised when webhook signature is invalid."""
    
    def __init__(self, message: str = "Invalid webhook signature"):
        super().__init__(message, code="INVALID_WEBHOOK_SIGNATURE")


class DuplicateWebhookError(SpdpayException):
    """Raised when webhook has already been processed."""
    
    def __init__(self, webhook_id: str):
        super().__init__(f"Webhook {webhook_id} already processed", code="DUPLICATE_WEBHOOK")
