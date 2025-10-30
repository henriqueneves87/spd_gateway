---
trigger: manual
---

✅ Convenções de Código · Spdpay Gateway

Versão: 1.0.0
Status: Obrigatório 🚨
Data: 2025-10-29

Este documento define os padrões técnicos e de arquitetura do Spdpay Gateway.
Toda nova funcionalidade deverá respeitar estas regras.

🧠 Filosofia

Simplicidade antes de complexidade

Cada peça com uma responsabilidade clara

Falhar com clareza é melhor do que mascarar o erro

Nenhum dado sensível de cartão no nosso banco — nunca

🏗 Estrutura de Pastas (Atualizada para o Spdpay)
spdpay-gateway/
├─ src/
│  ├─ api/            # Endpoints FastAPI
│  ├─ services/       # Lógica de negócio (core payments)
│  ├─ adapters/       # Clientes externos (Adiq)
│  ├─ models/         # Entidades e schemas
│  ├─ core/           # Config, auth, utils globais
│  ├─ db/             # Supabase storage layer
│  └─ main.py
├─ tests/
├─ docs/
└─ ops/               # Infra (Docker, Render configs)


📌 API “magra”, Services “gordos”
Endpoints só validam entrada e chamam serviço.

🔐 PCI e Segurança

Regra Suprema:
✔ Nunca armazenar: PAN, CVV, data de validade, nome impresso no cartão
✔ Apenas token/vaultId da Adiq podem ir para o banco ✅

Outras diretrizes:

Item	Status
TLS obrigatório	✅ Render cuida
Adiq tokens sempre em memória curta	✅
Nunca logar payload de cartão	✅
Chaves mascaradas em logs	✅
API Keys por Merchant	✅ obrigatório
🧩 Tamanho e Organização do Código
Item	Limite	Observação
Endpoint	≤ 80 linhas	Apenas validação
Service	≤ 300 linhas	Coração do domínio
Adapter Adiq	≤ 200 linhas	Conexão externa
Schemas	≤ 100 linhas	Simples
Arquivo no geral	≤ 400 linhas	Fragmentar quando necessário
🙅‍♂️ Regras de Erros (CRÍTICAS PARA CARTÃO)

❌ Proibido:

except:
    pass


❌ Proibido:

return None  # no pagamento?!


✅ Obrigatório:

logger.error("adiq_auth_failed", error=str(e))
raise HTTPException(502, "Falha na comunicação com Adiq")


✅ Logs devem ter ID da invoice/transaction

📡 Webhooks

Regra:

Sempre idempotentes

Registar evento antes de processar

Atualização do status somente se status atual permite

Proibido reprocessar sucesso → Sucesso.

🧱 Domínio de Pagamentos — Estados Permitidos
Invoice Status
PENDING → PROCESSING → PAID
         PROCESSING → FAILED

Transaction Status
CREATED → AUTHORIZED → CAPTURED → SETTLED
CREATED → DECLINED
AUTHORIZED → CANCELLED


Nunca permitir:
❌ PAID → PENDING
❌ Pular etapas de transação

📚 Idioma e Docstrings

✅ Docstring em inglês
✅ Comentários de regra de negócio podem ser PT-BR

✅ Testes
Tipo	Obrigatório
Services de pagamento	✅
Adapter Adiq	✅
Webhooks	✅
Validação de schemas	✅
Endpoints	✅
Banco/Supabase	Parcial ⚠️

Cobertura mínima: >70%
(Não é jurídico, é cartão; cobertura realista)

🚀 Performance

Todas as chamadas para Adiq: async

Webhook rápido → colocar longo em task (futuro)

Rate-limiting por merchant

✅ Code Review Checklist (Gateway)
Item	Check
Nenhum dado de cartão no banco	✅
Logs estruturados	✅
Exceções específicas	✅
Testes cobrindo caminhos críticos	✅
Rotas organizadas por domínio	✅
Transições de status válidas	✅
🔥 Conclusão

Este material está:
✅ 100% alinhado ao contexto de pagamentos
✅ Sintético mas completo
✅ Excelente para o Cursor usar como regra do projeto
✅ Preparado para a construção do gateway