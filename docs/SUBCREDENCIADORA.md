# 🏦 Modelo Subcredenciadora - Spdpay Gateway

## 📋 Visão Geral

O Spdpay Gateway agora opera como uma **subcredenciadora real**, onde cada merchant (cliente) possui suas próprias credenciais Adiq e processa pagamentos em seu nome.

---

## 🔄 Mudanças Implementadas

### 1. **Schema do Banco de Dados**

Novos campos adicionados à tabela `merchants`:

```sql
ALTER TABLE merchants
ADD COLUMN adiq_seller_id TEXT,        -- ID do estabelecimento na Adiq
ADD COLUMN adiq_client_id TEXT,        -- Client ID do merchant na Adiq
ADD COLUMN adiq_client_secret TEXT,    -- Client Secret do merchant (deve ser criptografado)
ADD COLUMN adiq_environment TEXT DEFAULT 'hml',  -- Ambiente: hml ou prd
ADD COLUMN bank_code TEXT,             -- Código do banco
ADD COLUMN agency TEXT,                -- Agência
ADD COLUMN account TEXT,               -- Conta
ADD COLUMN webhook_url TEXT;           -- URL para webhooks
```

### 2. **Modelo Merchant Atualizado**

O modelo `Merchant` agora inclui:
- Credenciais Adiq específicas do merchant
- Informações bancárias
- Ambiente Adiq (HML/PRD)
- URL de webhook

### 3. **AdiqAdapter Dinâmico**

O `AdiqAdapter` foi atualizado para aceitar credenciais por merchant:

```python
adapter = AdiqAdapter(
    client_id=merchant.adiq_client_id,
    client_secret=merchant.adiq_client_secret,
    base_url=base_url,
    seller_id=merchant.adiq_seller_id
)
```

**Fallback:** Se o merchant não tiver credenciais próprias, usa as credenciais globais do `.env`.

### 4. **PaymentService com Credenciais Dinâmicas**

O `PaymentService` agora:
1. Busca as credenciais do merchant no banco
2. Cria um `AdiqAdapter` específico para aquele merchant
3. Inclui o `seller_id` no payload do pagamento

```python
# Payload enviado à Adiq
{
  "sellerInfo": {
    "id": "<merchant.adiq_seller_id>",  # ← Novo campo
    "orderNumber": "SPD-...",
    "softDescriptor": "PAG*SPDPAY"
  }
}
```

### 5. **Novo Endpoint: Registro de Merchant na Adiq**

**POST /v1/merchants/register-adiq**

Registra um merchant como seller na Adiq e armazena as credenciais retornadas.

**Payload:**
```json
{
  "legal_name": "Empresa LTDA",
  "document_number": "12345678000190",
  "mcc": "5411",
  "bank_code": "001",
  "agency": "1234",
  "account": "12345-6",
  "account_type": "checking",
  "email": "contato@empresa.com",
  "phone": "11999999999",
  "street": "Rua Exemplo",
  "number": "123",
  "neighborhood": "Centro",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234-567",
  "adiq_environment": "hml"
}
```

**Resposta:**
```json
{
  "id": "uuid",
  "name": "Empresa LTDA",
  "is_active": true,
  "adiq_seller_id": "seller_123",
  "adiq_environment": "hml",
  "has_adiq_credentials": true,
  "webhook_url": null,
  "created_at": "2025-10-29T...",
  "updated_at": "2025-10-29T..."
}
```

### 6. **Novo Endpoint: Informações do Merchant**

**GET /v1/merchants/me**

Retorna informações do merchant autenticado (baseado no `X-API-Key`).

---

## 🔐 Segurança

### ⚠️ Importante

1. **Criptografia do `client_secret`**
   - O campo `adiq_client_secret` **deve ser criptografado** antes de ser armazenado
   - Atualmente armazenado em texto plano (TODO: implementar criptografia)

2. **Nunca Expor Credenciais**
   - O endpoint `/merchants/me` retorna apenas `has_adiq_credentials: true/false`
   - Nunca retorna `client_id` ou `client_secret` via API

3. **Logs Sanitizados**
   - Credenciais nunca aparecem nos logs
   - Apenas flags booleanas são logadas

---

## 🚀 Fluxo de Uso

### Cenário 1: Merchant com Credenciais Próprias

1. Merchant se registra na Adiq via `POST /merchants/register-adiq`
2. Sistema armazena `seller_id`, `client_id`, `client_secret`
3. Ao processar pagamento:
   - Sistema busca credenciais do merchant
   - Cria `AdiqAdapter` com credenciais do merchant
   - Envia pagamento com `sellerInfo.id = seller_id`
   - Pagamento é processado **em nome do merchant**

### ~~Cenário 2: Merchant sem Credenciais (Fallback)~~ ❌ REMOVIDO

**🚫 FALLBACK GLOBAL REMOVIDO**

A partir desta versão, **não é mais possível processar pagamentos sem credenciais próprias**.

Se um merchant tentar processar um pagamento sem ter:
- `adiq_client_id`
- `adiq_client_secret`
- `adiq_seller_id`

O sistema retornará **HTTP 400** com a mensagem:
```
Merchant não possui credenciais da Adiq configuradas.
Registre-se via POST /v1/merchants/register-adiq antes de processar pagamentos.
```

---

## 📊 Endpoints Atualizados

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/v1/merchants/register-adiq` | POST | Registra merchant na Adiq |
| `/v1/merchants/me` | GET | Informações do merchant autenticado |
| `/v1/payments` | POST | Processa pagamento (agora com credenciais dinâmicas) |

---

## 🧪 Testando

### 1. Registrar Merchant na Adiq

```bash
curl -X POST http://localhost:8000/v1/merchants/register-adiq \
  -H "X-API-Key: test" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Teste LTDA",
    "document_number": "12345678000190",
    "mcc": "5411",
    "bank_code": "001",
    "agency": "1234",
    "account": "12345-6",
    "account_type": "checking",
    "email": "teste@empresa.com",
    "phone": "11999999999",
    "street": "Rua Teste",
    "number": "123",
    "neighborhood": "Centro",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234-567",
    "adiq_environment": "hml"
  }'
```

### 2. Ver Informações do Merchant

```bash
curl http://localhost:8000/v1/merchants/me \
  -H "X-API-Key: test"
```

### 3. Processar Pagamento

```bash
curl -X POST http://localhost:8000/v1/payments \
  -H "X-API-Key: test" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "uuid-da-invoice",
    "card_token": "token-adiq",
    "cardholder_name": "TESTE",
    "expiration_month": "12",
    "expiration_year": "25",
    "security_code": "123",
    "installments": 1,
    "capture_type": "ac"
  }'
```

---

## ✅ Checklist de Implementação

- [x] Schema Supabase atualizado
- [x] Modelo `Merchant` atualizado
- [x] `AdiqAdapter` com credenciais dinâmicas
- [x] `PaymentService` busca credenciais do merchant
- [x] Campo `sellerInfo.id` incluído nos pagamentos
- [x] Endpoint `/merchants/register-adiq` criado
- [x] Endpoint `/merchants/me` criado
- [x] ~~Fallback para credenciais globais~~ **REMOVIDO** ✅
- [x] Validação obrigatória de credenciais
- [x] HTTP 400 para merchants sem credenciais
- [x] Logs sanitizados
- [ ] **TODO: Criptografar `adiq_client_secret`**

---

## 🚫 Regras de Segurança (Atualizado)

### ✅ Credenciais Obrigatórias

**TODOS os pagamentos DEVEM ter:**
1. `adiq_client_id` do merchant
2. `adiq_client_secret` do merchant
3. `adiq_seller_id` do merchant
4. `sellerInfo.id` no payload enviado à Adiq

**Sem exceções. Sem fallback.**

### ⚠️ Uso das Credenciais Globais

As credenciais globais (`ADIQ_CLIENT_ID`, `ADIQ_CLIENT_SECRET`) no `.env` são usadas **APENAS** para:
- Endpoint administrativo `/v1/merchants/register-adiq`
- Operações de gestão do gateway
- **NUNCA** para processar pagamentos de clientes

---

## 🔮 Próximos Passos

1. **Implementar criptografia** do `client_secret`
2. **Adicionar testes** para novos endpoints
3. **Documentar processo** de certificação por merchant
4. **Implementar webhook** por merchant
5. **Dashboard** para merchants gerenciarem suas credenciais

---

**Modelo subcredenciadora implementado com sucesso!** 🎉
