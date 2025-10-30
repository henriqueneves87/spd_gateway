# 📖 Guia do Swagger - Spdpay Gateway

## 🌐 Acessar Swagger

1. Inicie o servidor:
   ```bash
   uvicorn src.main:app --reload
   ```

2. Acesse: **http://localhost:8000/docs**

---

## 🔐 Autenticação

Antes de fazer qualquer requisição (exceto Health Check):

1. Clique no botão **🔒 Authorize** (canto superior direito)
2. Em **APIKeyHeader (apiKey)**:
   - **Value:** `password`
3. Clique em **Authorize**
4. Clique em **Close**

✅ Agora você está autenticado!

---

## 🎯 Fluxo Completo de Teste

### 1️⃣ Health Check

**Endpoint:** `GET /health`

1. Expanda o endpoint
2. Clique em **Try it out**
3. Clique em **Execute**

✅ Deve retornar: `{"status": "healthy"}`

---

### 2️⃣ Criar Invoice

**Endpoint:** `POST /v1/invoices`

1. Expanda o endpoint
2. Clique em **Try it out**
3. Use o exemplo padrão (já preenchido):

```json
{
  "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
  "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
  "amount": 1000,
  "currency": "BRL",
  "description": "Teste de pagamento"
}
```

4. Clique em **Execute**

✅ **Copie o `id` da resposta** - você vai precisar dele!

---

### 3️⃣ Processar Pagamento (com PAN)

**Endpoint:** `POST /v1/payments/`

1. Expanda o endpoint
2. Clique em **Try it out**
3. **COLE O PAYLOAD CORRETO:**

```json
{
  "invoice_id": "COLE-O-ID-DA-INVOICE-AQUI",
  "pan": "4761739001010036",
  "brand": "visa",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

4. **Substitua** `COLE-O-ID-DA-INVOICE-AQUI` pelo UUID da invoice criada no passo 2
5. Clique em **Execute**

✅ **Pagamento aprovado!** 🎉

**Resposta esperada:**
```json
{
  "id": "uuid",
  "status": "CAPTURED",
  "payment_id": "020085619310292014490007157884210000000000",
  "authorization_code": "275505",
  ...
}
```

---

### 4️⃣ Consultar Pagamento

**Endpoint:** `GET /v1/payments/{transaction_id}`

1. Expanda o endpoint
2. Clique em **Try it out**
3. Cole o `transaction_id` da resposta anterior
4. Clique em **Execute**

✅ Veja os detalhes completos do pagamento!

---

## 🎴 Cartões de Teste

### Visa (Aprovado)
```json
{
  "pan": "4761739001010036",
  "brand": "visa",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123"
}
```

### Mastercard (Aprovado)
```json
{
  "pan": "5201561050025011",
  "brand": "mastercard",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123"
}
```

---

## 💡 Dicas Importantes

### ❌ NÃO use esta estrutura:
```json
{
  "data": {
    "invoice_id": "...",
    "card_token": "string",
    ...
  },
  "customer_data": {}
}
```

### ✅ USE esta estrutura:
```json
{
  "invoice_id": "uuid-da-invoice",
  "pan": "4761739001010036",
  "brand": "visa",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

---

## 🔄 Duas Opções de Pagamento

### Opção 1: PAN (Recomendado) ⭐

**Vantagem:** Não expira, mais simples!

```json
{
  "invoice_id": "uuid",
  "pan": "4761739001010036",
  "brand": "visa",
  ...
}
```

### Opção 2: Token

**Quando usar:** Se você já tem um token pré-gerado.

**Gerar token:**
```bash
python gerar_token.py
```

**Payload:**
```json
{
  "invoice_id": "uuid",
  "card_token": "TOKEN-GERADO",
  "brand": "visa",
  ...
}
```

⚠️ **Tokens expiram em 10 minutos!**

---

## 📊 Testar Parcelamento

Altere o campo `installments`:

```json
{
  "invoice_id": "uuid",
  "pan": "4761739001010036",
  "brand": "visa",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 3,  ← Parcelado em 3x
  "capture_type": "ac"
}
```

---

## ⚠️ Erros Comuns

### ❌ 401 Unauthorized
**Solução:** Clique em 🔒 Authorize e adicione a API Key: `password`

### ❌ 404 Invoice not found
**Solução:** Crie uma invoice primeiro (POST /v1/invoices)

### ❌ Either pan or card_token must be provided
**Solução:** Adicione o campo `pan` OU `card_token` (não ambos)

### ❌ brand is required when using pan
**Solução:** Adicione o campo `brand` quando usar `pan`

---

## 🎯 Exemplo Completo Passo a Passo

### 1. Criar Invoice
```json
POST /v1/invoices
{
  "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
  "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
  "amount": 1000,
  "currency": "BRL",
  "description": "Teste"
}
```

**Resposta:** Copie o `id`

### 2. Processar Pagamento
```json
POST /v1/payments/
{
  "invoice_id": "ID-COPIADO-ACIMA",
  "pan": "4761739001010036",
  "brand": "visa",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

**Resposta:** Pagamento aprovado! 🎉

---

## 📝 Campos Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `invoice_id` | UUID da invoice | `"uuid"` |
| `pan` ou `card_token` | Número do cartão OU token | `"4761739001010036"` |
| `brand` | Bandeira (se usar PAN) | `"visa"` |
| `cardholder_name` | Nome no cartão | `"JOSE DA SILVA"` |
| `expiration_month` | Mês (MM) | `"12"` |
| `expiration_year` | Ano (YY) | `"25"` |
| `security_code` | CVV | `"123"` |
| `installments` | Parcelas (1-12) | `1` |
| `capture_type` | ac ou pa | `"ac"` |

---

## 🚀 Pronto!

Agora você pode testar o gateway completo pelo Swagger! 🎉

**Dúvidas?** Consulte: `docs/API_DOCUMENTATION.md`
