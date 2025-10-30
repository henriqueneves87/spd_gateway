# 📡 Resumo - Webhook da Adiq

**Data:** 30/10/2025  
**Status:** ⏳ Aguardando configuração pela Adiq

---

## ✅ O Que Descobrimos

### 1. **Endpoint de Configuração**
```
POST /v1/merchant/webhook
```

### 2. **Payload de Configuração**
```json
{
  "postBackUrl": "https://seu-servidor.com/v1/webhooks/adiq",
  "postbackEnabled": true,
  "headers": []
}
```

### 3. **Payload que a Adiq Envia**
```json
{
  "Date": "2025-04-28T15:59:31.6906714",
  "OrderNumber": "0000000001",
  "PaymentId": "020057103504281858290001942369970000000000",
  "PaymentMethod": "Credit",
  "Amount": "690",
  "StatusCode": "0",
  "StatusDescription": "Captura - Sucesso"
}
```

### 4. **Tentativas de Reenvio**
A Adiq tenta enviar o webhook até **6 vezes**:
- 1ª: Imediatamente
- 2ª: Após 5 minutos
- 3ª: Após 30 minutos
- 4ª: Após 1 hora
- 5ª: Após 1.5 horas
- 6ª: Após 2 horas

---

## ❌ Problema Encontrado

**Erro:** 403 Forbidden ao tentar configurar via API

**Possíveis causas:**
1. Credenciais de cliente não têm permissão
2. Apenas admin pode configurar
3. Configuração deve ser feita via portal

---

## 🎯 Solução

### Opção 1: E-mail para Adiq (RECOMENDADO)

Enviar e-mail solicitando configuração:
- ✅ Template pronto em: `docs/EMAIL_ADIQ_WEBHOOK.md`
- ✅ URL de teste: https://webhook.site/833e5a6a-fa12-4230-9606-cce1f23de3e5
- ✅ URL produção: https://spdpay-gateway.onrender.com/v1/webhooks/adiq

### Opção 2: Portal Admin

Se tiver acesso ao portal admin:
1. Acessar: https://admin-spdpaydigital-hml.adiq.io/
2. Menu: Configurações → Webhooks
3. Adicionar URL

---

## 🔧 Nosso Endpoint Está Pronto

```
✅ Endpoint criado: /v1/webhooks/adiq
✅ Processamento implementado
✅ Logs de auditoria funcionando
✅ Atualização de transações funcionando
✅ Pronto para receber webhooks!
```

**Código:**
- `src/api/v1/webhooks.py` - Endpoint
- `src/services/webhook_service.py` - Processamento
- Tabela: `webhook_logs` - Auditoria

---

## 📊 Formato Esperado vs Recebido

### Formato da Documentação Adiq:
```json
{
  "Date": "2025-04-28T15:59:31",
  "OrderNumber": "0000000001",
  "PaymentId": "020057103504281858290001942369970000000000",
  "PaymentMethod": "Credit",
  "Amount": "690",
  "StatusCode": "0",
  "StatusDescription": "Captura - Sucesso"
}
```

### Formato que Recebemos nos Testes:
```json
{
  "eventType": "payment.captured",
  "paymentId": "020048967410301230120007230412810000000000",
  "status": "Captured",
  "authorizationCode": "223899"
}
```

**⚠️ ATENÇÃO:** Formatos diferentes! Precisamos validar qual é o correto.

---

## 🧪 Plano de Testes

### Fase 1: Validação com webhook.site
1. ✅ Solicitar à Adiq configuração do webhook.site
2. ⏳ Fazer pagamento de teste
3. ⏳ Ver payload real que a Adiq envia
4. ⏳ Ajustar nosso código se necessário

### Fase 2: Deploy e Produção
1. ⏳ Deploy no Render
2. ⏳ Configurar URL do Render na Adiq
3. ⏳ Testar com URL real
4. ⏳ Validar processamento automático

---

## 📝 Checklist

- [x] Endpoint de webhook criado
- [x] Processamento implementado
- [x] Logs de auditoria funcionando
- [x] Documentação da Adiq analisada
- [x] Template de e-mail criado
- [x] URL de teste (webhook.site) pronta
- [ ] Solicitar configuração à Adiq
- [ ] Validar formato do payload
- [ ] Deploy no Render
- [ ] Configurar URL produção
- [ ] Testes finais

---

## 🎯 Próximos Passos

### Imediato
1. **Enviar e-mail para Adiq** (template pronto)
2. **Aguardar resposta** sobre como configurar
3. **Testar com webhook.site** quando configurado

### Curto Prazo
1. Deploy no Render
2. Configurar URL definitiva
3. Validar em produção

---

## 📞 Contatos Adiq

- **E-mail:** suporte@adiq.com.br
- **Portal Admin:** https://admin-spdpaydigital-hml.adiq.io/
- **Portal Merchant:** https://portal-spdpaydigital-hml.adiq.io/

---

## 💡 Observações Importantes

1. **Webhook.site é temporário** - Use apenas para validação
2. **Render é gratuito** - Mas tem cold start (15 min inatividade)
3. **Payload pode variar** - Validar formato real quando receber
4. **6 tentativas de reenvio** - Sistema robusto da Adiq
5. **Nosso endpoint é público** - Não requer autenticação (webhook)

---

**Status:** ⏳ Aguardando Adiq configurar webhook  
**Última atualização:** 30/10/2025 11:48
