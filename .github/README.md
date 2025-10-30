# 🔧 GitHub Configuration

Esta pasta contém configurações específicas do GitHub para o projeto Spdpay Gateway.

## 📁 Estrutura

```
.github/
├── workflows/
│   └── ci.yml                    # Pipeline CI/CD
├── ISSUE_TEMPLATE/
│   ├── bug_report.md            # Template para bugs
│   └── feature_request.md       # Template para features
├── PULL_REQUEST_TEMPLATE.md     # Template para PRs
├── FUNDING.yml                  # Configuração de funding
└── README.md                    # Este arquivo
```

## 🔄 CI/CD Pipeline

### Workflow: `ci.yml`

Executa automaticamente em:
- Push para `main` ou `develop`
- Pull Requests para `main` ou `develop`

#### Jobs

1. **Lint & Format**
   - Black (formatação)
   - Ruff (linting)
   - isort (imports)
   - mypy (type checking)

2. **Security Scan**
   - Bandit (análise estática de segurança)
   - pip-audit (vulnerabilidades em dependências)

3. **Tests**
   - Pytest (Python 3.11 e 3.12)
   - Coverage report
   - Threshold mínimo: 70%

4. **Build**
   - Docker image build
   - Cache otimizado

### Status Badges

Adicione ao README principal:

```markdown
[![CI](https://github.com/henriqueneves87/spd_gateway/workflows/CI/badge.svg)](https://github.com/henriqueneves87/spd_gateway/actions)
[![Coverage](https://codecov.io/gh/henriqueneves87/spd_gateway/branch/main/graph/badge.svg)](https://codecov.io/gh/henriqueneves87/spd_gateway)
```

## 📝 Issue Templates

### Bug Report

Template estruturado para reportar bugs:
- Descrição do problema
- Passos para reproduzir
- Ambiente
- Logs
- Checklist de dados sensíveis

### Feature Request

Template para sugerir novas funcionalidades:
- Problema que resolve
- Solução proposta
- Impacto estimado
- Considerações de segurança

## 🔀 Pull Request Template

Checklist completo para PRs:
- ✅ Código e convenções
- ✅ Testes
- ✅ Segurança (PCI DSS)
- ✅ Documentação
- ✅ CI/CD

## 💰 Funding

Configuração de sponsorship (opcional).

## 🔐 Secrets Necessários

Para o CI/CD funcionar completamente, configure os seguintes secrets no GitHub:

### Repository Secrets

```
CODECOV_TOKEN          # Token do Codecov (opcional)
```

### Environment Secrets (para deploy)

```
RENDER_API_KEY         # API key do Render
SUPABASE_URL          # URL do Supabase
SUPABASE_KEY          # Key do Supabase
ADIQ_CLIENT_ID        # Client ID da Adiq
ADIQ_CLIENT_SECRET    # Client Secret da Adiq
```

## 🚀 Como Usar

### Criar Issue

1. Vá para [Issues](https://github.com/henriqueneves87/spd_gateway/issues)
2. Clique em "New Issue"
3. Escolha o template apropriado
4. Preencha todas as seções

### Criar Pull Request

1. Crie uma branch: `git checkout -b feature/nome-da-feature`
2. Faça commits: `git commit -m "feat: descrição"`
3. Push: `git push origin feature/nome-da-feature`
4. Abra PR no GitHub
5. Preencha o template
6. Aguarde CI passar
7. Solicite review

### Verificar CI

1. Vá para [Actions](https://github.com/henriqueneves87/spd_gateway/actions)
2. Veja o status dos workflows
3. Clique em um workflow para ver detalhes
4. Corrija erros se necessário

## 📊 Branch Protection

Recomendações para proteger branches:

### Branch `main`

- ✅ Require pull request reviews (1 aprovação)
- ✅ Require status checks to pass (CI)
- ✅ Require branches to be up to date
- ✅ Include administrators
- ✅ Restrict who can push

### Branch `develop`

- ✅ Require pull request reviews (1 aprovação)
- ✅ Require status checks to pass (CI)
- ✅ Require branches to be up to date

## 🏷️ Labels Recomendados

```
# Tipo
bug                    # Bugs
enhancement           # Novas features
documentation         # Documentação
refactor              # Refatoração
security              # Segurança

# Prioridade
priority:critical     # Crítico
priority:high         # Alta
priority:medium       # Média
priority:low          # Baixa

# Status
status:in-progress    # Em progresso
status:blocked        # Bloqueado
status:review         # Em revisão
status:ready          # Pronto

# Área
area:api              # API
area:database         # Banco de dados
area:security         # Segurança
area:tests            # Testes
area:docs             # Documentação

# Outros
good-first-issue      # Bom para iniciantes
help-wanted           # Precisa de ajuda
wontfix               # Não será corrigido
duplicate             # Duplicado
```

## 📞 Suporte

Para dúvidas sobre configuração do GitHub:
- Abra uma [Discussion](https://github.com/henriqueneves87/spd_gateway/discussions)
- Entre em contato: dev@spdpay.com

---

**Mantenha este diretório atualizado conforme o projeto evolui!**
