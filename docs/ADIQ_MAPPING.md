# 🗺️ Mapeamento Adiq → Spdpay Gateway

**Versão:** 1.0.0  
**Data:** 2025-10-29

Este documento mapeia os campos da API Adiq para os models internos do Spdpay Gateway.

---

## 📋 Índice

- [Autenticação](#autenticação)
- [Tokenização](#tokenização)
- [Vault](#vault)
- [Pagamento](#pagamento)
- [Webhook](#webhook)
- [Estados](#estados)

---

## 🔐 Autenticação

### Request → Adiq

| Campo Spdpay | Campo Adiq | Tipo | Observação |
|--------------|------------|------|------------|
| `client_id` | `Authorization` (Basic) | string | Base64(clientId:clientSecret) |
| `client_secret` | `Authorization` (Basic) | string | Base64(clientId:clientSecret) |
| - | `grantType` | string | Sempre "client_credentials" |

### Response ← Adiq

| Campo Adiq | Campo Spdpay | Tipo | Armazenar? |
|------------|--------------|------|------------|
| `access_token` | `access_token` | string | ⚠️ Memória (1h) |
| `token_type` | - | string | Ignorar |
| `expires_in` | `expires_at` | int | Calcular timestamp |

---

## 💳 Tokenização

### Request → Adiq

```
POST /v1/tokens/cards
```

| Campo Spdpay | Campo Adiq | Tipo | PCI |
|--------------|------------|------|-----|
| `card_number` | `cardNumber` | string | ❌ Nunca armazenar |

### Response ← Adiq

| Campo Adiq | Campo Spdpay | Tipo | Armazenar? |
|------------|--------------|------|------------|
| `numberToken` | `card_token` | UUID | ✅ Sim (temporário) |

---

## 🏦 Vault (Cofre)

### Request → Adiq

```
POST /v1/vaults/cards
```

| Campo Spdpay | Campo Adiq | Tipo | PCI | Observação |
|--------------|------------|------|-----|------------|
| `card_token` | `numberToken` | UUID | ✅ | Token da etapa anterior |
| `brand` | `brand` | string | ✅ | visa, mastercard, elo, etc |
| `cardholder_name` | `cardholderName` | string | ❌ | Nunca armazenar |
| `expiration_month` | `expirationMonth` | string | ❌ | Nunca armazenar |
| `expiration_year` | `expirationYear` | string | ❌ | Nunca armazenar |
| `security_code` | `securityCode` | string | ❌ | Nunca armazenar |
| `verify_card` | `verifyCard` | boolean | - | Sempre true |

### Response ← Adiq

| Campo Adiq | Campo Spdpay | Tipo | Armazenar? |
|------------|--------------|------|------------|
| `vaultId` | `vault_id` | UUID | ✅ Sim |
| `brand` | `brand` | string | ✅ Sim |
| `last4` | `last4` | string | ✅ Sim |
| `status` | - | string | Validar = ACTIVE |

### Model Interno: `Card`

```python
class Card(BaseModel):
    id: UUID
    merchant_id: UUID
    customer_id: UUID
    vault_id: str          # ✅ Armazenar
    brand: str             # ✅ Armazenar
    last4: str             # ✅ Armazenar
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # ❌ NUNCA adicionar:
    # card_number, cvv, expiration_*, cardholder_name
```

---

## 💰 Pagamento

### Request → Adiq

```
POST /v2/payments
```

#### Payment Object

| Campo Spdpay | Campo Adiq | Tipo | Observação |
|--------------|------------|------|------------|
| `transaction_type` | `payment.transactionType` | string | "Credit" ou "Debit" |
| `amount` | `payment.amount` | int | Centavos |
| `currency` | `payment.currencyCode` | string | "brl" |
| `product_type` | `payment.productType` | string | "avista", "parcelado_loja" |
| `installments` | `payment.installments` | int | 1-12 |
| `capture_type` | `payment.captureType` | string | "ac" (auto), "pa" (pré-auth) |
| `recurrent` | `payment.recurrent` | boolean | false para MVP |

#### Card Info

| Campo Spdpay | Campo Adiq | Tipo | PCI |
|--------------|------------|------|-----|
| `card_token` | `cardInfo.numberToken` | UUID | ✅ |
| `brand` | `cardInfo.brand` | string | ✅ |
| `cardholder_name` | `cardInfo.cardholderName` | string | ❌ |
| `expiration_month` | `cardInfo.expirationMonth` | string | ❌ |
| `expiration_year` | `cardInfo.expirationYear` | string | ❌ |
| `security_code` | `cardInfo.securityCode` | string | ❌ |

#### Seller Info

| Campo Spdpay | Campo Adiq | Tipo | Observação |
|--------------|------------|------|------------|
| `order_number` | `sellerInfo.orderNumber` | string | Único por merchant |
| `soft_descriptor` | `sellerInfo.softDescriptor` | string | Max 13 chars |
| `antifraud_code` | `sellerInfo.CodeAntiFraud` | UUID | Opcional |
| `3ds_code` | `sellerInfo.code3DS` | UUID | Para 3DS |
| `3ds_url` | `sellerInfo.urlSite3DS` | string | URL de retorno 3DS |
| `program_protocol` | `sellerInfo.programProtocol` | string | "2.0.2" para 3DS |

#### Customer (Opcional)

| Campo Spdpay | Campo Adiq | Tipo | Observação |
|--------------|------------|------|------------|
| `document_type` | `customer.documentType` | string | "cpf" ou "cnpj" |
| `document_number` | `customer.documentNumber` | string | Sem formatação |
| `first_name` | `customer.firstName` | string | - |
| `last_name` | `customer.lastName` | string | - |
| `email` | `customer.email` | string | Importante para antifraude |
| `phone` | `customer.phoneNumber` | string | - |
| `mobile_phone` | `customer.mobilePhoneNumber` | string | - |
| `address` | `customer.address` | string | - |
| `complement` | `customer.complement` | string | - |
| `city` | `customer.city` | string | - |
| `state` | `customer.state` | string | 2 letras |
| `zip_code` | `customer.zipCode` | string | Sem formatação |
| `ip_address` | `customer.ipAddress` | string | IP do cliente |
| `country` | `customer.country` | string | "BR" |

#### Device Info (3DS)

| Campo Spdpay | Campo Adiq | Tipo | Observação |
|--------------|------------|------|------------|
| `ip_address` | `deviceInfo.ipAddress` | string | IP do cliente |
| `accept_header` | `deviceInfo.httpAcceptBrowserValue` | string | HTTP Accept |
| `color_depth` | `deviceInfo.httpBrowserColorDepth` | int | 24, 32, etc |
| `java_enabled` | `deviceInfo.httpBrowserJavaEnabled` | string | "Y" ou "N" |
| `javascript_enabled` | `deviceInfo.httpBrowserJavaScriptEnabled` | boolean | true/false |
| `language` | `deviceInfo.httpBrowserLanguage` | string | "pt-BR" |
| `screen_height` | `deviceInfo.httpBrowserScreenHeight` | int | Pixels |
| `screen_width` | `deviceInfo.httpBrowserScreenWidth` | int | Pixels |
| `timezone_offset` | `deviceInfo.httpBrowserTimeDifference` | int | Minutos |
| `user_agent` | `deviceInfo.userAgentBrowserValue` | string | User-Agent |

### Response ← Adiq

| Campo Adiq | Campo Spdpay | Tipo | Armazenar? |
|------------|--------------|------|------------|
| `paymentId` | `payment_id` | string | ✅ Sim |
| `authorizationCode` | `authorization_code` | string | ✅ Sim |
| `status` | `status` | string | ✅ Sim (mapear) |
| `amount` | `amount` | int | ✅ Sim |
| `captureType` | `capture_type` | string | ✅ Sim |
| `nsu` | `nsu` | string | ✅ Sim |
| `tid` | `tid` | string | ✅ Sim |
| `eci` | `eci` | string | ✅ Sim (3DS) |
| `cavv` | `cavv` | string | ✅ Sim (3DS) |
| `xid` | `xid` | string | ✅ Sim (3DS) |

### Model Interno: `Transaction`

```python
class Transaction(BaseModel):
    id: UUID
    invoice_id: UUID
    merchant_id: UUID
    
    # Adiq IDs
    payment_id: str              # ✅ paymentId
    authorization_code: str      # ✅ authorizationCode
    nsu: Optional[str]           # ✅ nsu
    tid: Optional[str]           # ✅ tid
    
    # Payment details
    amount: int                  # ✅ centavos
    currency: str                # ✅ "BRL"
    installments: int            # ✅ 1-12
    
    # Card info (safe)
    card_brand: str              # ✅ visa, mastercard
    card_last4: str              # ✅ últimos 4 dígitos
    
    # Status
    status: TransactionStatus    # ✅ CREATED, AUTHORIZED, etc
    
    # 3DS
    eci: Optional[str]           # ✅ Electronic Commerce Indicator
    cavv: Optional[str]          # ✅ Cardholder Authentication Value
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    authorized_at: Optional[datetime]
    captured_at: Optional[datetime]
    settled_at: Optional[datetime]
```

---

## 📨 Webhook

### Payload ← Adiq

```
POST /v1/webhooks/adiq
```

| Campo Adiq | Campo Spdpay | Tipo | Ação |
|------------|--------------|------|------|
| `eventType` | `event_type` | string | Mapear evento |
| `paymentId` | `payment_id` | string | Buscar transaction |
| `authorizationCode` | `authorization_code` | string | Validar |
| `status` | `new_status` | string | Atualizar |
| `amount` | `amount` | int | Validar |
| `timestamp` | `event_timestamp` | datetime | Registrar |
| `nsu` | `nsu` | string | Atualizar |
| `tid` | `tid` | string | Atualizar |

### Event Types

| Adiq Event | Spdpay Action | Transaction Status | Invoice Status |
|------------|---------------|-------------------|----------------|
| `PAYMENT_CREATED` | Log | CREATED | PROCESSING |
| `PAYMENT_AUTHORIZED` | Update | AUTHORIZED | PROCESSING |
| `PAYMENT_CAPTURED` | Update | CAPTURED | PROCESSING |
| `PAYMENT_APPROVED` | Update | SETTLED | PAID |
| `PAYMENT_DECLINED` | Update | DECLINED | FAILED |
| `PAYMENT_CANCELLED` | Update | CANCELLED | FAILED |
| `PAYMENT_REFUNDED` | Update | REFUNDED | REFUNDED |

### Model Interno: `WebhookLog`

```python
class WebhookLog(BaseModel):
    id: UUID
    merchant_id: UUID
    
    # Webhook data
    event_type: str
    payment_id: str
    payload: dict              # JSON completo
    signature: str             # HMAC signature
    
    # Processing
    processed: bool
    processed_at: Optional[datetime]
    error: Optional[str]
    
    # Timestamps
    received_at: datetime
    created_at: datetime
```

---

## 🔄 Estados

### Mapeamento de Status

#### Transaction Status

| Adiq Status | Spdpay Status | Descrição |
|-------------|---------------|-----------|
| `CREATED` | `CREATED` | Transação criada |
| `AUTHORIZED` | `AUTHORIZED` | Autorizada (pré-auth) |
| `CAPTURED` | `CAPTURED` | Capturada |
| `APPROVED` | `SETTLED` | Aprovada e liquidada |
| `DECLINED` | `DECLINED` | Negada |
| `CANCELLED` | `CANCELLED` | Cancelada |
| `REFUNDED` | `REFUNDED` | Estornada |
| `PENDING` | `PENDING` | Pendente (3DS, etc) |

#### Invoice Status

| Transaction Status | Invoice Status |
|-------------------|----------------|
| `CREATED` | `PROCESSING` |
| `AUTHORIZED` | `PROCESSING` |
| `CAPTURED` | `PROCESSING` |
| `SETTLED` | `PAID` |
| `DECLINED` | `FAILED` |
| `CANCELLED` | `FAILED` |

---

## 🔍 Consulta de Pagamento

### Request → Adiq

```
GET /v1/payments/{paymentId}
```

### Response ← Adiq

Mesmos campos do response de criação de pagamento.

---

## 🧪 Dados de Teste

### E-mails Especiais (Antifraude)

| E-mail | Resultado |
|--------|-----------|
| `accept@test.com` | APPROVED |
| `reject@test.com` | DECLINED |
| `review@test.com` | PENDING (manual review) |

### Cartões de Teste

Ver [CERTIFICATION.md](./CERTIFICATION.md#-cartões-de-teste)

---

## 📝 Notas Importantes

### Campos Obrigatórios vs Opcionais

#### Mínimo para Pagamento

```json
{
  "payment": {
    "transactionType": "Credit",
    "amount": 10000,
    "currencyCode": "brl",
    "productType": "avista",
    "installments": 1,
    "captureType": "ac"
  },
  "cardInfo": {
    "numberToken": "...",
    "brand": "visa",
    "cardholderName": "...",
    "expirationMonth": "12",
    "expirationYear": "25",
    "securityCode": "123"
  },
  "sellerInfo": {
    "orderNumber": "..."
  }
}
```

#### Para Antifraude (Recomendado)

Adicionar:
- `customer` completo
- `sellerInfo.CodeAntiFraud`
- `customer.email` (importante!)

#### Para 3DS (Obrigatório)

Adicionar:
- `sellerInfo.code3DS`
- `sellerInfo.urlSite3DS`
- `sellerInfo.programProtocol`
- `deviceInfo` completo
- `customer` completo

---

## 🔐 Regras de Segurança

### Nunca Armazenar

- ❌ `cardNumber`
- ❌ `securityCode` (CVV)
- ❌ `expirationMonth` + `expirationYear` (juntos)
- ❌ `cardholderName`

### Pode Armazenar

- ✅ `numberToken` (temporário, até criar vault)
- ✅ `vaultId` (permanente)
- ✅ `brand`
- ✅ `last4`
- ✅ `paymentId`
- ✅ `authorizationCode`

### Logs

```python
# ❌ NUNCA
logger.info(f"Payment: {payment_request}")

# ✅ SEMPRE sanitizar
logger.info(
    "payment_created",
    payment_id=payment_id,
    amount=amount,
    brand=brand,
    last4=last4,
    merchant_id=merchant_id
)
```

---

## 🔗 Referências

- **Documentação Adiq:** https://developers.adiq.io/manual/ecommerce
- **Portal Admin:** https://admin-hml.adiq.io/api
- **Postman Collection:** `docs/Adiq.Gateways.Ecommerce.postman_collection.json`

---

**Sempre consulte este documento ao implementar integrações com Adiq!**
