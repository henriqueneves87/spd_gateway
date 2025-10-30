# 🐳 Deploy na VPS com Docker

**Guia completo para fazer deploy do Spdpay Gateway na sua VPS usando Docker**

---

## 📋 Pré-requisitos na VPS

```bash
# 1. Docker instalado
docker --version

# 2. Docker Compose instalado
docker-compose --version

# 3. Git instalado
git --version

# 4. Porta 8000 liberada no firewall
sudo ufw allow 8000
```

---

## 🚀 Passo a Passo

### 1. **Conectar na VPS**

```bash
ssh usuario@seu-ip-vps
```

### 2. **Clonar Repositório**

```bash
# Ir para diretório de aplicações
cd /opt  # ou ~/apps

# Clonar
git clone https://github.com/henriqueneves87/spd_gateway.git
cd spd_gateway
```

### 3. **Criar Arquivo .env**

```bash
nano .env
```

Cole o conteúdo:

```env
# Supabase
SUPABASE_URL=https://ndcfypvqspylcbbewhmi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kY2Z5cHZxc3B5bGNiYmV3aG1pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NDk0NDQsImV4cCI6MjA3NzMyNTQ0NH0.Su_A2tWbwBilrMydQYkN6VRlPxUkko2Kmd-RJOIC6s0

# Adiq Homologação
ADIQ_BASE_URL=https://ecommerce-hml.adiq.io
ADIQ_CLIENT_ID=A40A208C-0914-479D-BA17-BBD6E9063991
ADIQ_CLIENT_SECRET=D597E2B5-2BF2-48D1-A682-26C58F83D0EF

# Ambiente
ENV=production
LOG_LEVEL=INFO

# Security
JWT_SECRET=8KzP9mN4vR2xQ7wL6tY3hJ5nB1cF0dG8sA4eU9iO2pM7kV6xZ3qW1rT5yH4jN8bC
API_KEY_HEADER=X-API-Key

# Server
HOST=0.0.0.0
PORT=8000
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. **Build e Start**

```bash
# Build da imagem
docker-compose build

# Subir container
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 5. **Verificar se Está Rodando**

```bash
# Ver containers
docker ps

# Testar health
curl http://localhost:8000/health

# Ver logs
docker-compose logs -f api
```

---

## 🌐 Configurar Nginx (Opcional mas Recomendado)

### 1. **Instalar Nginx**

```bash
sudo apt update
sudo apt install nginx
```

### 2. **Criar Configuração**

```bash
sudo nano /etc/nginx/sites-available/spdpay
```

Cole:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;  # ou IP da VPS

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. **Ativar Site**

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/spdpay /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 4. **Configurar SSL com Let's Encrypt (Opcional)**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática já está configurada!
```

---

## 🔄 Atualizar Aplicação

```bash
# Entrar no diretório
cd /opt/spd_gateway

# Pull das mudanças
git pull origin main

# Rebuild e restart
docker-compose down
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f
```

---

## 📊 Comandos Úteis

### Ver Logs
```bash
# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Logs de um serviço específico
docker-compose logs -f api
```

### Gerenciar Container
```bash
# Parar
docker-compose stop

# Iniciar
docker-compose start

# Reiniciar
docker-compose restart

# Parar e remover
docker-compose down

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Monitoramento
```bash
# Ver uso de recursos
docker stats

# Entrar no container
docker-compose exec api bash

# Ver processos
docker-compose top
```

---

## 🔧 Configurar Webhook na Adiq

Depois que a aplicação estiver rodando:

### 1. **Obter URL Pública**

Se usar Nginx:
```
http://seu-ip-vps/v1/webhooks/adiq
```

Com domínio:
```
https://seu-dominio.com/v1/webhooks/adiq
```

### 2. **Configurar na Adiq**

```bash
# Na sua máquina local, editar o script
nano configurar_webhook_render.py

# Mudar a URL:
WEBHOOK_URL = "http://seu-ip-vps/v1/webhooks/adiq"

# Executar
python configurar_webhook_render.py
```

---

## 🐛 Troubleshooting

### Container não inicia
```bash
# Ver logs de erro
docker-compose logs

# Verificar se porta está em uso
sudo netstat -tulpn | grep 8000

# Rebuild sem cache
docker-compose build --no-cache
```

### Erro de permissão
```bash
# Dar permissão ao Docker
sudo usermod -aG docker $USER
newgrp docker
```

### Aplicação não responde
```bash
# Verificar health
curl http://localhost:8000/health

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart
```

### Firewall bloqueando
```bash
# Liberar porta 8000
sudo ufw allow 8000

# Liberar porta 80 (Nginx)
sudo ufw allow 80

# Liberar porta 443 (HTTPS)
sudo ufw allow 443

# Ver status
sudo ufw status
```

---

## 📋 Checklist de Deploy

- [ ] VPS com Docker instalado
- [ ] Repositório clonado
- [ ] Arquivo `.env` criado
- [ ] Build da imagem realizado
- [ ] Container rodando (`docker ps`)
- [ ] Health check OK (`curl http://localhost:8000/health`)
- [ ] Nginx configurado (opcional)
- [ ] SSL configurado (opcional)
- [ ] Firewall liberado
- [ ] Webhook configurado na Adiq
- [ ] Teste de pagamento realizado
- [ ] Webhook recebido e processado

---

## 🎯 URLs Importantes

**API:**
```
http://seu-ip-vps:8000
```

**Swagger:**
```
http://seu-ip-vps:8000/docs
```

**Health Check:**
```
http://seu-ip-vps:8000/health
```

**Webhook:**
```
http://seu-ip-vps:8000/v1/webhooks/adiq
```

---

## 🚀 Vantagens da VPS vs Render

✅ **Deploy instantâneo** (segundos vs minutos)  
✅ **Controle total** do ambiente  
✅ **Sem cold start** (sempre ativo)  
✅ **Logs em tempo real**  
✅ **Debug mais fácil**  
✅ **Performance melhor**  

---

## 💡 Dicas

1. **Use `screen` ou `tmux`** para manter sessões ativas
2. **Configure backup automático** do `.env`
3. **Monitore logs** regularmente
4. **Configure alertas** para erros
5. **Documente** mudanças no servidor

---

**Última atualização:** 30/10/2025  
**Versão:** 1.0.0
