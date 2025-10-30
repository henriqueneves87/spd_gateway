"""
Adiq API adapter for payment processing.
Handles OAuth2, tokenization, vault, and payments.
"""
import httpx
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.core.config import settings
from src.core.logger import get_logger, sanitize_data
from src.core.exceptions import AdiqError, AdiqAuthenticationError, AdiqPaymentError

logger = get_logger(__name__)


class AdiqAdapter:
    """Adapter for Adiq Gateway API with per-merchant credentials support."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        seller_id: str,
        base_url: Optional[str] = None
    ):
        """
        Initialize Adiq adapter with MANDATORY merchant credentials.
        
        Args:
            client_id: Merchant-specific client ID (REQUIRED)
            client_secret: Merchant-specific client secret (REQUIRED)
            seller_id: Merchant's seller ID in Adiq (REQUIRED)
            base_url: Adiq base URL (optional, defaults to HML)
            
        Raises:
            ValueError: If any required credential is missing
        """
        # Validate required credentials
        if not client_id or not client_secret or not seller_id:
            raise ValueError(
                "Credenciais Adiq obrigatórias ausentes. "
                "Merchant deve possuir client_id, client_secret e seller_id."
            )
        
        self.base_url = base_url or "https://ecommerce-hml.adiq.io"
        self.client_id = client_id
        self.client_secret = client_secret
        self.seller_id = seller_id
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        logger.info(f"AdiqAdapter initialized - seller_id={seller_id}, base_url={self.base_url}")
    
    def _get_basic_auth(self) -> str:
        """Get Basic Auth header for OAuth."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def tokenize_card(
        self,
        pan: str,
        expiration_month: str,
        expiration_year: str,
        brand: str
    ) -> Dict[str, Any]:
        """
        Tokenize a card at Adiq.
        
        Args:
            pan: Card PAN (Primary Account Number)
            expiration_month: Expiration month (MM)
            expiration_year: Expiration year (YY)
            brand: Card brand (visa, mastercard, etc)
            
        Returns:
            Dict with numberToken, brand, last4
            
        Raises:
            AdiqError: If tokenization fails
        """
        await self._ensure_authenticated()
        
        url = f"{self.base_url}/v1/tokens/cards"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "cardNumber": pan  # Adiq espera apenas cardNumber
        }
        
        try:
            logger.info(f"tokenizing_card - brand={brand}, last4={pan[-4:]}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"card_tokenized - token={result.get('numberToken')[:10]}..., last4={pan[-4:]}")
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"tokenization_failed - status={e.response.status_code}, error={e.response.text}")
            raise AdiqError(f"Failed to tokenize card: {e.response.text}")
        except Exception as e:
            logger.error(f"tokenization_error - error={str(e)}")
            raise AdiqError(f"Tokenization error: {str(e)}")
    
    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if self.access_token and self.token_expires_at:
            if datetime.utcnow() < self.token_expires_at:
                return  # Token still valid
        
        await self.authenticate()
    
    async def authenticate(self) -> str:
        """
        Authenticate with Adiq using OAuth2 client credentials.
        
        Returns:
            Access token
            
        Raises:
            AdiqAuthenticationError: If authentication fails
        """
        url = f"{self.base_url}/auth/oauth2/v1/token"
        headers = {
            "Authorization": self._get_basic_auth(),
            "Content-Type": "application/json"
        }
        payload = {"grantType": "client_credentials"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                self.access_token = data["accessToken"]  # Adiq usa camelCase
                expires_in = int(data.get("expiresIn", 3600))  # Adiq usa camelCase, converter para int
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                
                logger.info(f"adiq_authenticated - expires_in={expires_in}")
                return self.access_token
                
        except httpx.HTTPStatusError as e:
            logger.error(f"adiq_auth_failed - status_code={e.response.status_code}, error={str(e)}")
            raise AdiqAuthenticationError(f"Authentication failed: {e}")
        except Exception as e:
            logger.error(f"adiq_auth_error - error={str(e)}")
            raise AdiqAuthenticationError(f"Authentication error: {e}")
    
    async def create_vault(
        self,
        number_token: str,
        brand: str,
        cardholder_name: str,
        expiration_month: str,
        expiration_year: str,
        security_code: str,
        verify_card: bool = True
    ) -> Dict[str, Any]:
        """
        Create card vault in Adiq.
        
        Args:
            number_token: Token from tokenize_card
            brand: Card brand (visa, mastercard, etc)
            cardholder_name: Name on card
            expiration_month: MM
            expiration_year: YY
            security_code: CVV
            verify_card: Whether to verify card
            
        Returns:
            Vault data with vaultId, brand, last4
            
        Raises:
            AdiqError: If vault creation fails
        """
        await self._ensure_authenticated()
        
        url = f"{self.base_url}/v1/vaults/cards"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "numberToken": number_token,
            "brand": brand,
            "cardholderName": cardholder_name,
            "expirationMonth": expiration_month,
            "expirationYear": expiration_year,
            "securityCode": security_code,
            "verifyCard": verify_card
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"vault_created - vault_id={data['vaultId']}, brand={data['brand']}, last4={data['last4']}")
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"vault_creation_failed - status_code={e.response.status_code}")
            raise AdiqError(f"Vault creation failed: {e}", status_code=e.response.status_code)
        except Exception as e:
            logger.error(f"vault_creation_error - error={str(e)}")
            raise AdiqError(f"Vault creation error: {e}")
    
    async def create_payment(
        self,
        amount: int,
        number_token: str,
        brand: str,
        cardholder_name: str,
        expiration_month: str,
        expiration_year: str,
        security_code: str,
        order_number: str,
        installments: int = 1,
        capture_type: str = "ac",
        soft_descriptor: str = "PAG*SPDPAY",
        customer: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment in Adiq.
        
        Args:
            amount: Amount in cents
            number_token: Tokenized card
            brand: Card brand
            cardholder_name: Name on card
            expiration_month: MM
            expiration_year: YY
            security_code: CVV
            order_number: Unique order number
            installments: Number of installments (1-12)
            capture_type: "ac" (auto-capture) or "pa" (pre-auth)
            soft_descriptor: Descriptor on card statement
            customer: Customer data (for antifraud)
            device_info: Device info (for 3DS)
            
        Returns:
            Payment data with paymentId, authorizationCode, status
            
        Raises:
            AdiqPaymentError: If payment fails
        """
        await self._ensure_authenticated()
        
        url = f"{self.base_url}/v1/payments"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        product_type = "avista" if installments == 1 else "lojista"
        
        payload = {
            "payment": {
                "transactionType": "credit",
                "amount": amount,
                "currencyCode": "brl",
                "productType": product_type,
                "installments": installments,
                "captureType": capture_type,
                "recurrent": False
            },
            "cardInfo": {
                "numberToken": number_token,
                "brand": brand,
                "cardholderName": cardholder_name,
                "expirationMonth": expiration_month,
                "expirationYear": expiration_year,
                "securityCode": security_code
            },
            "sellerInfo": {
                "orderNumber": order_number,
                "softDescriptor": soft_descriptor,
                "codeAntiFraud": "00000000-0000-0000-0000-000000000000"  # Dummy para testes
            }
        }
        
        # Add seller ID if merchant has one (subcredenciadora model)
        if self.seller_id:
            payload["sellerInfo"]["id"] = self.seller_id
            logger.info(f"payment_with_seller_id - seller_id={self.seller_id}")
        
        if customer:
            payload["customer"] = customer
        
        if device_info:
            payload["deviceInfo"] = device_info
        
        try:
            # Sanitize payload for logging (remove sensitive data)
            safe_payload = sanitize_data(payload)
            logger.info(f"creating_payment - order_number={order_number}, amount={amount}, installments={installments}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=90.0)  # Aumentado para 90s
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"payment_created - payment_id={data.get('paymentId')}, authorization_code={data.get('authorizationCode')}, status={data.get('status')}")
                return data
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"payment_failed - status_code={e.response.status_code}, error={error_detail}")
            raise AdiqPaymentError(f"Payment failed: {error_detail}")
        except Exception as e:
            logger.error(f"payment_error - error={str(e)}")
            raise AdiqPaymentError(f"Payment error: {e}")
    
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details from Adiq.
        
        Args:
            payment_id: Adiq payment ID
            
        Returns:
            Payment data
            
        Raises:
            AdiqError: If request fails
        """
        await self._ensure_authenticated()
        
        url = f"{self.base_url}/v1/payments/{payment_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"get_payment_failed - payment_id={payment_id}, status_code={e.response.status_code}")
            raise AdiqError(f"Get payment failed: {e}", status_code=e.response.status_code)
        except Exception as e:
            logger.error(f"get_payment_error - payment_id={payment_id}, error={str(e)}")
            raise AdiqError(f"Get payment error: {e}")
