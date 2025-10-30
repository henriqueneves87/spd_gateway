# 📋 Convenções de Código - Spdpay Gateway

**Versão:** 1.0.0  
**Status:** Obrigatório 🚨  
**Data:** 2025-10-29

Este documento define os padrões técnicos e de arquitetura do Spdpay Gateway.
Toda nova funcionalidade deverá respeitar estas regras.

---

## 🧠 Filosofia

- **Simplicidade antes de complexidade**
- **Cada peça com uma responsabilidade clara**
- **Falhar com clareza é melhor do que mascarar o erro**
- **Nenhum dado sensível de cartão no nosso banco — nunca**

---

## 🏗 Estrutura de Pastas

```
spdpay-gateway/
├─ src/
│  ├─ api/            # Endpoints FastAPI
│  │  ├─ v1/          # Versão 1 da API
│  │  │  ├─ __init__.py
│  │  │  ├─ invoices.py
│  │  │  ├─ payments.py
│  │  │  ├─ cards.py
│  │  │  └─ webhooks.py
│  │  ├─ dependencies.py  # Auth e validações
│  │  └─ health.py
│  ├─ services/       # Lógica de negócio (core payments)
│  │  ├─ invoice_service.py
│  │  ├─ payment_service.py
│  │  └─ webhook_service.py
│  ├─ schemas/        # Pydantic models (request/response)
│  │  ├─ invoice.py
│  │  ├─ payment.py
│  │  ├─ card.py
│  │  └─ webhook.py
│  ├─ adapters/       # Clientes externos (Adiq)
│  │  └─ adiq.py
│  ├─ models/         # Domain models (DB entities)
│  │  ├─ invoice.py
│  │  ├─ transaction.py
│  │  ├─ customer.py
│  │  ├─ merchant.py
│  │  └─ card.py
│  ├─ core/           # Config, auth, utils globais
│  │  ├─ config.py
│  │  ├─ logger.py
│  │  ├─ security.py
│  │  ├─ state_machine.py
│  │  └─ exceptions.py
│  ├─ db/             # Supabase storage layer
│  │  ├─ schemas.py
│  │  └─ client.py
│  └─ main.py
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ certification/
│  └─ fixtures/
├─ docs/
└─ ops/               # Infra (Docker, Render configs)
```

---

## 📌 Princípios de Arquitetura

### API "magra", Services "gordos"

**Endpoints só validam entrada e chamam serviço.**

```python
# ✅ Correto
@router.post("/invoices")
async def create_invoice(data: InvoiceCreateRequest):
    return await invoice_service.create(data)

# ❌ Errado - lógica no endpoint
@router.post("/invoices")
async def create_invoice(data: InvoiceCreateRequest):
    # validações complexas aqui
    # chamadas ao banco aqui
    # lógica de negócio aqui
```

### Separação de Responsabilidades

- **API Layer**: Validação de entrada, autenticação, serialização
- **Service Layer**: Lógica de negócio, orquestração, transações
- **Adapter Layer**: Comunicação com serviços externos (Adiq)
- **Model Layer**: Representação de dados, persistência

---

## 🔐 PCI e Segurança

### Regra Suprema

**✅ Nunca armazenar:**
- PAN (número do cartão)
- CVV
- Data de validade
- Nome impresso no cartão

**✅ Apenas permitido:**
- Token/vaultId da Adiq
- Brand (bandeira)
- Last4 (últimos 4 dígitos)

### Diretrizes de Segurança

| Item | Status | Observação |
|------|--------|------------|
| TLS obrigatório | ✅ | Render cuida |
| Adiq tokens sempre em memória curta | ✅ | Nunca persistir |
| Nunca logar payload de cartão | ✅ | Sanitizar logs |
| Chaves mascaradas em logs | ✅ | `****1234` |
| API Keys por Merchant | ✅ | Obrigatório |

### Exemplo de Log Seguro

```python
# ❌ NUNCA fazer isso
logger.info(f"Card: {card_number}")

# ✅ Correto
logger.info(f"Card tokenized: {token_id}, last4: {last4}")
```

---

## 🧩 Tamanho e Organização do Código

| Item | Limite | Observação |
|------|--------|------------|
| Endpoint | ≤ 80 linhas | Apenas validação |
| Service | ≤ 300 linhas | Coração do domínio |
| Adapter Adiq | ≤ 200 linhas | Conexão externa |
| Schemas | ≤ 100 linhas | Simples |
| Arquivo no geral | ≤ 400 linhas | Fragmentar quando necessário |

---

## 🙅‍♂️ Regras de Erros (CRÍTICAS PARA CARTÃO)

### ❌ Proibido

```python
# NUNCA fazer isso
try:
    payment = process_payment()
except:
    pass  # ❌ Silenciar erro de pagamento

# NUNCA fazer isso
def process_payment():
    try:
        # ...
        return None  # ❌ Retornar None em pagamento
    except:
        return None
```

### ✅ Obrigatório

```python
# ✅ Correto - logar e propagar
try:
    token = await adiq_client.authenticate()
except Exception as e:
    logger.error(
        "adiq_auth_failed",
        error=str(e),
        merchant_id=merchant_id
    )
    raise HTTPException(
        status_code=502,
        detail="Falha na comunicação com Adiq"
    )

# ✅ Logs devem ter ID da invoice/transaction
logger.info(
    "payment_processed",
    invoice_id=invoice.id,
    transaction_id=transaction.id,
    amount=amount
)
```

---

## 📡 Webhooks

### Regras Obrigatórias

1. **Sempre idempotentes**: Processar o mesmo webhook múltiplas vezes não deve causar efeitos colaterais
2. **Registrar evento antes de processar**: Salvar webhook_log primeiro
3. **Atualização de status somente se permitido**: Validar transição de estado
4. **Proibido reprocessar sucesso → sucesso**

```python
# ✅ Correto
async def process_webhook(webhook_data: dict):
    # 1. Registrar recebimento
    webhook_log = await save_webhook_log(webhook_data)
    
    # 2. Verificar se já foi processado (idempotência)
    if webhook_log.processed:
        return {"status": "already_processed"}
    
    # 3. Validar transição de estado
    if not can_transition(current_status, new_status):
        raise InvalidStateTransition()
    
    # 4. Processar
    await update_transaction_status(new_status)
    
    # 5. Marcar como processado
    await mark_webhook_processed(webhook_log.id)
```

---

## 🧱 Domínio de Pagamentos — Estados Permitidos

### Invoice Status

```
PENDING → PROCESSING → PAID
         PROCESSING → FAILED
```

### Transaction Status

```
CREATED → AUTHORIZED → CAPTURED → SETTLED
CREATED → DECLINED
AUTHORIZED → CANCELLED
```

### ❌ Nunca Permitir

- `PAID → PENDING` (reverter status)
- Pular etapas de transação
- Transições não mapeadas

### Implementação

```python
# core/state_machine.py
ALLOWED_TRANSITIONS = {
    "Invoice": {
        "PENDING": ["PROCESSING"],
        "PROCESSING": ["PAID", "FAILED"],
        "PAID": [],  # Estado final
        "FAILED": []  # Estado final
    },
    "Transaction": {
        "CREATED": ["AUTHORIZED", "DECLINED"],
        "AUTHORIZED": ["CAPTURED", "CANCELLED"],
        "CAPTURED": ["SETTLED"],
        "SETTLED": [],  # Estado final
        "DECLINED": [],  # Estado final
        "CANCELLED": []  # Estado final
    }
}

def can_transition(entity_type: str, from_status: str, to_status: str) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(entity_type, {}).get(from_status, [])
    return to_status in allowed
```

---

## 📚 Idioma e Docstrings

### Padrões

- ✅ **Docstrings em inglês**
- ✅ **Comentários de regra de negócio podem ser PT-BR**
- ✅ **Nomes de variáveis em inglês**
- ✅ **Logs em inglês**

```python
# ✅ Correto
async def create_invoice(data: InvoiceCreateRequest) -> Invoice:
    """
    Create a new invoice for a merchant.
    
    Args:
        data: Invoice creation request data
        
    Returns:
        Created invoice instance
        
    Raises:
        InvalidMerchantError: If merchant is not active
    """
    # Regra de negócio: faturas só podem ser criadas para merchants ativos
    if not merchant.is_active:
        raise InvalidMerchantError()
```

---

## ✅ Testes

### Cobertura Obrigatória

| Tipo | Obrigatório | Cobertura Mínima |
|------|-------------|------------------|
| Services de pagamento | ✅ | 80% |
| Adapter Adiq | ✅ | 70% |
| Webhooks | ✅ | 80% |
| Validação de schemas | ✅ | 90% |
| Endpoints | ✅ | 70% |
| Banco/Supabase | Parcial ⚠️ | 50% |

**Cobertura mínima geral: >70%**

### Estrutura de Testes

```python
# tests/unit/test_payment_service.py
import pytest
from src.services.payment_service import PaymentService

@pytest.mark.asyncio
async def test_create_payment_success():
    """Test successful payment creation"""
    # Arrange
    service = PaymentService()
    data = create_test_payment_data()
    
    # Act
    result = await service.create_payment(data)
    
    # Assert
    assert result.status == "CREATED"
    assert result.amount == data.amount
```

---

## 🚀 Performance

### Regras

1. **Todas as chamadas para Adiq: async**
2. **Webhook rápido → colocar longo em task (futuro)**
3. **Rate-limiting por merchant**
4. **Connection pooling para Supabase**

```python
# ✅ Correto - async
async def tokenize_card(card_data: dict) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=card_data)
        return response.json()["token"]

# ❌ Errado - sync
def tokenize_card(card_data: dict) -> str:
    response = requests.post(url, json=card_data)
    return response.json()["token"]
```

---

## ✅ Code Review Checklist

Antes de fazer merge, verificar:

- [ ] Nenhum dado de cartão no banco
- [ ] Logs estruturados e sanitizados
- [ ] Exceções específicas (não genéricas)
- [ ] Testes cobrindo caminhos críticos
- [ ] Rotas organizadas por domínio
- [ ] Transições de status válidas
- [ ] Docstrings em inglês
- [ ] Type hints em todas as funções
- [ ] Async onde necessário
- [ ] Sem hardcoded secrets

---

## 🔧 Ferramentas Obrigatórias

### Formatação e Linting

```bash
# Black - formatação
black src/ tests/

# Ruff - linting
ruff check src/ tests/

# isort - ordenação de imports
isort src/ tests/

# mypy - type checking (parcial)
mypy src/ --ignore-missing-imports
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
```

---

## 🚫 Prevenção de Duplicação de Código

### Regra Crítica: Verificar Antes de Criar

**Antes de criar qualquer arquivo, função ou classe, SEMPRE:**

1. **Buscar primeiro** - Use grep/search para verificar se já existe
2. **Consultar estrutura** - Verifique este documento e a árvore de pastas
3. **Reutilizar** - Prefira estender código existente a duplicar

### Checklist Obrigatório

```bash
# 1. Buscar se já existe
grep -r "class PaymentService" src/
grep -r "def process_payment" src/

# 2. Verificar estrutura de pastas
ls -la src/services/

# 3. Se existir, reutilizar ou estender
# Se não existir, criar no lugar correto conforme estrutura
```

### Arquivos Únicos (Nunca Duplicar)

| Arquivo | Localização | Propósito |
|---------|-------------|-----------|
| `README.md` | Raiz | Apresentação do projeto |
| `ROADMAP.md` | Raiz | Planejamento de fases |
| `CONVENTIONS.md` | Raiz | Este documento |
| `SECURITY.md` | Raiz | Política de segurança |
| `CONTRIBUTING.md` | Raiz | Guia de contribuição |
| `docs/README.md` | docs/ | Índice da documentação |
| `main.py` | src/ | Entry point da aplicação |
| `config.py` | src/core/ | Configurações centralizadas |

### Padrão de Nomenclatura

```python
# ✅ Correto - Nome único e descritivo
class AdiqPaymentAdapter:
    pass

# ❌ Errado - Nome genérico que pode duplicar
class Adapter:
    pass

# ✅ Correto - Função específica
def validate_credit_card_payment(data: dict) -> bool:
    pass

# ❌ Errado - Função genérica
def validate(data: dict) -> bool:
    pass
```

### Antes de Fazer PR

- [ ] Busquei por código similar
- [ ] Verifiquei a estrutura de pastas
- [ ] Não criei arquivos duplicados
- [ ] Segui a nomenclatura padrão
- [ ] Consultei CONVENTIONS.md

---

## 🔥 Conclusão

Este documento está:
- ✅ 100% alinhado ao contexto de pagamentos
- ✅ Sintético mas completo
- ✅ Excelente para referência durante desenvolvimento
- ✅ Preparado para a construção do gateway
- ✅ Com regras de prevenção de duplicação

**Sempre consulte este documento antes de implementar novas features.**
