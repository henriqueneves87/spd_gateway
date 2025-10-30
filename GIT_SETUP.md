# 🚀 Setup Git - Spdpay Gateway

## 📋 Pré-requisitos

Você precisa ter:
- ✅ Conta no GitHub/GitLab/Bitbucket
- ✅ Git instalado localmente
- ✅ Repositório remoto criado

---

## 🔧 Opção 1: GitHub

### 1. Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome: `spdpay-gateway`
3. Descrição: `Gateway de pagamentos integrado com Adiq`
4. **NÃO** inicialize com README (já temos)
5. **NÃO** adicione .gitignore (já temos)
6. Clique em **Create repository**

### 2. Conectar Repositório Local

```bash
# Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/spdpay-gateway.git

# Verificar
git remote -v

# Push inicial
git push -u origin master
```

---

## 🔧 Opção 2: GitLab

### 1. Criar Repositório no GitLab

1. Acesse: https://gitlab.com/projects/new
2. Nome: `spdpay-gateway`
3. Descrição: `Gateway de pagamentos integrado com Adiq`
4. Visibilidade: Private
5. **NÃO** inicialize com README
6. Clique em **Create project**

### 2. Conectar Repositório Local

```bash
# Adicionar remote
git remote add origin https://gitlab.com/SEU-USUARIO/spdpay-gateway.git

# Push inicial
git push -u origin master
```

---

## 🔧 Opção 3: Bitbucket

### 1. Criar Repositório no Bitbucket

1. Acesse: https://bitbucket.org/repo/create
2. Nome: `spdpay-gateway`
3. Descrição: `Gateway de pagamentos integrado com Adiq`
4. Acesso: Private
5. Clique em **Create repository**

### 2. Conectar Repositório Local

```bash
# Adicionar remote
git remote add origin https://bitbucket.org/SEU-USUARIO/spdpay-gateway.git

# Push inicial
git push -u origin master
```

---

## 🔐 Autenticação

### GitHub (Token)

1. Acesse: https://github.com/settings/tokens
2. Generate new token (classic)
3. Selecione: `repo` (full control)
4. Copie o token
5. Use no lugar da senha ao fazer push

### SSH (Recomendado)

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar no GitHub/GitLab/Bitbucket
# Settings → SSH Keys → Add SSH Key

# Usar SSH remote
git remote set-url origin git@github.com:SEU-USUARIO/spdpay-gateway.git
```

---

## 📝 Comandos Úteis

### Verificar Status
```bash
git status
git log --oneline
git remote -v
```

### Criar Branch
```bash
git checkout -b develop
git push -u origin develop
```

### Atualizar
```bash
git pull origin master
```

### Desfazer Mudanças
```bash
git reset --soft HEAD~1  # Desfaz último commit (mantém mudanças)
git reset --hard HEAD~1  # Desfaz último commit (perde mudanças)
```

---

## 🎯 Workflow Recomendado

### Branches

```
master (main)     → Produção (sempre estável)
  ↓
develop           → Desenvolvimento (integração)
  ↓
feature/xxx       → Features específicas
```

### Exemplo

```bash
# Criar branch de feature
git checkout -b feature/webhook-improvements

# Fazer mudanças
git add .
git commit -m "feat: melhorias no webhook"

# Push
git push -u origin feature/webhook-improvements

# Criar Pull Request no GitHub
```

---

## 🔒 Segurança

### ⚠️ NUNCA commitar:

- ❌ `.env` (credenciais)
- ❌ `*.log` (logs podem ter dados sensíveis)
- ❌ Tokens de API
- ❌ Senhas
- ❌ Chaves privadas

### ✅ Já está protegido:

- ✅ `.gitignore` configurado
- ✅ `.env.example` (template sem credenciais)
- ✅ Arquivos sensíveis ignorados

---

## 📊 Após o Push

### Verificar no GitHub

1. Acesse: `https://github.com/SEU-USUARIO/spdpay-gateway`
2. Verifique:
   - ✅ 100 arquivos
   - ✅ README.md aparecendo
   - ✅ Estrutura de pastas correta

### Configurar Repositório

1. **About** → Adicionar descrição e tags
2. **Settings** → Configurar branch protection
3. **Actions** → Configurar CI/CD (opcional)

---

## 🎉 Pronto!

Seu código está no Git e pronto para ser compartilhado!

### Próximos Passos

1. ✅ Código no Git
2. 📝 Adicionar colaboradores
3. 🔄 Configurar CI/CD
4. 📦 Deploy em produção

---

## 🆘 Problemas Comuns

### "Permission denied"
```bash
# Verificar SSH
ssh -T git@github.com

# Ou usar HTTPS com token
```

### "Repository not found"
```bash
# Verificar URL
git remote -v

# Corrigir se necessário
git remote set-url origin URL-CORRETA
```

### "Push rejected"
```bash
# Forçar push (cuidado!)
git push -f origin master

# Ou pull primeiro
git pull origin master --rebase
```

---

**Repositório configurado e pronto!** 🚀
