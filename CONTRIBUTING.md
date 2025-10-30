# 🤝 Guia de Contribuição - Spdpay Gateway

Obrigado por contribuir com o Spdpay Gateway! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Testes](#testes)
- [Documentação](#documentação)

---

## 📜 Código de Conduta

- Seja respeitoso e profissional
- Aceite feedback construtivo
- Foque no que é melhor para o projeto
- Mantenha a segurança como prioridade

---

## 🚀 Como Contribuir

### Tipos de Contribuição

1. **Bug Reports**: Reporte bugs via issues
2. **Feature Requests**: Sugira novas funcionalidades
3. **Code Contributions**: Envie pull requests
4. **Documentation**: Melhore a documentação
5. **Tests**: Adicione ou melhore testes

### Antes de Começar

1. Verifique se já existe uma issue relacionada
2. Para mudanças grandes, abra uma issue primeiro para discussão
3. Leia as [Convenções](./CONVENTIONS.md) e [Segurança](./SECURITY.md)

---

## 🛠️ Configuração do Ambiente

### Pré-requisitos

- Python 3.11+
- Git
- Docker (opcional, para desenvolvimento local)

### Setup Local

```bash
# 1. Clone o repositório
git clone https://github.com/spdpay/spdpay-gateway.git
cd spdpay-gateway

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 5. Rode os testes
pytest

# 6. Inicie o servidor
uvicorn src.main:app --reload
```

### Docker (Alternativa)

```bash
# Build
docker-compose build

# Run
docker-compose up

# Testes
docker-compose run --rm api pytest
```

---

## 📝 Padrões de Código

### Estrutura de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

#### Exemplos

```bash
feat(payments): add 3DS support

Implement 3DS authentication flow for credit card payments.
Includes deviceInfo collection and challenge handling.

Closes #123

---

fix(webhooks): prevent duplicate processing

Add idempotency check to webhook handler to prevent
duplicate transaction updates.

Fixes #456

---

docs(api): update payment endpoint examples

Add examples for all payment types including installments.
```

### Branches

- `main`: Produção (protegida)
- `develop`: Desenvolvimento (protegida)
- `feature/nome-da-feature`: Novas funcionalidades
- `fix/nome-do-bug`: Correções
- `docs/nome-da-doc`: Documentação

```bash
# Criar branch
git checkout -b feature/add-pix-support

# Commitar
git add .
git commit -m "feat(payments): add PIX payment method"

# Push
git push origin feature/add-pix-support
```

---

## 🔍 Padrões de Código

### Python Style Guide

Seguimos [PEP 8](https://pep8.org/) com algumas customizações:

```python
# ✅ Bom
async def create_payment(
    invoice_id: str,
    amount: int,
    merchant: Merchant
) -> Payment:
    """
    Create a new payment for an invoice.
    
    Args:
        invoice_id: Invoice UUID
        amount: Amount in cents
        merchant: Merchant instance
        
    Returns:
        Created payment instance
        
    Raises:
        InvalidAmountError: If amount is invalid
        InvoiceNotFoundError: If invoice doesn't exist
    """
    if amount <= 0:
        raise InvalidAmountError("Amount must be positive")
    
    invoice = await get_invoice(invoice_id)
    if not invoice:
        raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
    
    payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        merchant_id=merchant.id,
        status="CREATED"
    )
    
    await db.save(payment)
    logger.info("payment_created", payment_id=payment.id)
    
    return payment


# ❌ Ruim
def create_payment(invoice_id,amount,merchant):
    if amount<=0:raise Exception("bad amount")
    invoice=get_invoice(invoice_id)
    if invoice==None:return None
    payment=Payment(invoice_id=invoice_id,amount=amount,merchant_id=merchant.id,status="CREATED")
    db.save(payment)
    return payment
```

### Type Hints

**Obrigatório** em todas as funções:

```python
# ✅ Correto
async def process_payment(
    payment_id: str,
    card_token: str
) -> dict[str, Any]:
    pass

# ❌ Errado
async def process_payment(payment_id, card_token):
    pass
```

### Docstrings

Use formato Google:

```python
def calculate_installment_amount(
    total: int,
    installments: int
) -> int:
    """
    Calculate amount per installment.
    
    Args:
        total: Total amount in cents
        installments: Number of installments
        
    Returns:
        Amount per installment in cents
        
    Raises:
        ValueError: If installments is less than 1
        
    Example:
        >>> calculate_installment_amount(10000, 3)
        3333
    """
    if installments < 1:
        raise ValueError("Installments must be >= 1")
    
    return total // installments
```

### Imports

Use `isort` para organizar:

```python
# Standard library
import os
import sys
from typing import Any, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Local
from src.core.config import settings
from src.models.payment import Payment
from src.services.payment_service import PaymentService
```

---

## 🧪 Testes

### Estrutura

```
tests/
├─ unit/              # Testes unitários
│  ├─ test_services.py
│  ├─ test_adapters.py
│  └─ test_models.py
├─ integration/       # Testes de integração
│  ├─ test_api.py
│  └─ test_database.py
├─ certification/     # Testes de certificação
│  ├─ test_adiq_flow.py
│  └─ test_3ds.py
└─ fixtures/          # Dados de teste
   └─ sample_data.py
```

### Escrevendo Testes

```python
import pytest
from src.services.payment_service import PaymentService
from tests.fixtures.sample_data import create_test_payment

@pytest.mark.asyncio
async def test_create_payment_success():
    """Test successful payment creation"""
    # Arrange
    service = PaymentService()
    payment_data = create_test_payment()
    
    # Act
    result = await service.create_payment(payment_data)
    
    # Assert
    assert result.status == "CREATED"
    assert result.amount == payment_data.amount
    assert result.id is not None

@pytest.mark.asyncio
async def test_create_payment_invalid_amount():
    """Test payment creation with invalid amount"""
    # Arrange
    service = PaymentService()
    payment_data = create_test_payment(amount=-100)
    
    # Act & Assert
    with pytest.raises(InvalidAmountError):
        await service.create_payment(payment_data)
```

### Rodando Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Específico
pytest tests/unit/test_payment_service.py

# Com output detalhado
pytest -v -s

# Apenas testes marcados
pytest -m "not slow"
```

### Cobertura Mínima

- **Services:** 80%
- **Adapters:** 70%
- **API Endpoints:** 70%
- **Geral:** 70%

---

## 📚 Documentação

### Atualizando Docs

Ao adicionar novas features:

1. Atualize `README.md` se necessário
2. Adicione docstrings em todas as funções
3. Atualize `ROADMAP.md` se aplicável
4. Adicione exemplos de uso

### API Documentation

FastAPI gera docs automaticamente em `/docs`.

Para melhorar:

```python
@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=201,
    summary="Create a new payment",
    description="Create a new payment for an existing invoice",
    responses={
        201: {"description": "Payment created successfully"},
        400: {"description": "Invalid request data"},
        404: {"description": "Invoice not found"},
        502: {"description": "Payment processor error"}
    }
)
async def create_payment(
    data: PaymentCreateRequest,
    merchant: Merchant = Depends(get_current_merchant)
) -> PaymentResponse:
    """
    Create a new payment.
    
    - **invoice_id**: UUID of the invoice
    - **card_token**: Tokenized card from Adiq
    - **installments**: Number of installments (1-12)
    """
    return await payment_service.create(data, merchant)
```

---

## 🔄 Processo de Pull Request

### Checklist

Antes de abrir um PR:

- [ ] Código segue as [Convenções](./CONVENTIONS.md)
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Cobertura de testes mantida/melhorada
- [ ] Documentação atualizada
- [ ] Commits seguem padrão Conventional Commits
- [ ] Sem dados sensíveis no código
- [ ] Logs sanitizados
- [ ] Type hints adicionados

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Resultado esperado

## Checklist
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Sem breaking changes (ou documentado)
- [ ] Segurança verificada

## Issues Relacionadas
Closes #123
```

### Processo de Review

1. **Automated Checks**: CI/CD roda testes e linting
2. **Code Review**: Pelo menos 1 aprovação necessária
3. **Security Review**: Para mudanças sensíveis
4. **Merge**: Squash and merge para manter histórico limpo

### CI/CD

GitHub Actions roda automaticamente:

```yaml
# .github/workflows/ci.yml
- Linting (ruff, black, isort)
- Type checking (mypy)
- Tests (pytest)
- Security scan (bandit, pip-audit)
- Coverage report
```

---

## 🐛 Reportando Bugs

### Template de Issue

```markdown
## Descrição do Bug
Descrição clara do problema.

## Como Reproduzir
1. Passo 1
2. Passo 2
3. Erro aparece

## Comportamento Esperado
O que deveria acontecer.

## Comportamento Atual
O que está acontecendo.

## Screenshots
Se aplicável.

## Ambiente
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11.5]
- Versão: [e.g. 1.2.3]

## Logs
```
Cole logs relevantes aqui
```

## Informações Adicionais
Qualquer contexto adicional.
```

---

## 💡 Sugerindo Features

### Template de Feature Request

```markdown
## Problema
Qual problema esta feature resolve?

## Solução Proposta
Como você imagina que funcione?

## Alternativas Consideradas
Outras soluções que você pensou?

## Impacto
- Usuários afetados:
- Complexidade estimada:
- Prioridade:

## Informações Adicionais
Mockups, exemplos, etc.
```

---

## 🎯 Prioridades

### Roadmap

Consulte [ROADMAP.md](../ROADMAP.md) para ver as prioridades do projeto.

### Labels

- `priority:critical`: Bugs críticos de segurança
- `priority:high`: Features importantes
- `priority:medium`: Melhorias
- `priority:low`: Nice to have
- `good-first-issue`: Bom para iniciantes
- `help-wanted`: Precisa de ajuda

---

## 📞 Contato

### GitHub

- **Repository**: https://github.com/henriqueneves87/spd_gateway
- **Issues**: [GitHub Issues](https://github.com/henriqueneves87/spd_gateway/issues)
- **Pull Requests**: [GitHub PRs](https://github.com/henriqueneves87/spd_gateway/pulls)
- **Discussões**: [GitHub Discussions](https://github.com/henriqueneves87/spd_gateway/discussions)

### E-mail

- **Segurança**: security@spdpay.com
- **Geral**: dev@spdpay.com

---

## 🙏 Agradecimentos

Obrigado por contribuir com o Spdpay Gateway!

Sua contribuição ajuda a construir um sistema de pagamentos mais seguro e confiável.

---

**Lembre-se: Segurança em primeiro lugar! 🔐**
