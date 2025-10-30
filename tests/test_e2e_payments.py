"""
End-to-end tests for Payment endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

# Test data
MERCHANT_ID = "219c230a-5c4b-43d4-861d-f25979de2e88"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"
API_KEY = "test"


def get_client():
    """Get test client with proper configuration."""
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    )


@pytest.mark.asyncio
async def test_payment_without_adiq_credentials_should_fail():
    """
    Test that payment fails with HTTP 400 when merchant has no Adiq credentials.
    
    This test validates the subcredenciadora model:
    - No fallback to global credentials
    - Merchants MUST have their own Adiq credentials
    - Clear error message guiding merchant to register
    """
    async with get_client() as client:
        # First, create an invoice
        invoice_response = await client.post(
            "/v1/invoices",
            headers={"X-API-Key": API_KEY},
            json={
                "merchant_id": MERCHANT_ID,
                "customer_id": CUSTOMER_ID,
                "amount": 10000,
                "currency": "BRL",
                "description": "Test payment without credentials"
            }
        )
        
        assert invoice_response.status_code == 201
        invoice_id = invoice_response.json()["id"]
        
        # Try to process payment (merchant doesn't have Adiq credentials)
        payment_response = await client.post(
            "/v1/payments",
            headers={"X-API-Key": API_KEY},
            json={
                "invoice_id": invoice_id,
                "card_token": "fake_token",
                "cardholder_name": "TEST USER",
                "expiration_month": "12",
                "expiration_year": "25",
                "security_code": "123",
                "installments": 1,
                "capture_type": "ac"
            }
        )
        
        # Should fail with 400
        assert payment_response.status_code == 400
        
        error_detail = payment_response.json()["detail"]
        
        # Validate error message
        assert "não possui credenciais" in error_detail.lower()
        assert "register-adiq" in error_detail.lower()
        
        # Log for debugging
        print(f"✅ Payment correctly rejected: {error_detail}")


@pytest.mark.asyncio
async def test_payment_endpoint_requires_authentication():
    """Test that payment endpoint requires API key."""
    async with get_client() as client:
        response = await client.post(
            "/v1/payments",
            json={
                "invoice_id": "00000000-0000-0000-0000-000000000000",
                "card_token": "token",
                "cardholder_name": "TEST",
                "expiration_month": "12",
                "expiration_year": "25",
                "security_code": "123",
                "installments": 1,
                "capture_type": "ac"
            }
        )
        
        assert response.status_code == 401
        assert "Missing API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_payment_with_invalid_invoice():
    """Test payment with non-existent invoice."""
    async with get_client() as client:
        response = await client.post(
            "/v1/payments",
            headers={"X-API-Key": API_KEY},
            json={
                "invoice_id": "00000000-0000-0000-0000-000000000000",
                "card_token": "token",
                "cardholder_name": "TEST",
                "expiration_month": "12",
                "expiration_year": "25",
                "security_code": "123",
                "installments": 1,
                "capture_type": "ac"
            }
        )
        
        # Should fail (invoice not found or credentials missing)
        assert response.status_code in [400, 404]
