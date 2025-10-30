# 🧪 Testes do Spdpay Gateway

Testes de integração e validação do gateway.

---

## 📋 Testes Disponíveis

### `test_swagger_flow.py`
Simula exatamente o fluxo do Swagger UI.

**O que testa:**
- Criação de invoice
- Processamento de pagamento com PAN
- Tokenização automática
- Resposta completa da API

**Uso:**
```bash
python tests/test_swagger_flow.py
```

**Quando usar:**
- Para validar que o fluxo do Swagger funciona
- Debug de problemas reportados via Swagger
- Teste rápido end-to-end

---

### `test_payment_and_webhook.py`
Teste completo: pagamento + simulação de webhook.

**O que testa:**
- Criação de invoice
- Processamento de pagamento
- Simulação de webhook da Adiq
- Atualização de status

**Uso:**
```bash
python tests/test_payment_and_webhook.py
```

**Quando usar:**
- Testar fluxo completo com webhooks
- Validar atualização de status via webhook
- Debug de processamento de webhooks

---

### `test_webhook_simple.py`
Teste simples de webhook (apenas endpoint).

**O que testa:**
- Endpoint `/v1/webhooks/adiq`
- Recebimento de payload
- Logging básico

**Uso:**
```bash
python tests/test_webhook_simple.py
```

**Quando usar:**
- Validar que o endpoint de webhook responde
- Debug rápido de webhooks
- Testar sem criar pagamento real

---

## 🎯 Testes de Certificação

Para rodar os testes oficiais de certificação da Adiq:

```bash
python run_tests.py
```

**Pré-requisitos:**
1. Gerar tokens frescos: `python scripts/gerar_token.py`
2. Atualizar tokens no `run_tests.py`
3. Servidor rodando: `uvicorn src.main:app --reload`

---

## 📊 Estrutura de Testes

```
tests/
├── README.md                      # Este arquivo
├── test_swagger_flow.py           # Simula Swagger
├── test_payment_and_webhook.py    # Teste completo
└── test_webhook_simple.py         # Teste simples webhook
```

---

## ✅ Checklist de Testes

Antes de fazer deploy ou certificação:

- [ ] `test_swagger_flow.py` passa
- [ ] `test_payment_and_webhook.py` passa
- [ ] `run_tests.py` executa todos os casos
- [ ] Swagger UI funciona manualmente
- [ ] Postman collection funciona

---

## 🆘 Troubleshooting

### Teste falha com "Token inválido"
```bash
# Gerar novos tokens
python scripts/gerar_token.py
```

### Teste falha com "Connection refused"
```bash
# Verificar se servidor está rodando
uvicorn src.main:app --reload
```

### Teste falha com "Invoice já paga"
- Cada invoice só pode ser usada uma vez
- Testes criam novas invoices automaticamente

---

## 📚 Mais Informações

- **Documentação da API:** `docs/API_DOCUMENTATION.md`
- **Guia do Swagger:** `docs/SWAGGER_GUIDE.md`
- **Guia do Postman:** `docs/POSTMAN_GUIDE.md`
- **Guia de Webhooks:** `docs/WEBHOOK_GUIDE.md`
