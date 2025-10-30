# 🚀 Próximos Passos - Continuação do Código

**Status Atual:** Core completo, schemas iniciados  
**Próximo:** Schemas, Models, Adapter Adiq, Services, API

---

## ✅ Já Criado

### Configuração
- ✅ `.env.example` - Variáveis de ambiente
- ✅ `.gitignore` - Arquivos ignorados
- ✅ `requirements.txt` - Dependências Python

### Core (`src/core/`)
- ✅ `config.py` - Configurações (Pydantic Settings)
- ✅ `exceptions.py` - Exceções customizadas
- ✅ `state_machine.py` - Estados de Invoice/Transaction
- ✅ `logger.py` - Logging com sanitização PCI
- ✅ `security.py` - API Key, webhook validation

### Schemas (`src/schemas/`)
- ✅ `base.py` - Schemas base

---

## 📝 Próximos Arquivos a Criar

### 1. Schemas Pydantic (`src/schemas/`)

#### `invoice.py`
```python
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class InvoiceBase(BaseModel):
    merchant_id: UUID
    customer_id: UUID
    amount: int  # em centavos
    currency: str = "BRL"
    description: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### `payment.py`
```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class PaymentCreate(BaseModel):
    invoice_id: UUID
    card_token: str  # Token da Adiq
    installments: int = 1
    capture_type: str = "ac"  # auto-capture

class PaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    status: str
    amount: int
    authorization_code: Optional[str]
    payment_id: Optional[str]  # ID da Adiq
    
    class Config:
        from_attributes = True
```

#### `card.py`
```python
from pydantic import BaseModel

class CardTokenizeRequest(BaseModel):
    card_number: str  # Apenas para tokenização, nunca armazenar

class CardTokenizeResponse(BaseModel):
    token: str  # numberToken da Adiq
    
class CardVaultRequest(BaseModel):
    number_token: str
    brand: str
    cardholder_name: str
    expiration_month: str
    expiration_year: str
    security_code: str

class CardVaultResponse(BaseModel):
    vault_id: str
    brand: str
    last4: str
```

### 2. Models (`src/models/`)

#### `merchant.py`
```python
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Merchant:
    def __init__(
        self,
        id: UUID = None,
        name: str = None,
        api_key_hash: str = None,
        is_active: bool = True,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.api_key_hash = api_key_hash
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
```

#### `invoice.py`, `transaction.py`, `customer.py`, `card.py`
- Seguir mesmo padrão do Merchant
- Ver `docs/ADIQ_MAPPING.md` para campos

### 3. Adapter Adiq (`src/adapters/adiq.py`)

```python
import httpx
from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import AdiqError, AdiqAuthenticationError

logger = get_logger(__name__)

class AdiqAdapter:
    def __init__(self):
        self.base_url = settings.adiq_base_url
        self.client_id = settings.adiq_client_id
        self.client_secret = settings.adiq_client_secret
        self.access_token = None
        self.token_expires_at = None
    
    async def authenticate(self) -> str:
        """Get OAuth2 access token from Adiq."""
        # Implementar conforme docs/ADIQ_MAPPING.md
        pass
    
    async def tokenize_card(self, card_number: str) -> str:
        """Tokenize card number."""
        pass
    
    async def create_vault(self, **kwargs) -> dict:
        """Create card vault."""
        pass
    
    async def create_payment(self, **kwargs) -> dict:
        """Create payment."""
        pass
```

### 4. Database (`src/db/`)

#### `client.py`
```python
from supabase import create_client, Client
from src.core.config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)
```

#### `schemas.sql`
```sql
-- Ver estrutura completa em docs/
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- invoices, transactions, customers, cards, webhook_logs
```

### 5. Services (`src/services/`)

#### `invoice_service.py`
```python
from uuid import UUID
from src.schemas.invoice import InvoiceCreate, InvoiceResponse
from src.db.client import supabase
from src.core.logger import get_logger

logger = get_logger(__name__)

class InvoiceService:
    async def create(self, data: InvoiceCreate) -> InvoiceResponse:
        """Create new invoice."""
        pass
    
    async def get(self, invoice_id: UUID) -> InvoiceResponse:
        """Get invoice by ID."""
        pass
    
    async def update_status(self, invoice_id: UUID, status: str) -> InvoiceResponse:
        """Update invoice status."""
        pass
```

#### `payment_service.py`, `webhook_service.py`
- Seguir mesmo padrão

### 6. API Endpoints (`src/api/v1/`)

#### `invoices.py`
```python
from fastapi import APIRouter, Depends
from src.schemas.invoice import InvoiceCreate, InvoiceResponse
from src.services.invoice_service import InvoiceService
from src.core.security import validate_api_key

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    data: InvoiceCreate,
    api_key: str = Depends(validate_api_key)
):
    service = InvoiceService()
    return await service.create(data)
```

#### `payments.py`, `cards.py`, `webhooks.py`
- Seguir mesmo padrão

### 7. Main (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.v1 import invoices, payments, cards, webhooks
from src.core.config import settings

app = FastAPI(
    title="Spdpay Gateway",
    version="1.0.0",
    description="Payment gateway for Spdpay"
)

# Include routers
app.include_router(invoices.router, prefix="/v1")
app.include_router(payments.router, prefix="/v1")
app.include_router(cards.router, prefix="/v1")
app.include_router(webhooks.router, prefix="/v1")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
```

### 8. Testes (`tests/`)

#### `fixtures/test_cards.py`
```python
TEST_CARDS = {
    "visa": {
        "pan": "4761739001010036",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123",
        "brand": "visa"
    },
    # Outros cartões de docs/CERTIFICATION.md
}

ANTIFRAUDE_EMAILS = {
    "accept": "accept@test.com",
    "reject": "reject@test.com",
    "review": "review@test.com"
}
```

#### `certification/test_adiq_flow.py`
- Ver `docs/CERTIFICATION.md` para casos de teste

### 9. Docker (`ops/`)

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

---

## 🎯 Ordem Recomendada

1. **Schemas** (invoice, payment, card) - Define contratos
2. **Models** (domain entities) - Representa dados
3. **Adapter Adiq** - Integração externa
4. **Database** (client + schemas SQL) - Persistência
5. **Services** (invoice, payment, webhook) - Lógica de negócio
6. **API Endpoints** - Exposição HTTP
7. **Main** - Entry point
8. **Testes** - Validação
9. **Docker** - Deploy

---

## 📚 Referências

- `docs/CONVENTIONS.md` - Padrões de código
- `docs/SECURITY.md` - Regras PCI
- `docs/ADIQ_MAPPING.md` - Campos da API Adiq
- `docs/CERTIFICATION.md` - Testes obrigatórios

---

**Próximo comando:** Peça para eu continuar gerando os schemas completos!
