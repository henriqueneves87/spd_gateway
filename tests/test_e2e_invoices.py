"""
End-to-end tests for Invoice endpoints.
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
async def test_create_invoice_success():
    """Test creating an invoice successfully."""
    async with get_client() as client:
        response = await client.post(
            "/v1/invoices",
            headers={"X-API-Key": API_KEY},
            json={
                "merchant_id": MERCHANT_ID,
                "customer_id": CUSTOMER_ID,
                "amount": 10000,
                "currency": "BRL",
                "description": "Test invoice"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 10000
        assert data["status"] == "PENDING"
        assert data["currency"] == "BRL"
        assert "id" in data
        
        # Save invoice ID for other tests
        return data["id"]


@pytest.mark.asyncio
async def test_create_invoice_missing_api_key():
    """Test creating invoice without API key."""
    async with get_client() as client:
        response = await client.post(
            "/v1/invoices",
            json={
                "merchant_id": MERCHANT_ID,
                "customer_id": CUSTOMER_ID,
                "amount": 10000
            }
        )
        
        assert response.status_code == 401
        assert "Missing API key" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_invoice_invalid_amount():
    """Test creating invoice with invalid amount."""
    async with get_client() as client:
        response = await client.post(
            "/v1/invoices",
            headers={"X-API-Key": API_KEY},
            json={
                "merchant_id": MERCHANT_ID,
                "customer_id": CUSTOMER_ID,
                "amount": -100,  # Invalid
                "currency": "BRL"
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_invoice_success():
    """Test getting an invoice by ID."""
    # First create an invoice
    async with get_client() as client:
        create_response = await client.post(
            "/v1/invoices",
            headers={"X-API-Key": API_KEY},
            json={
                "merchant_id": MERCHANT_ID,
                "customer_id": CUSTOMER_ID,
                "amount": 5000,
                "description": "Test get invoice"
            }
        )
        invoice_id = create_response.json()["id"]
        
        # Now get it
        get_response = await client.get(
            f"/v1/invoices/{invoice_id}",
            headers={"X-API-Key": API_KEY}
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == invoice_id
        assert data["amount"] == 5000


@pytest.mark.asyncio
async def test_get_invoice_not_found():
    """Test getting a non-existent invoice."""
    async with get_client() as client:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/v1/invoices/{fake_id}",
            headers={"X-API-Key": API_KEY}
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_invoices_success():
    """Test listing invoices."""
    async with get_client() as client:
        # Create a couple of invoices first
        for i in range(2):
            await client.post(
                "/v1/invoices",
                headers={"X-API-Key": API_KEY},
                json={
                    "merchant_id": MERCHANT_ID,
                    "customer_id": CUSTOMER_ID,
                    "amount": 1000 * (i + 1),
                    "description": f"Test invoice {i}"
                }
            )
        
        # List them
        response = await client.get(
            "/v1/invoices",
            headers={"X-API-Key": API_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


@pytest.mark.asyncio
async def test_list_invoices_with_status_filter():
    """Test listing invoices with status filter."""
    async with get_client() as client:
        response = await client.get(
            "/v1/invoices?status=PENDING",
            headers={"X-API-Key": API_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All should have PENDING status
        for invoice in data:
            assert invoice["status"] == "PENDING"


@pytest.mark.asyncio
async def test_list_invoices_with_pagination():
    """Test listing invoices with pagination."""
    async with get_client() as client:
        response = await client.get(
            "/v1/invoices?limit=5&offset=0",
            headers={"X-API-Key": API_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
