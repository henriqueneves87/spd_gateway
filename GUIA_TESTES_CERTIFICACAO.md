# 🧪 Guia Prático - Testes de Certificação Adiq

## 📋 Pré-requisitos

✅ Merchant Speedpay criado no Supabase  
✅ API rodando em http://127.0.0.1:8000  
✅ Credenciais Adiq HML configuradas

---

## 🎯 Planilha de Testes

### Informações do Merchant

- **Merchant ID:** `fb93c667-fbab-47ea-b3c7-9dd27231244a`
- **API Key:** `password`
- **Seller ID:** `speedpay_seller_hml` (atualizar com o real)

---

## 📝 Roteiro de Testes (Passo a Passo)

### ✅ Teste 1: Autenticação OAuth2

**Objetivo:** Validar que conseguimos obter token da Adiq

**Como testar:**
```bash
# Via Swagger UI
1. Acesse http://127.0.0.1:8000/docs
2. Não precisa testar diretamente - o adapter faz isso automaticamente
```

**Resultado esperado:**
- Token obtido com sucesso
- Válido por 1 hora

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Evidências:**
- [ ] Screenshot do log mostrando token obtido
- [ ] Token válido

---

### ✅ Teste 2: Tokenização de Cartão

**Objetivo:** Converter PAN em token seguro

**Cartão de teste:**
- **PAN:** 4761739001010036
- **Validade:** 12/25
- **CVV:** 123
- **Bandeira:** Visa

**Como testar:**

O Spdpay Gateway **não expõe** endpoint de tokenização diretamente (PCI compliance).
A tokenização acontece **antes** de chamar nossa API.

**Opções:**

1. **Via Adiq diretamente:**
```bash
curl -X POST https://ecommerce-hml.adiq.io/v1/tokens/cards \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pan": "4761739001010036",
    "expirationMonth": "12",
    "expirationYear": "25",
    "brand": "visa"
  }'
```

2. **Via frontend seguro** (recomendado em produção)

**Resultado esperado:**
```json
{
  "numberToken": "D391DFDF-91D6-43D1-A98F-1B9E4FE57B10",
  "brand": "visa",
  "last4": "0036"
}
```

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Token obtido: `_______________________________________`
- Last4: `____`

---

### ✅ Teste 3: Criar Invoice

**Objetivo:** Criar uma fatura para pagamento

**Como testar via Swagger:**

1. Acesse http://127.0.0.1:8000/docs
2. Expanda `POST /v1/invoices`
3. Clique em "Try it out"
4. Use este payload:

```json
{
  "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
  "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
  "amount": 10000,
  "currency": "BRL",
  "description": "Teste Certificação - Pagamento à Vista"
}
```

5. Header: `X-API-Key: password`
6. Execute

**Resultado esperado:**
- Status 201 Created
- Invoice criada com status PENDING

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Invoice ID: `_______________________________________`

---

### ✅ Teste 4: Pagamento à Vista (Auto-Captura)

**Objetivo:** Processar pagamento com captura automática

**Pré-requisito:**
- Token do cartão (do Teste 2)
- Invoice ID (do Teste 3)

**Como testar via Swagger:**

1. Expanda `POST /v1/payments`
2. Clique em "Try it out"
3. Use este payload:

```json
{
  "invoice_id": "COLE_O_INVOICE_ID_AQUI",
  "card_token": "COLE_O_TOKEN_DO_CARTAO_AQUI",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

4. Header: `X-API-Key: password`
5. Execute

**Resultado esperado:**
- Status 201 Created
- Status do pagamento: APPROVED
- Authorization code presente
- Payment ID da Adiq presente

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Payment ID: `_______________________________________`
- Authorization Code: `_______________________________________`
- NSU: `_______________________________________`
- Status: `_______________________________________`

---

### ✅ Teste 5: Pagamento Parcelado (3x)

**Objetivo:** Processar pagamento em 3 parcelas

**Como testar:**

1. Criar nova invoice com amount 30000 (R$ 300,00)
2. Processar pagamento com `"installments": 3`

```json
{
  "invoice_id": "NOVO_INVOICE_ID",
  "card_token": "TOKEN_DO_CARTAO",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 3,
  "capture_type": "ac"
}
```

**Resultado esperado:**
- Status APPROVED
- Installments = 3
- Amount = 30000

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Payment ID: `_______________________________________`
- Authorization Code: `_______________________________________`
- Installments: `____`

---

### ✅ Teste 6: Antifraude - Aprovado

**Objetivo:** Validar integração com antifraude (aprovação)

**Como testar:**

1. Criar invoice
2. Processar pagamento **COM** customer_data usando email `accept@test.com`

```json
{
  "invoice_id": "INVOICE_ID",
  "card_token": "TOKEN",
  "cardholder_name": "JOAO SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

**Body adicional (customer_data):**
```json
{
  "document_type": "cpf",
  "document_number": "05002827063",
  "first_name": "JOAO",
  "last_name": "SILVA",
  "email": "accept@test.com",
  "phone": "11999999999"
}
```

**Resultado esperado:**
- Status APPROVED
- Antifraude aprovou

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Payment ID: `_______________________________________`
- Antifraude Status: `_______________________________________`

---

### ✅ Teste 7: Antifraude - Rejeitado

**Objetivo:** Validar rejeição por antifraude

**Como testar:**

Mesmo processo do Teste 6, mas com email `reject@test.com`

**Resultado esperado:**
- Status DECLINED
- Motivo: Antifraude

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Payment ID: `_______________________________________`
- Motivo da rejeição: `_______________________________________`

---

### ✅ Teste 8: Antifraude - Revisão Manual

**Objetivo:** Validar fluxo de revisão manual

**Como testar:**

Mesmo processo do Teste 6, mas com email `review@test.com`

**Resultado esperado:**
- Status PENDING ou REVIEW
- Aguardando revisão manual

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

**Registrar:**
- Payment ID: `_______________________________________`
- Status: `_______________________________________`

---

### ✅ Teste 9: Consulta de Pagamento

**Objetivo:** Buscar informações de um pagamento

**Como testar via Swagger:**

1. Expanda `GET /v1/payments/{transaction_id}`
2. Cole um transaction_id de teste anterior
3. Header: `X-API-Key: password`
4. Execute

**Resultado esperado:**
- Status 200 OK
- Dados do pagamento retornados

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

---

### ✅ Teste 10: Webhook (Simulação)

**Objetivo:** Validar recebimento de webhooks da Adiq

**Como testar:**

1. Expanda `POST /v1/webhooks/adiq`
2. Simule um webhook:

```json
{
  "event_type": "payment.captured",
  "payment_id": "PAYMENT_ID_DE_TESTE",
  "status": "CAPTURED",
  "amount": 10000,
  "timestamp": "2025-10-29T18:00:00Z"
}
```

3. Execute

**Resultado esperado:**
- Status 200 OK
- Webhook processado

**Status:** ⬜ Pendente | ✅ Aprovado | ❌ Reprovado

---

## 📊 Resumo dos Testes

| # | Teste | Status | Payment ID | Auth Code |
|---|-------|--------|------------|-----------|
| 1 | OAuth2 | ⬜ | - | - |
| 2 | Tokenização | ⬜ | - | - |
| 3 | Criar Invoice | ⬜ | - | - |
| 4 | Pagamento à Vista | ⬜ | | |
| 5 | Parcelado 3x | ⬜ | | |
| 6 | Antifraude Aprovado | ⬜ | | |
| 7 | Antifraude Rejeitado | ⬜ | | |
| 8 | Antifraude Revisão | ⬜ | | |
| 9 | Consulta Pagamento | ⬜ | - | - |
| 10 | Webhook | ⬜ | - | - |

---

## 📸 Evidências Necessárias

Para cada teste, capture:

1. **Screenshot do Swagger** mostrando:
   - Request enviado
   - Response recebido
   - Status code

2. **Logs do servidor** mostrando:
   - Requisição processada
   - Chamada à Adiq
   - Resposta da Adiq

3. **Dados do Supabase** mostrando:
   - Invoice criada
   - Transaction criada
   - Status atualizado

---

## 🚀 Começar os Testes

1. ✅ Certifique-se que a API está rodando
2. ✅ Acesse http://127.0.0.1:8000/docs
3. ✅ Siga os testes na ordem
4. ✅ Registre todos os resultados
5. ✅ Capture evidências (screenshots)

---

**Boa sorte nos testes!** 🎯
