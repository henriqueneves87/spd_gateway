"""
Payment service - Business logic for payment processing.
"""
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from datetime import datetime
from src.schemas.payment import PaymentCreate, PaymentResponse
from src.core.exceptions import InvoiceNotFoundError, InvalidStateTransitionError, AdiqPaymentError
from src.core.logger import get_logger
from src.adapters.adiq import AdiqAdapter
from src.db.client import supabase
from src.services.invoice_service import InvoiceService

logger = get_logger(__name__)


class PaymentService:
    """Service for payment operations with per-merchant Adiq credentials."""
    
    def __init__(self):
        self.invoice_service = InvoiceService()
    
    async def _get_merchant_adiq_adapter(self, merchant_id: UUID) -> AdiqAdapter:
        """
        Get AdiqAdapter with merchant-specific credentials.
        REQUIRES merchant to have Adiq credentials configured.
        
        Args:
            merchant_id: Merchant ID
            
        Returns:
            Configured AdiqAdapter
            
        Raises:
            HTTPException: If merchant not found or missing Adiq credentials
        """
        from fastapi import HTTPException, status
        
        # Fetch merchant from database
        result = supabase.table("merchants").select("*").eq("id", str(merchant_id)).execute()
        
        if not result.data:
            logger.error(f"merchant_not_found - merchant_id={merchant_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant não encontrado"
            )
        
        merchant = result.data[0]
        
        # Get merchant credentials
        client_id = merchant.get("adiq_client_id")
        client_secret = merchant.get("adiq_client_secret")
        seller_id = merchant.get("adiq_seller_id")
        
        # VALIDATE: Merchant MUST have Adiq credentials
        if not client_id or not client_secret or not seller_id:
            logger.error(
                f"merchant_missing_adiq_credentials - merchant_id={merchant_id}, "
                f"has_client_id={bool(client_id)}, has_client_secret={bool(client_secret)}, "
                f"has_seller_id={bool(seller_id)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Merchant não possui credenciais da Adiq configuradas. "
                    "Registre-se via POST /v1/merchants/register-adiq antes de processar pagamentos."
                )
            )
        
        # Determine base URL based on merchant environment
        adiq_env = merchant.get("adiq_environment", "hml")
        base_url = "https://ecommerce.adiq.io" if adiq_env == "prd" else "https://ecommerce-hml.adiq.io"
        
        logger.info(
            f"creating_adiq_adapter - merchant_id={merchant_id}, "
            f"seller_id={seller_id}, env={adiq_env}"
        )
        
        # Create adapter with REQUIRED credentials
        return AdiqAdapter(
            client_id=client_id,
            client_secret=client_secret,
            seller_id=seller_id,
            base_url=base_url
        )
    
    async def process_payment(
        self,
        data: PaymentCreate,
        merchant_id: UUID,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> PaymentResponse:
        """
        Process a payment through Adiq using merchant-specific credentials.
        
        Args:
            data: Payment creation data
            merchant_id: Merchant ID
            customer_data: Optional customer data for antifraud
            
        Returns:
            Payment response
            
        Raises:
            InvoiceNotFoundError: If invoice not found
            AdiqPaymentError: If payment fails
        """
        # 1. Get AdiqAdapter with merchant credentials
        adiq = await self._get_merchant_adiq_adapter(merchant_id)
        
        # 2. Get and validate invoice
        invoice = await self.invoice_service.get(data.invoice_id, merchant_id)
        
        if invoice.status != "PENDING":
            raise InvalidStateTransitionError(invoice.status, "PROCESSING")
        
        # 2. Update invoice to PROCESSING
        await self.invoice_service.update_status(data.invoice_id, "PROCESSING")
        
        # 3. Create transaction record
        transaction_id = uuid4()
        transaction_data = {
            "id": str(transaction_id),
            "invoice_id": str(data.invoice_id),
            "merchant_id": str(merchant_id),
            "amount": invoice.amount,
            "currency": invoice.currency,
            "installments": data.installments,
            "status": "CREATED"
        }
        
        try:
            supabase.table("transactions").insert(transaction_data).execute()
        except Exception as e:
            logger.error(f"transaction_creation_failed - error={str(e)}")
            raise
        
        # 4. Tokenize card if PAN was provided
        card_token = data.card_token
        if data.pan:
            logger.info(f"tokenizing_pan - merchant_id={merchant_id}, last4={data.pan[-4:]}")
            try:
                token_result = await adiq.tokenize_card(
                    pan=data.pan,
                    expiration_month=data.expiration_month,
                    expiration_year=data.expiration_year,
                    brand=data.brand
                )
                card_token = token_result['numberToken']
                logger.info(f"pan_tokenized - token={card_token[:10]}...")
            except Exception as e:
                logger.error(f"tokenization_failed - error={str(e)}")
                await self.invoice_service.update_status(data.invoice_id, "FAILED")
                raise AdiqPaymentError(f"Failed to tokenize card: {str(e)}")
        
        # 5. Process payment with Adiq
        try:
            # Generate unique order number (max 13 chars)
            import time
            order_number = f"{int(time.time() * 1000) % 10000000000000}"  # 13 dígitos
            
            # Prepare customer data for antifraud (obrigatório para contas com antifraude)
            if customer_data:
                adiq_customer = {
                    "documentType": customer_data.get("document_type", "cpf"),
                    "documentNumber": customer_data.get("document_number"),
                    "firstName": customer_data.get("first_name"),
                    "lastName": customer_data.get("last_name"),
                    "email": customer_data.get("email"),
                    "phoneNumber": customer_data.get("phone")
                }
            else:
                # Dados dummy para testes (antifraude obrigatório)
                adiq_customer = {
                    "documentType": "cpf",
                    "documentNumber": "12345678909",
                    "firstName": "Jose",
                    "lastName": "Silva",
                    "email": "accept@test.com",  # Email de teste que aprova
                    "phoneNumber": "1122334455",
                    "mobilePhoneNumber": "11999999999",
                    "address": "Rua Teste",
                    "addressNumber": "123",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zipCode": "01310100",
                    "country": "BR",
                    "ipAddress": "127.0.0.1"
                }
            
            # Call Adiq with merchant-specific adapter
            payment_result = await adiq.create_payment(
                amount=invoice.amount,
                number_token=card_token,  # Use tokenized card
                brand=data.brand or "visa",  # Use provided brand or default
                cardholder_name=data.cardholder_name,
                expiration_month=data.expiration_month,
                expiration_year=data.expiration_year,
                security_code=data.security_code,
                order_number=order_number,
                installments=data.installments,
                capture_type=data.capture_type,
                customer=adiq_customer
            )
            
            # 5. Update transaction with Adiq response
            # A resposta vem dentro de paymentAuthorization
            payment_auth = payment_result.get("paymentAuthorization", {})
            adiq_status = payment_auth.get("returnCode", "")
            
            # Se tem authorization code, foi aprovado
            # Verificar se é auto-captura (ac) ou pré-auth (pa)
            if payment_auth.get("authorizationCode"):
                if data.capture_type == "ac":
                    transaction_status = "CAPTURED"  # Auto-captura = já capturado
                else:
                    transaction_status = "AUTHORIZED"  # Pré-auth = apenas autorizado
            else:
                transaction_status = self._map_adiq_status(adiq_status)
            
            update_data = {
                "payment_id": payment_auth.get("paymentId"),
                "authorization_code": payment_auth.get("authorizationCode"),
                "nsu": payment_auth.get("nsu"),
                "tid": payment_auth.get("paymentId"),  # TID é o paymentId
                "status": transaction_status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if transaction_status == "AUTHORIZED":
                update_data["authorized_at"] = datetime.utcnow().isoformat()
            elif transaction_status == "CAPTURED":
                update_data["captured_at"] = datetime.utcnow().isoformat()
            
            supabase.table("transactions")\
                .update(update_data)\
                .eq("id", str(transaction_id))\
                .execute()
            
            # 6. Update invoice status based on payment result
            if transaction_status in ["CAPTURED", "AUTHORIZED"]:
                await self.invoice_service.update_status(data.invoice_id, "PAID")
            else:
                await self.invoice_service.update_status(data.invoice_id, "FAILED")
            
            # 7. Return payment response
            return PaymentResponse(
                id=transaction_id,
                invoice_id=data.invoice_id,
                transaction_id=transaction_id,
                status=transaction_status,
                amount=invoice.amount,
                installments=data.installments,
                authorization_code=payment_auth.get("authorizationCode"),
                payment_id=payment_auth.get("paymentId"),
                nsu=payment_auth.get("nsu"),
                tid=payment_auth.get("paymentId"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            # Payment failed - update statuses
            logger.error(
                f"payment_processing_failed - transaction_id={str(transaction_id)}, "
                f"invoice_id={str(data.invoice_id)}, error={str(e)}"
            )
            
            # Update transaction to DECLINED
            supabase.table("transactions")\
                .update({"status": "DECLINED", "updated_at": datetime.utcnow().isoformat()})\
                .eq("id", str(transaction_id))\
                .execute()
            
            # Update invoice to FAILED
            await self.invoice_service.update_status(data.invoice_id, "FAILED")
            
            raise
    
    def _map_adiq_status(self, adiq_status: str) -> str:
        """
        Map Adiq status to internal transaction status.
        
        Args:
            adiq_status: Status from Adiq
            
        Returns:
            Internal transaction status
        """
        status_map = {
            "Authorized": "AUTHORIZED",
            "Captured": "CAPTURED",
            "Settled": "SETTLED",
            "Declined": "DECLINED",
            "Cancelled": "CANCELLED",
            "Refunded": "REFUNDED"
        }
        
        return status_map.get(adiq_status, "CREATED")
    
    async def get_payment(self, transaction_id: UUID, merchant_id: UUID) -> PaymentResponse:
        """
        Get payment by transaction ID.
        
        Args:
            transaction_id: Transaction ID
            merchant_id: Merchant ID
            
        Returns:
            Payment response
        """
        try:
            result = supabase.table("transactions")\
                .select("*")\
                .eq("id", str(transaction_id))\
                .eq("merchant_id", str(merchant_id))\
                .execute()
            
            if not result.data:
                raise Exception("Transaction not found")
            
            transaction = result.data[0]
            
            return PaymentResponse(
                id=UUID(transaction["id"]),
                invoice_id=UUID(transaction["invoice_id"]),
                transaction_id=UUID(transaction["id"]),
                status=transaction["status"],
                amount=transaction["amount"],
                installments=transaction["installments"],
                authorization_code=transaction.get("authorization_code"),
                payment_id=transaction.get("payment_id"),
                nsu=transaction.get("nsu"),
                tid=transaction.get("tid"),
                created_at=datetime.fromisoformat(transaction["created_at"]),
                updated_at=datetime.fromisoformat(transaction["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"get_payment_failed - transaction_id={str(transaction_id)}, error={str(e)}")
            raise
