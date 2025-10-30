"""
Configurar Webhook do Render na Adiq
"""
import requests
import base64
import json
from datetime import datetime

# Credenciais
CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"
ADIQ_BASE_URL = "https://ecommerce-hml.adiq.io"

# URL do webhook no Render
WEBHOOK_URL = "https://spd-gateway.onrender.com/v1/webhooks/adiq"

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
    "postBackUrl": WEBHOOK_URL,
    "postbackEnabled": True,
    "headers": []
}

print(f"\n📝 Payload:")
print(json.dumps(webhook_config, indent=2))

# Tentar endpoint /v1/merchant/webhook
print(f"\n📡 Tentando: POST /v1/merchant/webhook")
webhook_response = requests.post(
    f"{ADIQ_BASE_URL}/v1/merchant/webhook",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json=webhook_config,
    timeout=30
)

print(f"📊 Status Code: {webhook_response.status_code}")

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
            
elif webhook_response.status_code == 403:
    print(f"❌ ERRO 403 - Sem permissão")
    print(f"\n⚠️  Suas credenciais não têm permissão para configurar webhook via API.")
    print(f"\n📧 SOLUÇÃO: Enviar e-mail para Adiq")
    print(f"\n" + "=" * 80)
    print("TEMPLATE DE E-MAIL PARA ADIQ")
    print("=" * 80)
    print(f"""
Para: suporte@adiq.com.br
Assunto: Configuração de Webhook - Spdpay Gateway

Olá equipe Adiq,

Precisamos configurar o webhook para receber notificações de pagamento.

INFORMAÇÕES:
- Client ID: {CLIENT_ID}
- Ambiente: Homologação (HML)
- URL do Webhook: {WEBHOOK_URL}

EVENTOS SOLICITADOS:
- payment.authorized
- payment.captured
- payment.settled
- payment.declined
- payment.cancelled
- payment.refunded

Tentamos configurar via API (POST /v1/merchant/webhook) mas recebemos 403 Forbidden.

Poderiam configurar o webhook ou nos informar como proceder?

Aguardamos retorno.

Atenciosamente,
Henrique Neves
Spdpay Gateway
""")
    
else:
    print(f"❌ ERRO ao configurar webhook")
    print(f"📄 Resposta: {webhook_response.text}")
    
    # Tentar endpoint alternativo
    print(f"\n📡 Tentando endpoint alternativo: POST /v1/merchants/webhook")
    webhook_response2 = requests.post(
        f"{ADIQ_BASE_URL}/v1/merchants/webhook",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=webhook_config,
        timeout=30
    )
    
    print(f"📊 Status Code: {webhook_response2.status_code}")
    
    if webhook_response2.status_code in [200, 201, 204]:
        print(f"✅ WEBHOOK CONFIGURADO COM SUCESSO!")
        print(f"\n🎉 A Adiq agora vai enviar notificações para:")
        print(f"   {WEBHOOK_URL}")
    else:
        print(f"❌ Também falhou: {webhook_response2.text}")
        print(f"\n⚠️  Necessário configurar via portal admin ou contatar Adiq")

print("\n" + "=" * 80)
print("📋 PRÓXIMOS PASSOS")
print("=" * 80)
print(f"""
1. Se configurado com sucesso:
   ✅ Fazer pagamento de teste
   ✅ Verificar se webhook chega
   
2. Se recebeu 403:
   📧 Enviar e-mail para Adiq (template acima)
   ⏳ Aguardar configuração
   
3. Testar webhook:
   python teste_webhook_render.py
""")

print("\n" + "=" * 80)
print("✅ SCRIPT CONCLUÍDO")
print("=" * 80)
