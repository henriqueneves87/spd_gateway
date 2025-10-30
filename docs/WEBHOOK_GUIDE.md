# 🔔 Guia de Webhooks - Spdpay Gateway

## 📋 O Que São Webhooks?

Webhooks são notificações automáticas que a Adiq envia para o seu gateway quando o status de um pagamento muda.

---

## 🎯 Eventos Suportados

| Evento | Descrição |
|--------|-----------|
| `payment.authorized` | Pagamento pré-autorizado |
| `payment.captured` | Pagamento capturado (aprovado) |
| `payment.settled` | Pagamento liquidado |
| `payment.declined` | Pagamento recusado |
| `payment.cancelled` | Pagamento cancelado |
| `payment.refunded` | Pagamento estornado |

---

## 🔧 Endpoint do Webhook

```
POST /v1/webhooks/adiq
```

**Headers:**
```
Content-Type: application/json
X-Webhook-Signature: <assinatura_da_adiq>
```

---

## 📝 Exemplo de Payload

```json
{
  "eventType": "payment.captured",
  "eventId": "evt_123456789",
  "timestamp": "2025-10-30T12:00:00Z",
  "data": {
    "paymentId": "020048967410301230120007230412810000000000",
    "transactionId": "b39e466c-d3d5-4c4a-911a-52f869a06801",
    "status": "Captured",
    "authorizationCode": "223899",
    "amount": 1000,
    "currency": "BRL",
    "installments": 1,
    "cardBrand": "visa",
    "cardLast4": "0036"
  }
}
```

---

## 🧪 Como Testar

### Opção 1: Script Python

```bash
python test_webhook.py
```

### Opção 2: cURL

```bash
curl -X POST http://localhost:8000/v1/webhooks/adiq \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: test_signature" \
  -d '{
    "eventType": "payment.captured",
    "eventId": "evt_123",
    "timestamp": "2025-10-30T12:00:00Z",
    "data": {
      "paymentId": "020048967410301230120007230412810000000000",
      "status": "Captured",
      "authorizationCode": "223899"
    }
  }'
```

### Opção 3: Postman

1. **Método:** POST
2. **URL:** `http://localhost:8000/v1/webhooks/adiq`
3. **Headers:**
   - `Content-Type`: `application/json`
   - `X-Webhook-Signature`: `test_signature`
4. **Body:** Cole o JSON de exemplo acima

---

## 🔐 Segurança

### Validação de Assinatura

A Adiq envia uma assinatura no header `X-Webhook-Signature` para garantir que o webhook é legítimo.

**Implementação:**
```python
import hmac
import hashlib

def validate_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## 📊 Fluxo do Webhook

```
1. Adiq processa pagamento
   ↓
2. Adiq envia webhook para seu gateway
   ↓
3. Gateway valida assinatura
   ↓
4. Gateway atualiza status da transação
   ↓
5. Gateway retorna 200 OK
   ↓
6. Adiq marca webhook como entregue
```

---

## ⚠️ Boas Práticas

### 1. Sempre Retorne 200 OK Rapidamente
```python
# ✅ Bom
@router.post("/webhooks/adiq")
async def webhook(request: Request):
    # Processar em background
    background_tasks.add_task(process_webhook, payload)
    return {"success": True}

# ❌ Ruim
@router.post("/webhooks/adiq")
async def webhook(request: Request):
    # Processar síncrono (pode dar timeout)
    await heavy_processing()
    return {"success": True}
```

### 2. Implemente Idempotência
```python
# Verificar se webhook já foi processado
if await webhook_already_processed(event_id):
    return {"success": True, "message": "Already processed"}
```

### 3. Valide Sempre a Assinatura
```python
if not validate_signature(body, signature, webhook_secret):
    raise HTTPException(status_code=401, detail="Invalid signature")
```

### 4. Log Tudo
```python
logger.info(f"webhook_received - event={event_type}, id={event_id}")
```

---

## 🔄 Retry Policy da Adiq

Se seu endpoint não responder 200 OK, a Adiq tentará reenviar:

| Tentativa | Delay |
|-----------|-------|
| 1ª | Imediato |
| 2ª | 1 minuto |
| 3ª | 5 minutos |
| 4ª | 30 minutos |
| 5ª | 1 hora |
| 6ª | 6 horas |

---

## 🌐 Configurar URL do Webhook na Adiq

### Via Portal Adiq

1. Acesse: https://portal-spdpaydigital-hml.adiq.io/
2. Vá em **Configurações** → **Webhooks**
3. Adicione a URL: `https://seu-dominio.com/v1/webhooks/adiq`
4. Salve

### Via API (Futuro)

```bash
POST /v1/merchants/{merchant_id}/webhooks
{
  "url": "https://seu-dominio.com/v1/webhooks/adiq",
  "events": ["payment.captured", "payment.declined"]
}
```

---

## 🧪 Testar com ngrok (Desenvolvimento)

Para testar webhooks em desenvolvimento local:

### 1. Instalar ngrok
```bash
choco install ngrok
```

### 2. Expor seu servidor
```bash
ngrok http 8000
```

### 3. Usar URL do ngrok
```
https://abc123.ngrok.io/v1/webhooks/adiq
```

### 4. Configurar na Adiq
Cole a URL do ngrok no portal da Adiq

---

## 📝 Exemplo Completo

```python
from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/webhooks/adiq")
async def adiq_webhook(
    request: Request,
    x_webhook_signature: str = Header(None)
):
    # 1. Obter payload
    body = await request.body()
    payload = await request.json()
    
    # 2. Validar assinatura
    if not validate_signature(body, x_webhook_signature):
        raise HTTPException(status_code=401)
    
    # 3. Verificar duplicata
    event_id = payload.get("eventId")
    if await is_duplicate(event_id):
        return {"success": True, "message": "Already processed"}
    
    # 4. Processar evento
    event_type = payload.get("eventType")
    
    if event_type == "payment.captured":
        await handle_payment_captured(payload["data"])
    elif event_type == "payment.declined":
        await handle_payment_declined(payload["data"])
    
    # 5. Marcar como processado
    await mark_as_processed(event_id)
    
    # 6. Retornar sucesso
    return {"success": True}
```

---

## 🆘 Troubleshooting

### Webhook não está chegando?

1. ✅ Verifique se a URL está configurada na Adiq
2. ✅ Verifique se o servidor está acessível publicamente
3. ✅ Verifique logs do servidor
4. ✅ Teste com ngrok primeiro

### Webhook dá erro 401?

1. ✅ Verifique validação de assinatura
2. ✅ Confirme o secret com a Adiq
3. ✅ Desabilite validação temporariamente para testar

### Webhook dá timeout?

1. ✅ Processe em background
2. ✅ Retorne 200 OK imediatamente
3. ✅ Use filas (Redis, RabbitMQ)

---

## 📚 Recursos

- **Endpoint:** `POST /v1/webhooks/adiq`
- **Teste:** `python test_webhook.py`
- **Logs:** Verifique console do servidor
- **Swagger:** http://localhost:8000/docs

---

**Webhooks configurados e prontos para uso!** 🔔✨
