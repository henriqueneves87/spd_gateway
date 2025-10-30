# 💳 Fluxo de Pagamento - Spdpay Gateway

## 🎯 Visão Geral

O Spdpay Gateway abstrai toda a complexidade da Adiq para seus clientes (merchants).  
**O merchant só precisa chamar seus endpoints** - a tokenização e processamento acontecem automaticamente!

---

## 📊 Fluxo Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. FRONTEND DO MERCHANT                                │
│    Cliente digita: 4761 7390 0101 0036                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ PAN + dados do cartão (HTTPS)
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 2. BACKEND DO MERCHANT                                 │
│    POST https://gateway.spdpay.com/v1/payments         │
│    Header: X-API-Key: merchant_api_key                 │
│    Body: {                                              │
│      "invoice_id": "...",                               │
│      "pan": "4761739001010036",  ← Envia PAN!         │
│      "cardholder_name": "JOSE SILVA",                   │
│      "expiration_month": "12",                          │
│      "expiration_year": "25",                           │
│      "security_code": "123",                            │
│      "installments": 1,                                 │
│      "capture_type": "ac"                               │
│    }                                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 3. SPDPAY GATEWAY ← AQUI A MÁGICA ACONTECE!           │
│                                                         │
│    A. Valida merchant (X-API-Key)                      │
│    B. Valida invoice                                    │
│    C. TOKENIZA o cartão na Adiq (interno)              │
│       - Usa credenciais do merchant                     │
│       - PAN → TOKEN                                     │
│    D. Processa pagamento com TOKEN                      │
│    E. Retorna resultado                                 │
│                                                         │
│    ⚠️ PAN nunca é armazenado!                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ (Comunicação interna)
                 ↓
┌─────────────────────────────────────────────────────────┐
│ 4. ADIQ API                                            │
│    - Tokenização: PAN → TOKEN                          │
│    - Processamento: TOKEN → Aprovação/Rejeição         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 API do Merchant (Cliente do Gateway)

### Endpoint: POST /v1/payments

**O merchant envia o PAN diretamente para você!**

```bash
curl -X POST https://gateway.spdpay.com/v1/payments \
  -H "X-API-Key: merchant_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "550e8400-e29b-41d4-a716-446655440000",
    "pan": "4761739001010036",
    "cardholder_name": "JOSE DA SILVA",
    "expiration_month": "12",
    "expiration_year": "25",
    "security_code": "123",
    "installments": 1,
    "capture_type": "ac"
  }'
```

**Response:**
```json
{
  "id": "txn_123456",
  "payment_id": "020004284405202219490000023429850000000000",
  "status": "APPROVED",
  "authorization_code": "027872",
  "amount": 10000,
  "installments": 1,
  "created_at": "2025-10-29T18:00:00Z"
}
```

---

## 🔐 Segurança: Como Funciona Internamente

### Passo 1: Merchant Chama Seu Gateway

```python
# Backend do merchant (Node.js, Python, PHP, etc)
response = requests.post(
    'https://gateway.spdpay.com/v1/payments',
    headers={'X-API-Key': 'merchant_key'},
    json={
        'invoice_id': invoice_id,
        'pan': '4761739001010036',  # ← Envia PAN
        'cardholder_name': 'JOSE SILVA',
        'expiration_month': '12',
        'expiration_year': '25',
        'security_code': '123',
        'installments': 1,
        'capture_type': 'ac'
    }
)
```

### Passo 2: Seu Gateway Tokeniza (Interno)

```python
# src/services/payment_service.py
async def process_payment(self, data: PaymentCreate, merchant_id: UUID):
    # 1. Buscar credenciais do merchant
    merchant = await get_merchant(merchant_id)
    
    # 2. Criar adapter com credenciais do merchant
    adapter = AdiqAdapter(
        client_id=merchant.adiq_client_id,
        client_secret=merchant.adiq_client_secret,
        seller_id=merchant.adiq_seller_id
    )
    
    # 3. TOKENIZAR o cartão (PAN → TOKEN)
    token_result = await adapter.tokenize_card(
        pan=data.pan,
        expiration_month=data.expiration_month,
        expiration_year=data.expiration_year,
        brand=data.brand
    )
    
    card_token = token_result['numberToken']
    
    # 4. Processar pagamento com TOKEN
    payment_result = await adapter.create_payment(
        number_token=card_token,  # ← Usa TOKEN, não PAN!
        amount=invoice.amount,
        ...
    )
    
    return payment_result
```

---

## 📚 Documentação para o Merchant

### Exemplo de Integração (Node.js)

```javascript
// Backend do merchant
const axios = require('axios');

async function processPayment(orderData) {
    try {
        const response = await axios.post(
            'https://gateway.spdpay.com/v1/payments',
            {
                invoice_id: orderData.invoiceId,
                pan: orderData.cardNumber,
                cardholder_name: orderData.cardholderName,
                expiration_month: orderData.expiryMonth,
                expiration_year: orderData.expiryYear,
                security_code: orderData.cvv,
                installments: orderData.installments || 1,
                capture_type: 'ac'
            },
            {
                headers: {
                    'X-API-Key': process.env.SPDPAY_API_KEY,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        if (response.data.status === 'APPROVED') {
            console.log('Pagamento aprovado!');
            console.log('Authorization Code:', response.data.authorization_code);
            return response.data;
        } else {
            console.log('Pagamento recusado');
            return null;
        }
    } catch (error) {
        console.error('Erro ao processar pagamento:', error.response?.data);
        throw error;
    }
}
```

---

## ⚠️ Importante: PCI DSS Compliance

### Seu Gateway (Spdpay)

- ✅ **Recebe PANs** (via HTTPS)
- ✅ **Tokeniza imediatamente** (não armazena)
- ✅ **Processa com tokens**
- ⚠️ **Requer PCI DSS Level 1** (você precisa se certificar)

### Merchant (Cliente)

- ✅ **Envia PANs** para seu gateway
- ✅ **Não precisa tokenizar**
- ✅ **Não precisa credenciais Adiq**
- ✅ **API simples e direta**
- ⚠️ **Ainda precisa HTTPS e segurança básica**

---

## 🎯 Vantagens para o Merchant

1. **API Simples**: Um único endpoint para tudo
2. **Sem Complexidade**: Não precisa entender Adiq
3. **Sem Credenciais**: Você gerencia tudo
4. **Sem Tokenização**: Você faz isso internamente
5. **Documentação Clara**: Fácil de integrar

---

## 📊 Comparação: Antes vs Depois

### ❌ Antes (Merchant faz tudo)

```javascript
// 1. Merchant tokeniza
const token = await adiq.tokenizeCard(pan);

// 2. Merchant processa
const payment = await adiq.createPayment(token);

// 3. Merchant gerencia credenciais Adiq
// 4. Merchant lida com erros da Adiq
// 5. Merchant precisa entender a API da Adiq
```

### ✅ Depois (Você faz tudo)

```javascript
// 1. Merchant só chama seu gateway
const payment = await spdpay.processPayment({
    pan: cardNumber,
    amount: 10000,
    ...
});

// Pronto! Você cuida do resto.
```

---

## 🚀 Resumo

**Para o Merchant:**
- Envia PAN → Recebe resultado
- Simples, direto, sem complicação

**Para Você (Spdpay):**
- Recebe PAN → Tokeniza → Processa → Retorna
- Toda a complexidade fica escondida
- Merchant nem sabe que a Adiq existe!

---

**Isso é o que um gateway de pagamento deve fazer!** 🎯
