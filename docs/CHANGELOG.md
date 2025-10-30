# 📝 Changelog - Documentação

Todas as mudanças notáveis na documentação serão registradas aqui.

---

## [1.1.0] - 2025-10-29

### ✨ Adicionado

- **Prevenção de Duplicação de Código**
  - Nova seção em CONVENTIONS.md
  - Checklist obrigatório antes de criar código
  - Tabela de arquivos únicos
  - Padrão de nomenclatura
  - Exemplos práticos

- **GitHub Configuration**
  - `.github/workflows/ci.yml` - Pipeline CI/CD completo
  - `.github/ISSUE_TEMPLATE/bug_report.md` - Template de bugs
  - `.github/ISSUE_TEMPLATE/feature_request.md` - Template de features
  - `.github/PULL_REQUEST_TEMPLATE.md` - Template de PRs
  - `.github/FUNDING.yml` - Configuração de funding
  - `.github/README.md` - Guia da configuração GitHub

### 📝 Modificado

- **ROADMAP.md**
  - Fase 1 alterada de ✅ para 🚧 (em construção)
  - Checkboxes da Fase 1 desmarcados (pendente implementação)
  - Postman Collection na Fase 2
  - Playground interativo na Fase 2

- **CONVENTIONS.md**
  - Seção de prevenção de duplicação adicionada
  - Checklist de PR atualizado
  - Exemplos de boas práticas

### 🗂️ Reorganizado

- **Arquivos movidos para raiz:**
  - `docs/CONVENTIONS.md` → `CONVENTIONS.md`
  - `docs/SECURITY.md` → `SECURITY.md`
  - `docs/CONTRIBUTING.md` → `CONTRIBUTING.md`

- **Arquivos excluídos:**
  - `readme.md` (minúsculo - duplicado)
  - `gptconversation.md` (vazio)
  - `prompt.md` (rascunho antigo)
  - `DOCUMENTATION_SUMMARY.md` (duplicado)

---

## [1.0.1] - 2025-10-29

### ✨ Adicionado

- **GitHub Repository Links**
  - Badge no README.md principal
  - Links úteis no docs/README.md
  - Seção completa de contato no CONTRIBUTING.md
  - Repository: https://github.com/henriqueneves87/spd_gateway

### 📝 Modificado

- **ROADMAP.md**
  - Postman Collection adicionada à Fase 2 (Dev Experience)
  - Playground interativo adicionado à Fase 2

- **README.md**
  - Badges profissionais (GitHub, Python, FastAPI, License)
  - Link direto para repositório

- **docs/README.md**
  - Seção de links úteis no topo

- **CONTRIBUTING.md**
  - Seção de contato expandida com links do GitHub

---

## [1.0.0] - 2025-10-29

### ✨ Adicionado

#### Documentação Completa

- **CONVENTIONS.md** - Convenções de código e arquitetura
  - Estrutura de pastas detalhada
  - Princípios de arquitetura (API magra, Services gordos)
  - Regras PCI DSS obrigatórias
  - Padrões de código (tamanho, organização)
  - Tratamento de erros
  - Regras de webhooks
  - Estados permitidos (Invoice e Transaction)
  - Idioma e docstrings
  - Cobertura de testes
  - Performance
  - Code review checklist

- **SECURITY.md** - Política de segurança completa
  - Conformidade PCI DSS (SAQ A-EP)
  - Dados proibidos vs permitidos
  - Autenticação e autorização (API Keys)
  - Rate limiting
  - Criptografia (em trânsito e repouso)
  - Logging seguro e sanitização
  - Auditoria obrigatória
  - Segurança de rede
  - Validação de webhooks (HMAC)
  - Resposta a incidentes
  - Testes de segurança
  - Monitoramento
  - Gerenciamento de secrets
  - Compliance (LGPD)
  - Reporte de vulnerabilidades

- **CONTRIBUTING.md** - Guia de contribuição
  - Código de conduta
  - Setup do ambiente (local e Docker)
  - Padrões de commits (Conventional Commits)
  - Estratégia de branches
  - Python style guide
  - Type hints obrigatórios
  - Docstrings (formato Google)
  - Organização de imports
  - Estrutura de testes
  - Processo de Pull Request
  - Templates de issues
  - CI/CD

- **CERTIFICATION.md** - Roteiro de certificação Adiq
  - Credenciais de homologação
  - Cartões de teste (todas as bandeiras)
  - Roteiro completo de testes:
    - OAuth2 autenticação
    - Tokenização
    - Vault (cofre)
    - Pagamento à vista
    - Pagamento parcelado
    - Antifraude (accept/reject/review)
    - 3DS (13 casos de teste)
    - Consulta de pagamento
    - Webhooks
  - Planilha de resultados
  - Checklist de certificação
  - Scripts de automação
  - Contatos de suporte

- **ADIQ_MAPPING.md** - Mapeamento Adiq ↔ Spdpay
  - Autenticação (OAuth2)
  - Tokenização
  - Vault (cofre)
  - Pagamento (request/response completo)
  - Webhook (eventos e payloads)
  - Estados e transições
  - Models internos (Card, Transaction, WebhookLog)
  - Dados de teste
  - Regras de segurança
  - Campos obrigatórios vs opcionais

- **README.md** (docs/) - Índice da documentação
  - Guia de leitura para diferentes perfis
  - Busca rápida
  - Diagramas (fluxo e arquitetura)
  - Checklist rápido

- **CHANGELOG.md** - Este arquivo

### 🔧 Estrutura

```
docs/
├── README.md                                      # Índice
├── CONVENTIONS.md                                 # Convenções
├── SECURITY.md                                    # Segurança
├── CONTRIBUTING.md                                # Contribuição
├── CERTIFICATION.md                               # Certificação Adiq
├── ADIQ_MAPPING.md                                # Mapeamento
├── CHANGELOG.md                                   # Este arquivo
├── Adiq.Gateways.Ecommerce.postman_collection.json  # Collection Postman
└── gateway-ecommerce-roteito-testes 3.xlsx       # Planilha de testes
```

### 📊 Estatísticas

- **Total de documentos:** 8
- **Linhas de documentação:** ~3.500
- **Tópicos cobertos:** 50+
- **Exemplos de código:** 30+
- **Diagramas:** 2

### ✅ Validação

Todos os documentos foram validados contra:

- ✅ Convenções do projeto (`.windsurf/rules/spd-gateway.md`)
- ✅ Padrões PCI DSS
- ✅ Documentação oficial Adiq
- ✅ Postman Collection Adiq
- ✅ Roteiro de testes Adiq

### 🎯 Próximos Passos

- [ ] Adicionar diagramas de sequência detalhados
- [ ] Criar guia de troubleshooting
- [ ] Adicionar FAQ
- [ ] Criar templates de código
- [ ] Adicionar exemplos de integração

---

## Formato

Este changelog segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

Tipos de mudanças:
- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correções de bugs
- `Segurança` para vulnerabilidades

---

**Mantenha este arquivo atualizado a cada mudança significativa na documentação!**
