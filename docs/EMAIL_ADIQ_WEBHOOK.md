# 📧 E-mail para Adiq - Configuração de Webhook

---

**Para:** suporte@adiq.com.br  
**Assunto:** Configuração de Webhook - Spdpay Gateway (Client ID: A40A208C-0914-479D-BA17-BBD6E9063991)

---

Olá equipe Adiq,

Estamos finalizando a integração do **Spdpay Gateway** com a Adiq e precisamos configurar o webhook para receber notificações de transações.

## 📋 Informações da Integração

**Credenciais:**
- **Client ID:** A40A208C-0914-479D-BA17-BBD6E9063991
- **Ambiente:** Homologação (HML)
- **Base URL:** https://ecommerce-hml.adiq.io

**Status da Integração:**
- ✅ Autenticação OAuth2 funcionando
- ✅ Tokenização de cartões funcionando
- ✅ Pagamentos sendo aprovados (Visa, Mastercard, Elo, Amex)
- ⏳ Webhook pendente de configuração

---

## 🎯 Solicitação

Tentamos configurar o webhook via API conforme documentação:

```
POST /v1/merchant/webhook
Authorization: Bearer {token}

{
  "postBackUrl": "https://webhook.site/833e5a6a-fa12-4230-9606-cce1f23de3e5",
  "postbackEnabled": true,
  "headers": []
}
```

Porém recebemos **403 Forbidden**, indicando que não temos permissão para configurar via API.

---

## 📍 URLs do Webhook

### Para Testes Imediatos (webhook.site)
```
https://webhook.site/833e5a6a-fa12-4230-9606-cce1f23de3e5
```

Visualizar em tempo real:
```
https://webhook.site/#!/833e5a6a-fa12-4230-9606-cce1f23de3e5
```

### Para Produção (após validação)
```
https://spdpay-gateway.onrender.com/v1/webhooks/adiq
```

---

## 🔔 Eventos Solicitados

Gostaríamos de receber notificações para todos os eventos de pagamento:

- ✅ Autorização (AC e PA)
- ✅ Captura
- ✅ Cancelamento
- ✅ Estorno
- ✅ Liquidação

Conforme documentação, esperamos receber o seguinte payload:

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

---

## 🧪 Plano de Testes

1. **Fase 1 - Validação (webhook.site):**
   - Configurar webhook.site temporariamente
   - Realizar transações de teste
   - Validar formato do payload
   - Confirmar recebimento das notificações

2. **Fase 2 - Produção:**
   - Configurar URL definitiva do Render
   - Realizar testes finais
   - Validar processamento automático

---

## ❓ Perguntas

1. **Como devemos proceder para configurar o webhook?**
   - Via portal admin?
   - Via API com credenciais diferentes?
   - Via solicitação ao suporte?

2. **Qual o prazo para configuração?**
   - Precisamos para completar a certificação

3. **Headers customizados são necessários?**
   - Ou apenas a URL é suficiente?

4. **Há alguma whitelist de IPs?**
   - Render usa IPs dinâmicos

---

## 📞 Contato

**Desenvolvedor:** Henrique Neves  
**Empresa:** Spdpay  
**E-mail:** [seu-email]  
**Telefone:** [seu-telefone]

---

## 📚 Documentação de Referência

Estamos seguindo a documentação:
- **Notification API:** POST /v1/merchant/webhook
- **Payload esperado:** Conforme especificação da documentação

---

Aguardamos retorno para darmos continuidade à certificação.

Atenciosamente,  
**Henrique Neves**  
Spdpay Gateway

---

## 📎 Anexos

- Logs de autenticação (sucesso)
- Logs de pagamentos (aprovados)
- Tentativa de configuração via API (403 Forbidden)

