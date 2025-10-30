# 🚀 Deploy no Render - Guia Completo

## ✅ Por Que Render?

```
✅ URL pública automática: https://spdpay-gateway.onrender.com
✅ SSL/HTTPS grátis (necessário para webhooks)
✅ Deploy automático via GitHub
✅ Logs em tempo real
✅ Plano gratuito disponível
✅ Variáveis de ambiente seguras
```

---

## 📋 Passo a Passo

### 1. **Criar Conta no Render**

1. Acesse: https://render.com
2. Clique em **Sign Up**
3. Conecte com GitHub

---

### 2. **Preparar Repositório GitHub**

Certifique-se que seu código está no GitHub:

```bash
# Se ainda não fez push
git add .
git commit -m "feat: preparar para deploy no Render"
git push origin main
```

---

### 3. **Criar Web Service no Render**

1. No dashboard do Render, clique em **New +**
2. Selecione **Web Service**
3. Conecte seu repositório GitHub
4. Selecione: `henriqueneves87/spd_gateway`

---

### 4. **Configurar o Service**

#### Configurações Básicas:
```
Name: spdpay-gateway
Region: Oregon (US West)
Branch: main
Runtime: Python 3
```

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

#### Instance Type:
```
Free (512 MB RAM, compartilhado)
```

---

### 5. **Configurar Variáveis de Ambiente**

Clique em **Environment** e adicione:

```env
# Ambiente
ENV=production

# Supabase
SUPABASE_URL=https://ndcfypvqspylcbbewhmi.supabase.co
SUPABASE_KEY=seu_supabase_key_aqui

# Adiq
ADIQ_BASE_URL=https://ecommerce-hml.adiq.io
ADIQ_CLIENT_ID=A40A208C-0914-479D-BA17-BBD6E9063991
ADIQ_CLIENT_SECRET=D597E2B5-2BF2-48D1-A682-26C58F83D0EF
```

⚠️ **IMPORTANTE:** Use as variáveis reais do seu `.env`

---

### 6. **Deploy!**

1. Clique em **Create Web Service**
2. Aguarde o build (3-5 minutos)
3. Render vai gerar uma URL: `https://spdpay-gateway.onrender.com`

---

## 🎯 Configurar Webhook na Adiq

Depois do deploy, você terá uma URL pública:

```
https://spdpay-gateway.onrender.com/v1/webhooks/adiq
```

### Registrar na Adiq:

1. Acesse: https://admin-spdpaydigital-hml.adiq.io/
2. Menu: **Configurações → Webhooks**
3. Adicionar webhook:
   ```
   URL: https://spdpay-gateway.onrender.com/v1/webhooks/adiq
   Método: POST
   Eventos: ☑️ Todos de pagamento
   ```
4. Salvar

---

## 🧪 Testar

### 1. Verificar se está no ar:
```bash
curl https://spdpay-gateway.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Testar API:
```bash
curl https://spdpay-gateway.onrender.com/docs
```

Deve abrir o Swagger UI.

### 3. Fazer pagamento de teste:

Use o Swagger ou Postman apontando para:
```
https://spdpay-gateway.onrender.com
```

### 4. Verificar webhook:

```sql
SELECT * FROM webhook_logs 
WHERE received_at > NOW() - INTERVAL '1 hour'
ORDER BY received_at DESC;
```

---

## 📊 Monitoramento

### Ver Logs em Tempo Real:

1. No dashboard do Render
2. Clique no seu service
3. Aba **Logs**
4. Veja logs em tempo real

### Métricas:

1. Aba **Metrics**
2. Veja CPU, memória, requests

---

## ⚙️ Configurações Avançadas

### Auto-Deploy:

Por padrão, Render faz deploy automático a cada push no GitHub.

Para desabilitar:
1. Settings → Build & Deploy
2. Desmarque **Auto-Deploy**

### Custom Domain:

Se tiver domínio próprio:
1. Settings → Custom Domains
2. Adicionar: `api.seudominio.com`
3. Configurar DNS

### Health Check:

Render verifica automaticamente:
```
GET /health
```

Se falhar 3x, reinicia o serviço.

---

## 💰 Plano Gratuito

### Limites:
```
✅ 512 MB RAM
✅ CPU compartilhado
✅ SSL grátis
✅ Deploy ilimitado
⚠️ Dorme após 15 min de inatividade
⚠️ Primeiro request pode demorar (cold start)
```

### Upgrade para Paid ($7/mês):
```
✅ Sem cold start
✅ Mais RAM e CPU
✅ Melhor performance
```

---

## 🔧 Troubleshooting

### Build falha:

**Erro:** `ModuleNotFoundError`
**Solução:** Verificar `requirements.txt`

### Service não inicia:

**Erro:** `Application startup failed`
**Solução:** Verificar variáveis de ambiente

### Webhook não chega:

**Erro:** Webhook não aparece nos logs
**Solução:** 
1. Verificar URL na Adiq
2. Verificar logs do Render
3. Testar endpoint manualmente

---

## 📝 Checklist de Deploy

- [ ] Código no GitHub
- [ ] `requirements.txt` atualizado
- [ ] `render.yaml` criado
- [ ] Conta no Render criada
- [ ] Web Service criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Health check funcionando
- [ ] Swagger acessível
- [ ] Webhook URL registrada na Adiq
- [ ] Pagamento de teste realizado
- [ ] Webhook recebido e processado

---

## 🎉 Resultado Final

Depois do deploy, você terá:

```
✅ API rodando em: https://spdpay-gateway.onrender.com
✅ Swagger em: https://spdpay-gateway.onrender.com/docs
✅ Webhook em: https://spdpay-gateway.onrender.com/v1/webhooks/adiq
✅ SSL/HTTPS automático
✅ Logs em tempo real
✅ Deploy automático via GitHub
```

---

## 🚀 Comandos Úteis

### Forçar novo deploy:
```bash
git commit --allow-empty -m "trigger deploy"
git push
```

### Ver logs via CLI:
```bash
# Instalar Render CLI
npm install -g render-cli

# Login
render login

# Ver logs
render logs -f spdpay-gateway
```

---

## 📚 Documentação

- Render Docs: https://render.com/docs
- Deploy Python: https://render.com/docs/deploy-fastapi
- Environment Variables: https://render.com/docs/environment-variables

---

## ✅ Vantagens vs ngrok

| Feature | Render | ngrok |
|---------|--------|-------|
| URL permanente | ✅ | ❌ (muda sempre) |
| SSL/HTTPS | ✅ | ✅ |
| Uptime 24/7 | ✅ | ❌ (precisa rodar) |
| Logs | ✅ | Limitado |
| Deploy automático | ✅ | ❌ |
| Grátis | ✅ | ✅ (limitado) |
| Produção | ✅ | ❌ (só teste) |

---

**Render é MUITO melhor que ngrok para produção!** 🎯

---

Última atualização: 30/10/2025 11:41
