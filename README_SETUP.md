# 🚀 Spdpay Gateway - Setup Guide

## 📋 Pré-requisitos

- Python 3.11+
- Conta Supabase
- Credenciais Adiq (Homologação)

---

## 🔧 Setup Local

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-supabase

# Adiq (já configurado para HML)
ADIQ_BASE_URL=https://ecommerce-hml.adiq.io
ADIQ_CLIENT_ID=a40a208c-0914-479d-ba17-bbd6e9063991
ADIQ_CLIENT_SECRET=C0A9E2AF-A902-44CA-8E22-762ED9CBA9EE

# Security
JWT_SECRET=seu-secret-super-seguro-aqui
```

### 3. Criar Schema no Supabase

1. Acesse o SQL Editor no Supabase
2. Cole o conteúdo de `src/db/schemas.sql`
3. Execute o script

### 4. Criar Merchant de Teste

```sql
-- No SQL Editor do Supabase
INSERT INTO merchants (name, api_key_hash, is_active)
VALUES (
    'Merchant Teste',
    '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  -- hash de 'test-api-key'
    true
);
```

### 5. Rodar a Aplicação

```bash
# Desenvolvimento
python src/main.py

# Ou com uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000/docs

---

## 🐳 Setup com Docker

```bash
# Build e run
docker-compose up --build

# Em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

---

## 🧪 Testar a API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Criar Invoice

```bash
curl -X POST http://localhost:8000/v1/invoices \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "UUID-DO-MERCHANT",
    "customer_id": "UUID-DO-CUSTOMER",
    "amount": 10000,
    "currency": "BRL",
    "description": "Teste de pagamento"
  }'
```

### 3. Processar Pagamento

Primeiro, tokenize o cartão com Adiq, depois:

```bash
curl -X POST http://localhost:8000/v1/payments \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "UUID-DA-INVOICE",
    "card_token": "TOKEN-DA-ADIQ",
    "cardholder_name": "TESTE APROVADO",
    "expiration_month": "12",
    "expiration_year": "25",
    "security_code": "123",
    "installments": 1,
    "capture_type": "ac"
  }'
```

---

## 📚 Documentação

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Convenções**: `docs/CONVENTIONS.md`
- **Segurança**: `docs/SECURITY.md`
- **Certificação Adiq**: `docs/CERTIFICATION.md`
- **Mapeamento Adiq**: `docs/ADIQ_MAPPING.md`

---

## 🎯 Próximos Passos

1. ✅ Criar merchant e customer no Supabase
2. ✅ Testar autenticação OAuth com Adiq
3. ✅ Testar tokenização de cartão
4. ✅ Processar pagamento de teste
5. ✅ Configurar webhook da Adiq
6. ✅ Executar testes de certificação (`docs/CERTIFICATION.md`)

---

## 🔐 Cartões de Teste

Ver `tests/fixtures/test_cards.py` para cartões de teste da Adiq.

**Visa Aprovado:**
- PAN: 4761739001010036
- CVV: 123
- Validade: 12/25

**Emails Antifraude:**
- accept@test.com - Aprovado
- reject@test.com - Rejeitado
- review@test.com - Revisão manual

---

## 🐛 Troubleshooting

### Erro de autenticação Adiq
- Verifique as credenciais no `.env`
- Confirme que está usando a URL de HML

### Erro de conexão Supabase
- Verifique URL e KEY no `.env`
- Confirme que o schema foi criado

### API Key inválida
- Verifique o hash no banco: `echo -n 'test-api-key' | sha256sum`
- Confirme que o merchant está ativo

---

**Pronto para começar!** 🚀
