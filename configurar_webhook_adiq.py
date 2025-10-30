"""
Configurar Webhook na Adiq via API
"""
import requests
import base64
import json
from datetime import datetime

# Credenciais
CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"
ADIQ_BASE_URL = "https://ecommerce-hml.adiq.io"

# URL do webhook (webhook.site para teste)
WEBHOOK_URL = "https://webhook.site/833e5a6a-fa12-4230-9606-cce1f23de3e5"

print("=" * 80)
print("CONFIGURAR WEBHOOK NA ADIQ")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"🌐 Base URL: {ADIQ_BASE_URL}")
print(f"📍 Webhook URL: {WEBHOOK_URL}")

# 1. Autenticar na Adiq
print("\n1️⃣ Autenticando na Adiq...")
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
basic_auth = base64.b64encode(credentials.encode()).decode()

auth_response = requests.post(
    f"{ADIQ_BASE_URL}/auth/oauth2/v1/token",
    headers={
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/json"
    },
    json={"grantType": "client_credentials"},
    timeout=30
)

if auth_response.status_code != 200:
    print(f"❌ Erro na autenticação: {auth_response.status_code}")
    print(f"   {auth_response.text}")
    exit(1)

access_token = auth_response.json()["accessToken"]
print(f"✅ Token obtido: {access_token[:30]}...")

# 2. Configurar Webhook
print("\n2️⃣ Configurando webhook...")

webhook_config = {
    "PostBackUrl": WEBHOOK_URL,
    "PostBackEnabled": True,
    "Headers": []  # Sem headers customizados por enquanto
}

print(f"\n📝 Payload:")
print(json.dumps(webhook_config, indent=2))

webhook_response = requests.post(
    f"{ADIQ_BASE_URL}/v1/merchants/webhook",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json=webhook_config,
    timeout=30
)

print(f"\n📊 Status Code: {webhook_response.status_code}")

if webhook_response.status_code in [200, 201, 204]:
    print(f"✅ WEBHOOK CONFIGURADO COM SUCESSO!")
    print(f"\n🎉 A Adiq agora vai enviar notificações para:")
    print(f"   {WEBHOOK_URL}")
    
    if webhook_response.text:
        print(f"\n📄 Resposta:")
        try:
            print(json.dumps(webhook_response.json(), indent=2))
        except:
            print(webhook_response.text)
else:
    print(f"❌ ERRO ao configurar webhook")
    print(f"📄 Resposta: {webhook_response.text}")

print("\n" + "=" * 80)
print("📋 PRÓXIMOS PASSOS")
print("=" * 80)
print("""
1. Acesse: https://webhook.site/#!/833e5a6a-fa12-4230-9606-cce1f23de3e5
2. Faça um pagamento de teste
3. Veja o webhook chegar em tempo real!
4. Depois, configure com a URL do seu servidor:
   - Local (ngrok): https://abc123.ngrok.io/v1/webhooks/adiq
   - Render: https://spdpay-gateway.onrender.com/v1/webhooks/adiq
""")

print("\n" + "=" * 80)
print("✅ CONFIGURAÇÃO CONCLUÍDA")
print("=" * 80)
