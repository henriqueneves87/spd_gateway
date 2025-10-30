# 💳 Spdpay Gateway

[![GitHub](https://img.shields.io/github/license/henriqueneves87/spd_gateway)](https://github.com/henriqueneves87/spd_gateway/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/henriqueneves87/spd_gateway)](https://github.com/henriqueneves87/spd_gateway/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/henriqueneves87/spd_gateway)](https://github.com/henriqueneves87/spd_gateway/issues)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

Gateway de pagamentos integrado com Adiq para processamento de transações de cartão de crédito.

> 🚀 **Status:** Produção | ✅ Certificação Adiq em andamento

## 🚀 Quick Start

### 1. Iniciar o Servidor

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testar com Postman

1. Importe: `docs/Spdpay_Gateway.postman_collection.json`
2. Configure environment conforme `docs/POSTMAN_GUIDE.md`
3. Execute os testes!

### 3. Ou use o Swagger

Acesse: http://localhost:8000/docs

---

## 📚 Documentação

### Para Desenvolvedores
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Documentação completa da API
- **[Postman Guide](docs/POSTMAN_GUIDE.md)** - Guia de uso do Postman
- **[Fluxo de Pagamento](docs/FLUXO_PAGAMENTO.md)** - Fluxo detalhado de processamento

### Para Certificação
- **[Certification Guide](docs/CERTIFICATION.md)** - Roteiro de certificação Adiq
- **[Adiq Mapping](docs/ADIQ_MAPPING.md)** - Mapeamento Adiq ↔ Spdpay

### Para Contribuidores
- **[Conventions](docs/CONVENTIONS.md)** - Convenções de código
- **[Security](docs/SECURITY.md)** - Política de segurança PCI DSS
- **[Contributing](docs/CONTRIBUTING.md)** - Guia de contribuição

---

## 🎯 Funcionalidades

✅ **Processamento de Pagamentos**
- Cartão de crédito (Visa, Mastercard, Elo, Amex, Hipercard)
- À vista e parcelado (até 12x)
- Auto-captura e pré-autorização

✅ **Tokenização Automática**
- Aceita PAN (número do cartão) diretamente
- Gateway tokeniza automaticamente via Adiq
- Ou use tokens pré-gerados

✅ **Modelo Subcredenciadora**
- Credenciais Adiq por merchant
- Isolamento completo entre merchants
- Suporte a múltiplos sellers

✅ **Segurança PCI DSS**
- Dados sensíveis nunca armazenados
- Tokenização obrigatória
- Logs sanitizados

---

## 🔧 Tecnologias

- **FastAPI** - Framework web
- **Supabase** - Banco de dados
- **Adiq** - Processador de pagamentos
- **Pydantic** - Validação de dados
- **httpx** - Cliente HTTP assíncrono

---

## 📦 Instalação

### Pré-requisitos
- Python 3.11+
- Conta Supabase
- Credenciais Adiq (Homologação ou Produção)

### Setup

```bash
# 1. Clone o repositório
git clone https://github.com/henriqueneves87/spd_gateway.git
cd spd_gateway

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edite .env com suas credenciais

# 4. Inicie o servidor
uvicorn src.main:app --reload
```

---

## 🎴 Cartões de Teste

### Visa
- **PAN:** 4761739001010036
- **Validade:** 12/25
- **CVV:** 123

### Mastercard
- **PAN:** 5201561050025011
- **Validade:** 12/25
- **CVV:** 123

---

## 🧪 Testes Automatizados

### Gerar Tokens Frescos

```bash
python gerar_token.py
```

### Executar Testes de Certificação

```bash
python run_tests.py
```

**Nota:** Tokens expiram em 10 minutos. Gere novos antes de cada execução.

---

## 📊 Endpoints Principais

### Invoices
- `POST /v1/invoices` - Criar invoice
- `GET /v1/invoices/{id}` - Buscar invoice
- `GET /v1/invoices?merchant_id={id}` - Listar invoices

### Payments
- `POST /v1/payments/` - Processar pagamento
- `GET /v1/payments/{id}` - Buscar pagamento

### Health
- `GET /health` - Status da API

---

## 🔐 Autenticação

Todas as requisições requerem API Key:

```http
X-API-Key: password
```

---

## 🌍 Ambientes

### Homologação (HML)
```
Base URL: https://ecommerce-hml.adiq.io
```

### Produção
```
Base URL: https://ecommerce.adiq.io
```

**Configurar em:** `.env` → `ADIQ_BASE_URL`

---

## 📝 Exemplo de Uso

### 1. Criar Invoice

```bash
curl -X POST http://localhost:8000/v1/invoices \
  -H "X-API-Key: password" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "fb93c667-fbab-47ea-b3c7-9dd27231244a",
    "customer_id": "3b415031-7236-425e-bc8f-35c7a5f572ab",
    "amount": 1000,
    "currency": "BRL",
    "description": "Teste"
  }'
```

### 2. Processar Pagamento

```bash
curl -X POST http://localhost:8000/v1/payments/ \
  -H "X-API-Key: password" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "UUID-DA-INVOICE",
    "pan": "4761739001010036",
    "brand": "visa",
    "cardholder_name": "JOSE DA SILVA",
    "expiration_month": "12",
    "expiration_year": "25",
    "security_code": "123",
    "installments": 1,
    "capture_type": "ac"
  }'
```

---

## 🎯 Status do Projeto

✅ **Gateway 100% funcional**  
✅ **Integração com Adiq OK**  
✅ **Pagamentos sendo aprovados**  
✅ **Testes automatizados prontos**  
✅ **Documentação completa**  
⏳ **Aguardando credenciais oficiais para certificação**

---

## 📞 Suporte

- **Documentação:** `docs/`
- **Issues:** GitHub Issues
- **Email:** suporte@spdpay.com

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Adiq** - Processador de pagamentos
- **Supabase** - Banco de dados
- **FastAPI** - Framework web

---

**Desenvolvido com ❤️ pela equipe Spdpay**
