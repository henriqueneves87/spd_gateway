# 🎯 Roteiro de Certificação Adiq - Spdpay Gateway

**Versão:** 1.0.0  
**Data:** 2025-10-29  
**Status:** Em Progresso

---

## 📋 Visão Geral

Este documento contém o roteiro completo para certificação do Spdpay Gateway junto à Adiq.

**Ambiente:** Homologação  
**Base URL:** `https://ecommerce-hml.adiq.io`

---

## 🔑 Credenciais de Homologação

### Portal Adiq

- **Admin Portal:** https://admin-spdpaydigital-hml.adiq.io/
- **Merchant Portal:** https://portal-spdpaydigital-hml.adiq.io/
- **Credenciamento:** https://credenciamento-spdpaydigital-hml.adiq.io/

**Usuário:** speed.pay  
**Senha:** Mudar@123

### API Gateway

```
ClientId: a40a208c-0914-479d-ba17-bbd6e9063991
ClientSecret: C0A9E2AF-A902-44CA-8E22-762ED9CBA9EE
```

---

## 💳 Cartões de Teste

| Bandeira | PAN | Validade | CVV |
|----------|-----|----------|-----|
| **Mastercard** | 5201561050025011 | 09/24 | 123 |
| **Visa** | 4761739001010036 | 12/25 | 123 |
| **Amex** | 376470814541000 | 10/25 | 1234 |
| **Hipercard** | 6062828898541988 | 09/25 | 123 |
| **Elo** | 5067224275805500 | 11/25 | 123 |

**Nota:** Executar testes com apenas uma bandeira é suficiente para certificação.

---

## 📝 Roteiro de Testes

### 1️⃣ Autenticação OAuth2

**Objetivo:** Obter token de acesso para API.

#### Request

```bash
POST https://ecommerce-hml.adiq.io/auth/oauth2/v1/token
Authorization: Basic <base64(clientId:clientSecret)>
Content-Type: application/json

{
  "grantType": "client_credentials"
}
```

#### Response Esperado

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### Validações

- [ ] Status code 200
- [ ] Token retornado
- [ ] Token válido por 1 hora
- [ ] Refresh funciona antes da expiração

---

### 2️⃣ Tokenização de Cartão

**Objetivo:** Converter PAN em token seguro.

#### Request

```bash
POST https://ecommerce-hml.adiq.io/v1/tokens/cards
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "cardNumber": "4761739001010036"
}
```

#### Response Esperado

```json
{
  "numberToken": "D391DFDF-91D6-43D1-A98F-1B9E4FE57B10"
}
```

#### Validações

- [ ] Status code 200
- [ ] Token UUID retornado
- [ ] Token único por PAN
- [ ] Token reutilizável

**Registrar:**
- Number Token: ___________________________

---

### 3️⃣ Armazenamento em Cofre (Vault)

**Objetivo:** Salvar cartão tokenizado no cofre Adiq.

#### Request

```bash
POST https://ecommerce-hml.adiq.io/v1/vaults/cards
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "numberToken": "D391DFDF-91D6-43D1-A98F-1B9E4FE57B10",
  "brand": "visa",
  "cardholderName": "Jose da Silva",
  "expirationMonth": "12",
  "expirationYear": "25",
  "securityCode": "123",
  "verifyCard": true
}
```

#### Response Esperado

```json
{
  "vaultId": "e25393f5-5732-4f38-a4ec-5e60f0b4b3e5",
  "brand": "visa",
  "last4": "0036",
  "status": "ACTIVE"
}
```

#### Validações

- [ ] Status code 200
- [ ] VaultId retornado
- [ ] Cartão verificado (verifyCard=true)
- [ ] Brand e last4 corretos

**Registrar:**
- Vault ID: ___________________________

---

### 4️⃣ Pagamento com Captura Direta (AC)

**Objetivo:** Autorizar e capturar pagamento em uma única transação.

#### Request

```bash
POST https://ecommerce-hml.adiq.io/v2/payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "payment": {
    "transactionType": "Credit",
    "amount": 10000,
    "currencyCode": "brl",
    "productType": "avista",
    "installments": 1,
    "captureType": "ac",
    "recurrent": false
  },
  "cardInfo": {
    "numberToken": "D391DFDF-91D6-43D1-A98F-1B9E4FE57B10",
    "brand": "visa",
    "cardholderName": "Jose da Silva",
    "expirationMonth": "12",
    "expirationYear": "25",
    "securityCode": "123"
  },
  "sellerInfo": {
    "orderNumber": "ORDER-12345",
    "softDescriptor": "PAG*SPDPAY"
  }
}
```

#### Response Esperado

```json
{
  "paymentId": "020004284405202219490000023429850000000000",
  "authorizationCode": "027872",
  "status": "APPROVED",
  "amount": 10000,
  "captureType": "ac"
}
```

#### Validações

- [ ] Status code 200
- [ ] Status = APPROVED
- [ ] Authorization code retornado
- [ ] Payment ID retornado
- [ ] Amount correto

**Registrar:**
- Payment ID: ___________________________
- Authorization Code: ___________________________

---

### 5️⃣ Pagamento Parcelado

**Objetivo:** Processar pagamento em múltiplas parcelas.

#### Request

```bash
POST https://ecommerce-hml.adiq.io/v2/payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "payment": {
    "transactionType": "Credit",
    "amount": 30000,
    "currencyCode": "brl",
    "productType": "parcelado_loja",
    "installments": 3,
    "captureType": "ac",
    "recurrent": false
  },
  "cardInfo": {
    "numberToken": "D391DFDF-91D6-43D1-A98F-1B9E4FE57B10",
    "brand": "visa",
    "cardholderName": "Jose da Silva",
    "expirationMonth": "12",
    "expirationYear": "25",
    "securityCode": "123"
  },
  "sellerInfo": {
    "orderNumber": "ORDER-12346",
    "softDescriptor": "PAG*SPDPAY"
  }
}
```

#### Validações

- [ ] Status code 200
- [ ] Installments = 3
- [ ] Amount correto
- [ ] Status = APPROVED

**Registrar:**
- Payment ID: ___________________________
- Authorization Code: ___________________________

---

### 6️⃣ Testes de Antifraude

**Objetivo:** Validar integração com sistema antifraude.

#### 6.1 Transação Aprovada

**E-mail:** accept@test.com

```json
{
  "customer": {
    "email": "accept@test.com",
    "documentType": "cpf",
    "documentNumber": "05002827063",
    "firstName": "JOAO",
    "lastName": "SILVA"
  }
}
```

**Resultado Esperado:** APPROVED

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________

#### 6.2 Transação Rejeitada

**E-mail:** reject@test.com

```json
{
  "customer": {
    "email": "reject@test.com",
    "documentType": "cpf",
    "documentNumber": "05002827063",
    "firstName": "JOAO",
    "lastName": "SILVA"
  }
}
```

**Resultado Esperado:** DECLINED (Antifraude)

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________

#### 6.3 Transação em Revisão

**E-mail:** review@test.com

```json
{
  "customer": {
    "email": "review@test.com",
    "documentType": "cpf",
    "documentNumber": "05002827063",
    "firstName": "JOAO",
    "lastName": "SILVA"
  }
}
```

**Resultado Esperado:** PENDING (Manual Review)

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________

---

### 7️⃣ Testes 3DS (3D Secure)

**Documentação:** https://cardinaldocs.atlassian.net/wiki/spaces/CCen/pages/903577725/EMV+3DS+Test+Cases

#### 7.1 Test Case 1: Successful Frictionless Authentication

**Objetivo:** Autenticação 3DS sem desafio (frictionless).

```json
{
  "sellerInfo": {
    "code3DS": "6FBF4568-7BC3-4C7C-8D1B-71F6B7FC8BAB",
    "urlSite3DS": "http://127.0.0.1:3000",
    "programProtocol": "2.0.2"
  },
  "deviceInfo": {
    "ipAddress": "127.0.0.1",
    "httpAcceptBrowserValue": "text/html,application/xhtml+xml",
    "httpBrowserColorDepth": 24,
    "httpBrowserJavaEnabled": "N",
    "httpBrowserJavaScriptEnabled": true,
    "httpBrowserLanguage": "pt-BR",
    "httpBrowserScreenHeight": 1080,
    "httpBrowserScreenWidth": 1920,
    "httpBrowserTimeDifference": 180,
    "userAgentBrowserValue": "Mozilla/5.0..."
  }
}
```

**Resultado Esperado:** APPROVED com ECI=05

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________
- ECI: ___________________________

#### 7.2 Test Case 2: Failed Frictionless Authentication

**Resultado Esperado:** DECLINED (3DS Failed)

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________

#### 7.3 Test Case 9: Successful Step Up Authentication

**Objetivo:** Autenticação com desafio (challenge).

**Resultado Esperado:** Redirect para challenge → APPROVED

**Registrar:**
- Authorization Code: ___________________________
- Payment ID: ___________________________
- Challenge URL: ___________________________

---

### 8️⃣ Consulta de Pagamento

**Objetivo:** Verificar status de pagamento existente.

#### Request

```bash
GET https://ecommerce-hml.adiq.io/v1/payments/{paymentId}
Authorization: Bearer <access_token>
```

#### Response Esperado

```json
{
  "paymentId": "020004284405202219490000023429850000000000",
  "status": "APPROVED",
  "amount": 10000,
  "authorizationCode": "027872",
  "createdAt": "2025-10-29T10:30:00Z"
}
```

#### Validações

- [ ] Status code 200
- [ ] Dados consistentes com criação
- [ ] Histórico de transições disponível

---

### 9️⃣ Webhook de Confirmação

**Objetivo:** Receber notificações assíncronas da Adiq.

#### Configuração

1. Registrar URL do webhook no portal Adiq
2. Implementar endpoint: `POST /v1/webhooks/adiq`
3. Validar assinatura HMAC

#### Payload Esperado

```json
{
  "eventType": "PAYMENT_APPROVED",
  "paymentId": "020004284405202219490000023429850000000000",
  "authorizationCode": "027872",
  "status": "APPROVED",
  "amount": 10000,
  "timestamp": "2025-10-29T10:30:00Z"
}
```

#### Validações

- [ ] Webhook recebido
- [ ] Assinatura válida
- [ ] Idempotência funcionando
- [ ] Status atualizado corretamente
- [ ] Response 200 retornado

---

## 📊 Planilha de Resultados

### Transações Básicas

| Teste | Order Number | Payment ID | Auth Code | Vault ID | Status |
|-------|--------------|------------|-----------|----------|--------|
| Tokenização | - | - | - | | ⬜ |
| Vault | - | - | - | | ⬜ |
| Pagamento AC | ORDER-12345 | | | - | ⬜ |
| Parcelado 3x | ORDER-12346 | | | - | ⬜ |

### Antifraude

| E-mail | Payment ID | Auth Code | Status Esperado | Status Real |
|--------|------------|-----------|-----------------|-------------|
| accept@test.com | | | APPROVED | ⬜ |
| reject@test.com | | | DECLINED | ⬜ |
| review@test.com | | | PENDING | ⬜ |

### 3DS

| Test Case | Payment ID | Auth Code | ECI | Status |
|-----------|------------|-----------|-----|--------|
| TC1: Frictionless Success | | | 05 | ⬜ |
| TC2: Frictionless Failed | | | - | ⬜ |
| TC9: Step Up Success | | | 05 | ⬜ |

---

## ✅ Checklist de Certificação

### Pré-requisitos

- [ ] Ambiente de homologação configurado
- [ ] Credenciais Adiq obtidas
- [ ] Cartões de teste disponíveis
- [ ] Logs estruturados implementados
- [ ] Tratamento de erros implementado

### Testes Obrigatórios

- [ ] OAuth2 - Autenticação
- [ ] Tokenização de cartão
- [ ] Vault - Armazenamento seguro
- [ ] Pagamento à vista (AC)
- [ ] Pagamento parcelado
- [ ] Antifraude - Accept
- [ ] Antifraude - Reject
- [ ] Antifraude - Review
- [ ] 3DS - Frictionless Success
- [ ] 3DS - Step Up Challenge
- [ ] Consulta de pagamento
- [ ] Webhook - Recebimento
- [ ] Webhook - Idempotência

### Documentação

- [ ] Planilha de testes preenchida
- [ ] Screenshots de transações
- [ ] Logs de requisições/respostas
- [ ] Evidências de webhooks

### Envio para Adiq

- [ ] Planilha completa
- [ ] Evidências anexadas
- [ ] E-mail enviado para certificação
- [ ] Aguardar aprovação (5-7 dias úteis)

---

## 🚀 Automação de Testes

### Script de Certificação

```bash
# Rodar todos os testes de certificação
pytest tests/certification/ -v

# Gerar relatório
pytest tests/certification/ --html=report.html

# Apenas testes críticos
pytest tests/certification/ -m critical
```

### Exemplo de Teste Automatizado

```python
# tests/certification/test_payment_flow.py
import pytest
from src.adapters.adiq import AdiqClient
from tests.fixtures.test_cards import TEST_CARDS

@pytest.mark.asyncio
@pytest.mark.certification
async def test_full_payment_flow():
    """Test complete payment flow: token → vault → payment"""
    client = AdiqClient()
    card = TEST_CARDS["visa"]
    
    # 1. Authenticate
    token = await client.authenticate()
    assert token is not None
    
    # 2. Tokenize
    card_token = await client.tokenize_card(card["pan"])
    assert card_token is not None
    
    # 3. Vault
    vault_id = await client.create_vault(
        number_token=card_token,
        brand=card["brand"],
        cardholder_name="Jose da Silva",
        expiration_month=card["expiration_month"],
        expiration_year=card["expiration_year"],
        security_code=card["cvv"]
    )
    assert vault_id is not None
    
    # 4. Payment
    payment = await client.create_payment(
        amount=10000,
        number_token=card_token,
        brand=card["brand"],
        cardholder_name="Jose da Silva",
        expiration_month=card["expiration_month"],
        expiration_year=card["expiration_year"],
        security_code=card["cvv"],
        order_number="TEST-001"
    )
    
    assert payment["status"] == "APPROVED"
    assert payment["authorizationCode"] is not None
    assert payment["paymentId"] is not None
    
    print(f"✅ Payment ID: {payment['paymentId']}")
    print(f"✅ Auth Code: {payment['authorizationCode']}")
```

---

## 📞 Suporte

### Contatos Adiq

- **E-mail:** suporte@adiq.io
- **Portal:** https://admin-spdpaydigital-hml.adiq.io/
- **Documentação:** https://developers.adiq.io/manual/ecommerce

### Dúvidas Frequentes

**Q: Quanto tempo leva a certificação?**  
A: 5-7 dias úteis após envio da documentação completa.

**Q: Preciso testar todas as bandeiras?**  
A: Não, uma bandeira é suficiente para certificação inicial.

**Q: E se um teste falhar?**  
A: Documente o erro, corrija e reenvie apenas os testes afetados.

**Q: Webhooks são obrigatórios?**  
A: Sim, são essenciais para atualização de status assíncrona.

---

## 🎉 Próximos Passos

Após certificação aprovada:

1. **Produção:** Solicitar credenciais de produção
2. **Go-live:** Configurar ambiente produtivo
3. **Monitoramento:** Ativar alertas e dashboards
4. **Suporte:** Preparar equipe para operação

---

**Boa sorte com a certificação! 🚀**
