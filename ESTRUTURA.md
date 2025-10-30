# 📁 Estrutura do Projeto - Spdpay Gateway

## 🗂️ Organização de Pastas

```
spdpay_gateway/
│
├── 📂 src/                      # Código fonte principal
│   ├── adapters/                # Integrações externas (Adiq)
│   ├── api/                     # Endpoints FastAPI
│   │   └── v1/                  # API versão 1
│   ├── core/                    # Configurações e utilitários
│   ├── db/                      # Cliente Supabase
│   ├── schemas/                 # Modelos Pydantic
│   └── services/                # Lógica de negócio
│
├── 📂 docs/                     # Documentação completa
│   ├── API_DOCUMENTATION.md     # Documentação da API
│   ├── SWAGGER_GUIDE.md         # Guia do Swagger
│   ├── POSTMAN_GUIDE.md         # Guia do Postman
│   ├── WEBHOOK_GUIDE.md         # Guia de Webhooks
│   ├── ADIQ_MAPPING.md          # Mapeamento Adiq ↔ Spdpay
│   ├── CERTIFICATION.md         # Roteiro de certificação
│   ├── SECURITY.md              # Política de segurança
│   ├── CONVENTIONS.md           # Convenções de código
│   ├── CONTRIBUTING.md          # Guia de contribuição
│   ├── CHANGELOG.md             # Histórico de mudanças
│   └── Spdpay_Gateway.postman_collection.json
│
├── 📂 scripts/                  # Scripts utilitários
│   ├── README.md                # Documentação dos scripts
│   ├── gerar_token.py           # Gerar tokens de teste
│   └── convert_excel_to_json.py # Converter planilha
│
├── 📂 tests/                    # Testes de integração
│   ├── README.md                # Documentação dos testes
│   ├── test_swagger_flow.py     # Simula fluxo Swagger
│   ├── test_payment_and_webhook.py  # Teste completo
│   └── test_webhook_simple.py   # Teste simples webhook
│
├── 📄 run_tests.py              # Script principal de testes
├── 📄 README.md                 # Visão geral do projeto
├── 📄 QUICK_START.md            # Guia de início rápido
├── 📄 SESSAO_COMPLETA.md        # Resumo da sessão de desenvolvimento
├── 📄 ESTRUTURA.md              # Este arquivo
├── 📄 requirements.txt          # Dependências Python
├── 📄 .env.example              # Exemplo de variáveis de ambiente
└── 📄 .gitignore                # Arquivos ignorados pelo Git
```

---

## 🎯 Arquivos Principais

### Código Fonte

| Arquivo | Descrição |
|---------|-----------|
| `src/main.py` | Aplicação FastAPI principal |
| `src/adapters/adiq.py` | Cliente da API Adiq |
| `src/services/payment_service.py` | Lógica de pagamentos |
| `src/services/invoice_service.py` | Lógica de invoices |
| `src/services/webhook_service.py` | Processamento de webhooks |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | Visão geral e setup |
| `QUICK_START.md` | Guia de 5 minutos |
| `docs/API_DOCUMENTATION.md` | Documentação completa da API |
| `docs/SWAGGER_GUIDE.md` | Como usar o Swagger |
| `docs/POSTMAN_GUIDE.md` | Como usar o Postman |

### Scripts

| Arquivo | Descrição |
|---------|-----------|
| `run_tests.py` | Executar testes de certificação |
| `scripts/gerar_token.py` | Gerar tokens de teste |
| `scripts/convert_excel_to_json.py` | Converter planilha |

### Testes

| Arquivo | Descrição |
|---------|-----------|
| `tests/test_swagger_flow.py` | Simula fluxo do Swagger |
| `tests/test_payment_and_webhook.py` | Teste completo |
| `tests/test_webhook_simple.py` | Teste simples |

---

## 🚀 Comandos Principais

### Desenvolvimento
```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn src.main:app --reload

# Acessar Swagger
http://localhost:8000/docs
```

### Testes
```bash
# Gerar tokens
python scripts/gerar_token.py

# Executar testes de certificação
python run_tests.py

# Testes individuais
python tests/test_swagger_flow.py
python tests/test_payment_and_webhook.py
```

### Documentação
```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

---

## 📊 Fluxo de Trabalho

### 1. Setup Inicial
```bash
git clone <repo>
cd spdpay_gateway
pip install -r requirements.txt
cp .env.example .env
# Configurar .env com credenciais
```

### 2. Desenvolvimento
```bash
uvicorn src.main:app --reload
# Abrir http://localhost:8000/docs
# Testar endpoints no Swagger
```

### 3. Testes
```bash
python scripts/gerar_token.py
python run_tests.py
```

### 4. Deploy
```bash
# Configurar variáveis de ambiente
# Deploy no servidor
# Configurar webhook na Adiq
```

---

## 🔐 Arquivos Sensíveis

**NÃO COMMITAR:**
- `.env` - Credenciais e secrets
- `*.log` - Logs podem conter dados sensíveis
- `docs/resultados_testes.json` - Pode conter dados reais

**Já está no `.gitignore`** ✅

---

## 📚 Mais Informações

- **Setup:** `README.md`
- **Início Rápido:** `QUICK_START.md`
- **API:** `docs/API_DOCUMENTATION.md`
- **Certificação:** `docs/CERTIFICATION.md`
- **Segurança:** `docs/SECURITY.md`

---

**Estrutura organizada e pronta para produção!** 🚀
