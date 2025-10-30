# 🔐 Política de Segurança - Spdpay Gateway

**Versão:** 1.0.0  
**Data:** 2025-10-29  
**Status:** Crítico 🚨

---

## 📋 Visão Geral

O Spdpay Gateway processa transações com cartão de crédito e débito, portanto está sujeito aos padrões **PCI DSS** (Payment Card Industry Data Security Standard).

Este documento define as políticas de segurança obrigatórias para o projeto.

---

## 🛡️ Conformidade PCI DSS

### Nível de Conformidade

- **Nível:** SAQ A-EP (E-commerce com redirecionamento)
- **Escopo:** Gateway não armazena dados de cartão
- **Responsável:** Adiq (processador certificado PCI)

### Dados Proibidos de Armazenar

| Dado | Status | Observação |
|------|--------|------------|
| PAN (número completo do cartão) | ❌ NUNCA | Apenas token Adiq |
| CVV/CVC | ❌ NUNCA | Nem em logs |
| Data de validade | ❌ NUNCA | Apenas em memória |
| Nome impresso no cartão | ❌ NUNCA | Apenas em memória |
| Track data (banda magnética) | ❌ NUNCA | N/A para e-commerce |

### Dados Permitidos

| Dado | Status | Observação |
|------|--------|------------|
| Token Adiq | ✅ Permitido | Identificador seguro |
| VaultId Adiq | ✅ Permitido | Referência ao cofre |
| Brand (bandeira) | ✅ Permitido | Ex: visa, mastercard |
| Last4 (últimos 4 dígitos) | ✅ Permitido | Para exibição |
| Expiration month/year | ⚠️ Cuidado | Apenas se necessário |

---

## 🔑 Autenticação e Autorização

### API Keys

- **Formato:** UUID v4
- **Armazenamento:** Hash SHA-256 no banco
- **Rotação:** A cada 90 dias (recomendado)
- **Escopo:** Por merchant

```python
# Exemplo de validação
async def validate_api_key(api_key: str) -> Merchant:
    """
    Validate API key and return associated merchant.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Merchant instance if valid
        
    Raises:
        UnauthorizedError: If API key is invalid
    """
    hashed_key = hash_api_key(api_key)
    merchant = await db.get_merchant_by_api_key(hashed_key)
    
    if not merchant or not merchant.is_active:
        raise UnauthorizedError("Invalid API key")
    
    return merchant
```

### Rate Limiting

- **Por merchant:** 100 requests/minuto
- **Global:** 1000 requests/minuto
- **Webhook:** 50 requests/minuto por merchant

---

## 🔒 Criptografia

### Em Trânsito

- **TLS 1.2+** obrigatório
- **Certificados:** Gerenciados pelo Render
- **HSTS:** Habilitado

### Em Repouso

- **Banco de dados:** Criptografia nativa do Supabase
- **Secrets:** Variáveis de ambiente (nunca no código)
- **Logs:** Sanitizados (sem dados sensíveis)

---

## 📝 Logging e Auditoria

### Regras de Logging

#### ✅ Pode Logar

```python
logger.info(
    "payment_created",
    invoice_id=invoice.id,
    transaction_id=transaction.id,
    amount=amount,
    currency="BRL",
    merchant_id=merchant.id,
    brand=card_brand,
    last4=card_last4
)
```

#### ❌ NUNCA Logar

```python
# ❌ PROIBIDO
logger.info(f"Card: {card_number}")
logger.info(f"CVV: {cvv}")
logger.debug(f"Request: {request.json()}")  # Pode conter dados sensíveis
```

### Sanitização Automática

```python
# core/logger.py
SENSITIVE_FIELDS = [
    "cardNumber", "card_number", "pan",
    "cvv", "cvc", "securityCode",
    "expirationMonth", "expirationYear",
    "cardholderName"
]

def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive fields from log data"""
    sanitized = data.copy()
    
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"
    
    return sanitized
```

### Auditoria Obrigatória

Registrar em tabela `audit_logs`:

- Criação de invoice
- Tentativa de pagamento
- Mudança de status
- Acesso a dados sensíveis
- Falhas de autenticação
- Webhooks recebidos

---

## 🌐 Segurança de Rede

### Firewall

- **Inbound:** Apenas HTTPS (443)
- **Outbound:** Apenas Adiq e Supabase
- **IPs permitidos:** Whitelist Adiq (webhooks)

### Headers de Segurança

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.spdpay.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## 🔐 Validação de Webhooks

### Assinatura HMAC

```python
import hmac
import hashlib

def validate_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Validate webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw webhook payload
        signature: Signature from webhook header
        secret: Webhook secret key
        
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)
```

### Proteção contra Replay

```python
# Verificar timestamp do webhook
MAX_WEBHOOK_AGE = 300  # 5 minutos

def is_webhook_fresh(timestamp: int) -> bool:
    """Check if webhook is not too old"""
    current_time = int(time.time())
    return (current_time - timestamp) <= MAX_WEBHOOK_AGE
```

---

## 🚨 Resposta a Incidentes

### Classificação de Incidentes

| Severidade | Descrição | Tempo de Resposta |
|------------|-----------|-------------------|
| **Crítico** | Vazamento de dados de cartão | Imediato |
| **Alto** | Falha de autenticação em massa | 1 hora |
| **Médio** | Erro no processamento de pagamentos | 4 horas |
| **Baixo** | Bug sem impacto de segurança | 24 horas |

### Procedimento de Incidente Crítico

1. **Isolar:** Pausar sistema imediatamente
2. **Notificar:** Equipe de segurança + Adiq
3. **Investigar:** Logs, banco de dados, tráfego
4. **Remediar:** Corrigir vulnerabilidade
5. **Documentar:** Post-mortem completo
6. **Comunicar:** Stakeholders e usuários afetados

### Contatos de Emergência

```
Segurança: security@spdpay.com
Adiq Suporte: suporte@adiq.io
Supabase: support@supabase.com
```

---

## 🔍 Testes de Segurança

### Obrigatórios

- [ ] **Penetration Testing:** Anual
- [ ] **Vulnerability Scanning:** Mensal
- [ ] **Dependency Audit:** Semanal (`pip-audit`)
- [ ] **SAST:** A cada commit (Ruff, Bandit)
- [ ] **Secrets Scanning:** A cada commit (GitGuardian)

### Ferramentas

```bash
# Audit de dependências
pip-audit

# Análise estática de segurança
bandit -r src/

# Verificar secrets
trufflehog filesystem . --only-verified
```

---

## 📊 Monitoramento

### Alertas Críticos

- Taxa de erro > 5%
- Latência > 2s (p95)
- Falhas de autenticação > 10/min
- Webhooks falhando > 20%
- Tentativas de acesso não autorizado

### Métricas de Segurança

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

auth_failures = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['merchant_id']
)

payment_processing_time = Histogram(
    'payment_processing_seconds',
    'Payment processing time'
)
```

---

## 🔐 Gerenciamento de Secrets

### Variáveis de Ambiente

```bash
# .env (NUNCA commitar)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
ADIQ_CLIENT_ID=a40a208c-...
ADIQ_CLIENT_SECRET=C0A9E2AF-...
WEBHOOK_SECRET=super-secret-key
JWT_SECRET=another-secret-key
```

### Rotação de Secrets

| Secret | Frequência | Responsável |
|--------|------------|-------------|
| API Keys | 90 dias | DevOps |
| Webhook Secret | 180 dias | DevOps |
| JWT Secret | 365 dias | DevOps |
| Supabase Key | Anual | DevOps |
| Adiq Credentials | Conforme Adiq | Adiq |

---

## 📜 Compliance

### LGPD (Lei Geral de Proteção de Dados)

- **Dados coletados:** Nome, CPF, e-mail, endereço
- **Base legal:** Execução de contrato
- **Retenção:** 5 anos (obrigação fiscal)
- **Direitos:** Acesso, correção, exclusão

### Relatórios Obrigatórios

- **PCI DSS:** Anual (SAQ A-EP)
- **Auditoria interna:** Trimestral
- **Relatório de incidentes:** Quando aplicável

---

## 🚀 Checklist de Deploy

Antes de cada deploy em produção:

- [ ] Secrets atualizados
- [ ] TLS configurado
- [ ] Rate limiting ativo
- [ ] Logs sanitizados
- [ ] Webhooks validados
- [ ] Monitoramento ativo
- [ ] Backup configurado
- [ ] Rollback testado

---

## 📞 Reporte de Vulnerabilidades

### Como Reportar

Se você descobrir uma vulnerabilidade de segurança:

1. **NÃO** abra uma issue pública
2. Envie e-mail para: **security@spdpay.com**
3. Inclua:
   - Descrição da vulnerabilidade
   - Passos para reproduzir
   - Impacto potencial
   - Sugestão de correção (se houver)

### Tempo de Resposta

- **Confirmação:** 24 horas
- **Avaliação:** 72 horas
- **Correção (crítico):** 7 dias
- **Correção (não crítico):** 30 dias

### Recompensas

Vulnerabilidades críticas podem ser elegíveis para recompensas (bug bounty).

---

## 🔥 Conclusão

A segurança é **responsabilidade de todos**.

**Lembre-se:**
- ❌ Nunca armazene dados de cartão
- ✅ Sempre valide entrada
- ✅ Sempre sanitize logs
- ✅ Sempre use HTTPS
- ✅ Sempre valide webhooks

**Em caso de dúvida, pergunte. Em caso de incidente, reporte imediatamente.**
