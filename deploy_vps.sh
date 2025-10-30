#!/bin/bash

# Script de Deploy Rápido na VPS
# Uso: ./deploy_vps.sh

set -e

echo "=================================="
echo "🚀 DEPLOY SPDPAY GATEWAY NA VPS"
echo "=================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Pull das mudanças
echo -e "\n${YELLOW}1️⃣ Atualizando código...${NC}"
git pull origin main

# 2. Parar containers
echo -e "\n${YELLOW}2️⃣ Parando containers...${NC}"
docker-compose down

# 3. Build
echo -e "\n${YELLOW}3️⃣ Fazendo build...${NC}"
docker-compose build

# 4. Subir
echo -e "\n${YELLOW}4️⃣ Subindo containers...${NC}"
docker-compose up -d

# 5. Aguardar health check
echo -e "\n${YELLOW}5️⃣ Aguardando aplicação iniciar...${NC}"
sleep 5

# 6. Testar
echo -e "\n${YELLOW}6️⃣ Testando health check...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Aplicação está rodando!${NC}"
else
    echo -e "${RED}❌ Erro: Aplicação não respondeu${NC}"
    echo -e "${YELLOW}Ver logs:${NC} docker-compose logs -f"
    exit 1
fi

# 7. Ver logs
echo -e "\n${YELLOW}7️⃣ Últimas linhas dos logs:${NC}"
docker-compose logs --tail=20

echo -e "\n${GREEN}=================================="
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "==================================${NC}"

echo -e "\n📊 Status:"
docker-compose ps

echo -e "\n💡 Comandos úteis:"
echo "  Ver logs:      docker-compose logs -f"
echo "  Reiniciar:     docker-compose restart"
echo "  Parar:         docker-compose stop"
echo "  Ver status:    docker-compose ps"

echo -e "\n🌐 URLs:"
echo "  API:      http://localhost:8000"
echo "  Swagger:  http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo "  Webhook:  http://localhost:8000/v1/webhooks/adiq"

echo -e "\n${GREEN}🎉 Pronto para usar!${NC}"
