"""
Merchant API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.merchant import MerchantRegisterAdiq, MerchantResponse
from src.api.dependencies import get_current_merchant
from src.core.logger import get_logger
from src.db.client import supabase
import httpx
from src.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.post("/register-adiq", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def register_merchant_in_adiq(
    data: MerchantRegisterAdiq,
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Register merchant as a seller in Adiq.
    
    This endpoint:
    1. Creates a seller in Adiq via POST /v1/sellers
    2. Stores the returned seller_id, client_id, and client_secret
    3. Updates the merchant record in Supabase
    
    **Required fields:**
    - legal_name: Business legal name
    - document_number: CNPJ
    - mcc: Merchant Category Code
    - bank_code, agency, account: Banking info
    - email, phone: Contact info
    - address fields: Complete address
    
    **Environments:**
    - hml: https://ecommerce-hml.adiq.io
    - prd: https://ecommerce.adiq.io
    """
    try:
        # Determine Adiq base URL
        base_url = "https://ecommerce.adiq.io" if data.adiq_environment == "prd" else "https://ecommerce-hml.adiq.io"
        
        # 1. Authenticate with Adiq (using global credentials)
        auth_url = f"{base_url}/auth/oauth2/v1/token"
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": settings.adiq_client_id,
            "client_secret": settings.adiq_client_secret
        }
        
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(auth_url, data=auth_data, headers=auth_headers, timeout=30.0)
            auth_response.raise_for_status()
            access_token = auth_response.json()["access_token"]
        
        # 2. Register seller in Adiq
        seller_url = f"{base_url}/v1/sellers"
        seller_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        seller_payload = {
            "legalName": data.legal_name,
            "documentNumber": data.document_number,
            "mcc": data.mcc,
            "bankAccount": {
                "bankCode": data.bank_code,
                "agency": data.agency,
                "account": data.account,
                "accountType": data.account_type
            },
            "contact": {
                "email": data.email,
                "phoneNumber": data.phone
            },
            "address": {
                "street": data.street,
                "number": data.number,
                "complement": data.complement,
                "neighborhood": data.neighborhood,
                "city": data.city,
                "state": data.state,
                "zipCode": data.zip_code
            }
        }
        
        async with httpx.AsyncClient() as client:
            seller_response = await client.post(
                seller_url,
                json=seller_payload,
                headers=seller_headers,
                timeout=60.0
            )
            seller_response.raise_for_status()
            seller_data = seller_response.json()
        
        # 3. Update merchant in Supabase
        update_data = {
            "adiq_seller_id": seller_data["sellerId"],
            "adiq_client_id": seller_data["clientId"],
            "adiq_client_secret": seller_data["clientSecret"],  # TODO: Encrypt this
            "adiq_environment": data.adiq_environment,
            "bank_code": data.bank_code,
            "agency": data.agency,
            "account": data.account
        }
        
        result = supabase.table("merchants").update(update_data).eq("id", str(merchant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update merchant"
            )
        
        merchant = result.data[0]
        
        logger.info(
            f"merchant_registered_in_adiq - merchant_id={merchant_id}, "
            f"seller_id={seller_data['sellerId']}, env={data.adiq_environment}"
        )
        
        return MerchantResponse(
            id=merchant["id"],
            name=merchant["name"],
            is_active=merchant["is_active"],
            adiq_seller_id=merchant["adiq_seller_id"],
            adiq_environment=merchant["adiq_environment"],
            has_adiq_credentials=True,
            webhook_url=merchant.get("webhook_url"),
            created_at=merchant["created_at"],
            updated_at=merchant["updated_at"]
        )
        
    except httpx.HTTPStatusError as e:
        logger.error(f"adiq_registration_failed - status={e.response.status_code}, detail={e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Adiq registration failed: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"merchant_registration_error - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Merchant registration failed: {str(e)}"
        )


@router.get("/me", response_model=MerchantResponse)
async def get_current_merchant_info(
    merchant_id: UUID = Depends(get_current_merchant)
):
    """
    Get current merchant information (based on API key).
    """
    try:
        result = supabase.table("merchants").select("*").eq("id", str(merchant_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant not found"
            )
        
        merchant = result.data[0]
        
        return MerchantResponse(
            id=merchant["id"],
            name=merchant["name"],
            is_active=merchant["is_active"],
            adiq_seller_id=merchant.get("adiq_seller_id"),
            adiq_environment=merchant.get("adiq_environment", "hml"),
            has_adiq_credentials=bool(merchant.get("adiq_client_id") and merchant.get("adiq_client_secret")),
            webhook_url=merchant.get("webhook_url"),
            created_at=merchant["created_at"],
            updated_at=merchant["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"get_merchant_failed - error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get merchant: {str(e)}"
        )
