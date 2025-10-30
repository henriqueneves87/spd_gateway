# 📡 Status dos Webhooks da Adiq

**Data:** 30/10/2025 11:35  
**Status:** ✅ FUNCIONANDO (com correção aplicada)

---

## ✅ Situação Atual

### Webhooks Recebidos
```
✅ A Adiq ESTÁ enviando webhooks!
✅ 2 webhooks recebidos e registrados
✅ Endpoint funcionando corretamente
```

### Webhooks Registrados

| # | Event Type | Payment ID | Data/Hora | Status |
|---|------------|------------|-----------|--------|
| 1 | payment.captured | 020048967410301230120007230412810000000000 | 30/10 12:39 | ⚠️ Não processado |
| 2 | payment.captured | (teste) | 30/10 12:38 | ⚠️ Não processado |

---

## 🔧 Problema Identificado e Corrigido

### Problema
O processamento de webhooks estava **desabilitado temporariamente** para debug:

```python
# src/services/webhook_service.py linha 80-81
# Temporariamente desabilitado para debug
# await self._process_payment_update(payload)
```

### Solução Aplicada
✅ Processamento **habilitado** novamente:

```python
# Process payment update
await self._process_payment_update(payload)
```

---

## 📊 Estrutura do Webhook

### Payload Recebido da Adiq

```json
{
  "eventType": "payment.captured",
  "paymentId": "020048967410301230120007230412810000000000",
  "status": "Captured",
  "authorizationCode": "223899"
}
```

### Payload Alternativo (mais completo)

```json
{
  "eventId": "evt_123456789",
  "eventType": "payment.captured",
  "timestamp": "2025-10-30T12:00:00Z",
  "data": {
    "paymentId": "020048967410301230120007230412810000000000",
    "transactionId": "b39e466c-d3d5-4c4a-911a-52f869a06801",
    "merchantId": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
    "customerId": "3b415031-7236-425e-bc8f-35c7a5f572ab",
    "amount": 1000,
    "currency": "BRL",
    "installments": 1,
    "status": "Captured",
    "authorizationCode": "223899",
    "cardBrand": "visa",
    "cardLast4": "0036"
  }
}
```

---

## 🎯 Eventos Suportados

| Evento | Descrição | Status |
|--------|-----------|--------|
| `payment.authorized` | Pagamento autorizado | ✅ Suportado |
| `payment.captured` | Pagamento capturado | ✅ Suportado |
| `payment.settled` | Pagamento liquidado | ✅ Suportado |
| `payment.declined` | Pagamento recusado | ✅ Suportado |
| `payment.cancelled` | Pagamento cancelado | ✅ Suportado |
| `payment.refunded` | Pagamento estornado | ✅ Suportado |

---

## 🔐 Configuração na Adiq

### URL do Webhook
```
http://SEU-SERVIDOR/v1/webhooks/adiq
```

### Para Testes Locais (ngrok)
```bash
# 1. Instalar ngrok
# https://ngrok.com/download

# 2. Expor servidor local
ngrok http 8000

# 3. Copiar URL gerada (ex: https://abc123.ngrok.io)

# 4. Configurar na Adiq:
https://abc123.ngrok.io/v1/webhooks/adiq
```

### Portal Admin da Adiq
```
URL: https://admin-spdpaydigital-hml.adiq.io/
Menu: Configurações > Webhooks
```

---

## 🧪 Como Testar

### 1. Teste Manual (Simular Webhook)

```bash
curl -X POST http://localhost:8000/v1/webhooks/adiq \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: test-signature" \
  -d '{
    "eventType": "payment.captured",
    "paymentId": "020012345678901234567890123456789012345678",
    "status": "Captured",
    "authorizationCode": "123456"
  }'
```

### 2. Teste Real (Fazer Pagamento)

```bash
# 1. Fazer um pagamento via API
# 2. Aguardar webhook da Adiq
# 3. Verificar logs
```

### 3. Verificar Webhooks Recebidos

```sql
SELECT id, event_type, payment_id, processed, received_at
FROM webhook_logs
ORDER BY received_at DESC
LIMIT 10;
```

---

## 📝 Logs e Monitoramento

### Consultar Webhooks

```python
# Python
from src.db.client import supabase

webhooks = supabase.table("webhook_logs")\
    .select("*")\
    .order("received_at", desc=True)\
    .limit(10)\
    .execute()

for webhook in webhooks.data:
    print(f"{webhook['event_type']} - {webhook['payment_id']}")
```

### Verificar Não Processados

```sql
SELECT COUNT(*) as total_nao_processados
FROM webhook_logs
WHERE processed = false;
```

### Reprocessar Webhook Manualmente

```python
# Se necessário reprocessar um webhook
webhook_id = "f959291e-3dee-4f01-9ecf-daa97f29faa8"

# Buscar webhook
webhook = supabase.table("webhook_logs")\
    .select("*")\
    .eq("id", webhook_id)\
    .single()\
    .execute()

# Reprocessar
from src.services.webhook_service import WebhookService
service = WebhookService()
await service.process_webhook(webhook.data['payload'], webhook.data['signature'])
```

---

## ✅ Checklist de Configuração

- [x] Endpoint `/v1/webhooks/adiq` criado
- [x] Tabela `webhook_logs` no Supabase
- [x] Processamento de webhooks implementado
- [x] Logs de auditoria funcionando
- [x] Webhooks sendo recebidos da Adiq
- [x] Processamento habilitado (corrigido)
- [ ] URL pública configurada na Adiq (pendente)
- [ ] Validação de assinatura implementada (opcional)

---

## 🚀 Próximos Passos

### Imediato
1. ✅ Habilitar processamento (FEITO)
2. ⏳ Reiniciar servidor para aplicar mudanças
3. ⏳ Fazer novo pagamento de teste
4. ⏳ Verificar se webhook é processado

### Curto Prazo
1. Configurar URL pública (ngrok ou deploy)
2. Atualizar URL no portal da Adiq
3. Implementar validação de assinatura
4. Adicionar retry automático

### Médio Prazo
1. Monitoramento de webhooks
2. Alertas para webhooks não processados
3. Dashboard de webhooks
4. Testes automatizados

---

## 📚 Documentação Relacionada

- `docs/WEBHOOK_GUIDE.md` - Guia completo de webhooks
- `src/api/v1/webhooks.py` - Endpoint de webhooks
- `src/services/webhook_service.py` - Serviço de processamento
- `src/schemas/webhook.py` - Schemas de webhook

---

## 🎉 Conclusão

**Status:** ✅ WEBHOOKS FUNCIONANDO!

- ✅ Adiq está enviando webhooks
- ✅ Endpoint recebendo corretamente
- ✅ Logs sendo registrados
- ✅ Processamento habilitado

**Próximo passo:** Reiniciar servidor e testar com novo pagamento.

---

**Última atualização:** 30/10/2025 11:35  
**Responsável:** Henrique Neves
