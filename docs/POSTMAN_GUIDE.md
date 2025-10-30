# 🚀 Guia Rápido - Postman

## 📥 Importar Collection

1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo: `docs/Spdpay_Gateway.postman_collection.json`
4. Clique em **Import**

---

## ⚙️ Configurar Environment

1. Clique em **Environments** (ícone de engrenagem)
2. Clique em **Create Environment**
3. Nome: `Spdpay Local`
4. Adicione as variáveis:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `api_key` | `password` | `password` |
| `merchant_id` | `fb93c667-fbab-47ea-b3c7-9dd27231244a` | `fb93c667-fbab-47ea-b3c7-9dd27231244a` |
| `customer_id` | `3b415031-7236-425e-bc8f-35c7a5f572ab` | `3b415031-7236-425e-bc8f-35c7a5f572ab` |
| `invoice_id` | | |
| `transaction_id` | | |
| `card_token` | | |

5. Clique em **Save**
6. Selecione o environment `Spdpay Local` no dropdown

---

## 🎯 Fluxo de Teste Completo

### 1️⃣ Verificar API

**Request:** `Health Check`

Deve retornar:
```json
{
  "status": "healthy"
}
```

---

### 2️⃣ Criar Invoice

**Request:** `Invoices > Create Invoice`

Body já está preenchido:
```json
{
  "merchant_id": "{{merchant_id}}",
  "customer_id": "{{customer_id}}",
  "amount": 1000,
  "currency": "BRL",
  "description": "Teste de pagamento"
}
```

**Resultado:**
- ✅ Status: 200 OK
- ✅ Variável `invoice_id` preenchida automaticamente

---

### 3️⃣ Gerar Token de Cartão

**Antes de processar pagamento, gere um token fresco:**

```bash
# No terminal
cd c:\spdpay_gateway
python gerar_token.py
```

**Copie o token do Visa e cole na variável `card_token` do environment.**

---

### 4️⃣ Processar Pagamento (Opção A: Com Token)

**Request:** `Payments > Create Payment (with Token)`

Body:
```json
{
  "invoice_id": "{{invoice_id}}",
  "card_token": "{{card_token}}",
  "brand": "visa",
  "cardholder_name": "JOSE DA SILVA",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123",
  "installments": 1,
  "capture_type": "ac"
}
```

**Resultado:**
- ✅ Status: 200 OK
- ✅ Variáveis `payment_id` e `transaction_id` preenchidas
- ✅ Pagamento aprovado!

---

### 4️⃣ Processar Pagamento (Opção B: Com PAN)

**Request:** `Payments > Create Payment (with PAN)`

Body:
```json
{
  "invoice_id": "{{invoice_id}}",
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

**Vantagem:** Não precisa gerar token manualmente!

---

### 5️⃣ Consultar Pagamento

**Request:** `Payments > Get Payment`

URL: `http://localhost:8000/v1/payments/{{transaction_id}}`

**Resultado:**
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

## 🎴 Cartões de Teste

### Visa (Aprovado)
```json
{
  "pan": "4761739001010036",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123"
}
```

### Mastercard (Aprovado)
```json
{
  "pan": "5201561050025011",
  "expiration_month": "12",
  "expiration_year": "25",
  "security_code": "123"
}
```

---

## ⚠️ Problemas Comuns

### ❌ 401 Unauthorized
**Solução:** Verifique se a API Key está correta no environment (`password`)

### ❌ 404 Not Found
**Solução:** Verifique se o servidor está rodando em `http://localhost:8000`

### ❌ Token inválido ou não existe
**Solução:** Gere um novo token com `python gerar_token.py` (tokens expiram em 10 minutos)

### ❌ Merchant não encontrado
**Solução:** Verifique se o `merchant_id` está correto no environment

---

## 🔄 Workflow Automatizado

A collection já tem **scripts de teste** que preenchem as variáveis automaticamente:

1. **Create Invoice** → Salva `invoice_id`
2. **Create Payment** → Salva `payment_id` e `transaction_id`
3. **Get Payment** → Usa `transaction_id` automaticamente

Basta executar as requests em sequência! 🚀

---

## 📊 Testar Parcelamento

**Request:** `Payments > Create Payment (Parcelado)`

Altere o campo `installments`:
```json
{
  "installments": 3
}
```

**Resultado:** Pagamento parcelado em 3x

---

## 🎯 Dicas

1. **Sempre gere tokens frescos** antes de testar (expiram em 10min)
2. **Use PAN diretamente** para evitar expiração de tokens
3. **Verifique o console do servidor** para ver logs detalhados
4. **Use o Swagger** em `http://localhost:8000/docs` para testar também

---

## 📝 Próximos Passos

1. ✅ Importar collection
2. ✅ Configurar environment
3. ✅ Testar Health Check
4. ✅ Criar Invoice
5. ✅ Processar Pagamento
6. ✅ Consultar resultado

**Pronto! Você já pode testar o gateway completo!** 🎉
