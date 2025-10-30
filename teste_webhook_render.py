"""
Teste Completo - Pagamento e Webhook via Render
"""
import requests
import base64
import time
from datetime import datetime

# URLs
RENDER_URL = "https://spd-gateway.onrender.com"
ADIQ_BASE_URL = "https://ecommerce-hml.adiq.io"

# Credenciais
CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

print("=" * 80)
print("TESTE WEBHOOK - RENDER + ADIQ")
print("=" * 80)
print(f"\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"🌐 Render URL: {RENDER_URL}")

# 1. Testar se Render está no ar
print("\n1️⃣ Testando se Render está online...")
try:
    response = requests.get(f"{RENDER_URL}/health", timeout=30)
    if response.status_code == 200:
        print(f"✅ Render está online!")
        print(f"   {response.json()}")
    else:
        print(f"❌ Render retornou {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Erro ao acessar Render: {str(e)}")
    exit(1)

# 2. Autenticar na Adiq
print("\n2️⃣ Autenticando na Adiq...")
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
    exit(1)

access_token = auth_response.json()["accessToken"]
print(f"✅ Token obtido")

# 3. Tokenizar cartão
print("\n3️⃣ Tokenizando cartão Visa...")
token_response = requests.post(
    f"{ADIQ_BASE_URL}/v1/tokens/cards",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={"cardNumber": "4761739001010036"},
    timeout=30
)

if token_response.status_code != 200:
    print(f"❌ Erro ao tokenizar: {token_response.status_code}")
    exit(1)

card_token = token_response.json()["numberToken"]
print(f"✅ Token: {card_token[:20]}...")

# 4. Criar Invoice via Render
print("\n4️⃣ Criando invoice via Render...")
invoice_response = requests.post(
    f"{RENDER_URL}/v1/invoices",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "merchant_id": MERCHANT_ID,
        "customer_id": CUSTOMER_ID,
        "amount": 1000,
        "currency": "BRL",
        "description": "Teste webhook Render"
    },
    timeout=30
)

if invoice_response.status_code != 201:
    print(f"❌ Erro ao criar invoice: {invoice_response.status_code}")
    print(f"   {invoice_response.text}")
    exit(1)

invoice_id = invoice_response.json()["id"]
print(f"✅ Invoice: {invoice_id}")

# 5. Processar Pagamento via Render
print("\n5️⃣ Processando pagamento via Render...")
payment_response = requests.post(
    f"{RENDER_URL}/v1/payments/",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "invoice_id": invoice_id,
        "card_token": card_token,
        "brand": "visa",
        "cardholder_name": "JOSE DA SILVA",
        "expiration_month": "12",
        "expiration_year": "25",
        "security_code": "123",
        "installments": 1,
        "capture_type": "ac"
    },
    timeout=120
)

print(f"\n📊 Status: {payment_response.status_code}")

if payment_response.status_code == 201:
    payment = payment_response.json()
    print(f"✅ PAGAMENTO APROVADO!")
    print(f"   Payment ID: {payment['payment_id']}")
    print(f"   Auth Code: {payment.get('authorization_code', 'N/A')}")
    print(f"   Status: {payment['status']}")
    
    payment_id = payment['payment_id']
    
    # 6. Aguardar webhook
    print(f"\n6️⃣ Aguardando webhook da Adiq...")
    print(f"   A Adiq deve enviar para: {RENDER_URL}/v1/webhooks/adiq")
    print(f"   Aguardando 30 segundos...")
    
    for i in range(6):
        time.sleep(5)
        print(f"   {30 - (i+1)*5} segundos restantes...")
    
    # 7. Verificar webhook no Supabase
    print(f"\n7️⃣ Verificando se webhook foi recebido...")
    
    from src.db.client import supabase
    
    webhooks = supabase.table("webhook_logs")\
        .select("*")\
        .eq("payment_id", payment_id)\
        .order("received_at", desc=True)\
        .execute()
    
    if webhooks.data:
        print(f"✅ WEBHOOK RECEBIDO!")
        print(f"   Total: {len(webhooks.data)}")
        
        for webhook in webhooks.data:
            print(f"\n   📡 Webhook:")
            print(f"      Event: {webhook['event_type']}")
            print(f"      Payment ID: {webhook['payment_id']}")
            print(f"      Processado: {webhook['processed']}")
            print(f"      Recebido em: {webhook['received_at']}")
    else:
        print(f"❌ WEBHOOK NÃO RECEBIDO")
        print(f"\n   ⚠️  Possíveis causas:")
        print(f"      1. Webhook não configurado na Adiq")
        print(f"      2. Adiq ainda não enviou (pode demorar)")
        print(f"      3. URL incorreta na Adiq")
        
        # Verificar últimos webhooks
        all_webhooks = supabase.table("webhook_logs")\
            .select("id, event_type, payment_id, received_at")\
            .order("received_at", desc=True)\
            .limit(5)\
            .execute()
        
        if all_webhooks.data:
            print(f"\n   📋 Últimos webhooks recebidos:")
            for w in all_webhooks.data:
                print(f"      • {w['event_type']} - {w['payment_id']} - {w['received_at']}")
        
else:
    print(f"❌ PAGAMENTO FALHOU")
    print(f"   {payment_response.text}")

print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)
print(f"""
✅ Render: Online
✅ Pagamento: {'Aprovado' if payment_response.status_code == 201 else 'Falhou'}
{'✅' if webhooks.data else '❌'} Webhook: {'Recebido' if webhooks.data else 'Não recebido'}

💡 PRÓXIMOS PASSOS:
   {'1. Webhook funcionando! Sistema completo!' if webhooks.data else '1. Configurar webhook na Adiq'}
   {'2. Testar em produção' if webhooks.data else '2. Enviar e-mail para Adiq com URL:'}
   {'   ' + RENDER_URL + '/v1/webhooks/adiq' if not webhooks.data else ''}
""")

print("=" * 80)
print("✅ TESTE CONCLUÍDO")
print("=" * 80)
