"""
Teste de Transacao para Verificar Webhook
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

print("=" * 80)
print("TESTE DE TRANSACAO PARA VERIFICAR WEBHOOK")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. Criar Invoice
print("\n1️⃣ Criando invoice...")
invoice_payload = {
    "merchant_id": MERCHANT_ID,
    "customer_id": CUSTOMER_ID,
    "amount": 1000,
    "currency": "BRL",
    "description": "Teste de webhook"
}

try:
    response = requests.post(
        f"{BASE_URL}/v1/invoices",
        headers=headers,
        json=invoice_payload,
        timeout=30
    )
    
    if response.status_code != 201:
        print(f"❌ Erro ao criar invoice: {response.status_code}")
        print(f"   {response.text}")
        exit(1)
    
    invoice = response.json()
    invoice_id = invoice["id"]
    print(f"✅ Invoice criada: {invoice_id}")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    exit(1)

# 2. Processar Pagamento com PAN (tokenizacao automatica)
print(f"\n2️⃣ Processando pagamento com PAN...")
payment_payload = {
    "invoice_id": invoice_id,
    "pan": "4761739001010036",
    "brand": "visa",
    "cardholder_name": "JOSE DA SILVA",
    "expiration_month": "12",
    "expiration_year": "25",
    "security_code": "123",
    "installments": 1,
    "capture_type": "ac"
}

try:
    response = requests.post(
        f"{BASE_URL}/v1/payments/",
        headers=headers,
        json=payment_payload,
        timeout=120
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 201:
        payment = response.json()
        print(f"✅ PAGAMENTO APROVADO!")
        print(f"   Payment ID: {payment['payment_id']}")
        print(f"   Auth Code: {payment['authorization_code']}")
        print(f"   Status: {payment['status']}")
        
        payment_id = payment['payment_id']
        
    else:
        print(f"❌ PAGAMENTO RECUSADO")
        print(f"   {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    exit(1)

# 3. Aguardar webhook (30 segundos)
print(f"\n3️⃣ Aguardando webhook da Adiq...")
print(f"   Esperando 30 segundos...")

for i in range(30, 0, -5):
    print(f"   {i} segundos restantes...")
    time.sleep(5)

# 4. Verificar se webhook chegou
print(f"\n4️⃣ Verificando webhooks recebidos...")

from src.db.client import supabase

try:
    # Buscar webhooks dos ultimos 5 minutos
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
            print(f"      Event Type: {webhook['event_type']}")
            print(f"      Payment ID: {webhook['payment_id']}")
            print(f"      Processado: {webhook['processed']}")
            print(f"      Recebido em: {webhook['received_at']}")
            
            if webhook.get('payload'):
                print(f"      Payload:")
                print(f"      {json.dumps(webhook['payload'], indent=6)}")
    else:
        print(f"❌ NENHUM WEBHOOK RECEBIDO")
        print(f"   Payment ID procurado: {payment_id}")
        
        # Buscar todos os webhooks recentes
        all_webhooks = supabase.table("webhook_logs")\
            .select("id, event_type, payment_id, received_at")\
            .order("received_at", desc=True)\
            .limit(5)\
            .execute()
        
        if all_webhooks.data:
            print(f"\n   📋 Últimos webhooks recebidos (qualquer payment):")
            for w in all_webhooks.data:
                print(f"      • {w['event_type']} - {w['payment_id']} - {w['received_at']}")
        else:
            print(f"\n   ⚠️  Nenhum webhook no banco de dados")
            
except Exception as e:
    print(f"❌ Erro ao consultar webhooks: {str(e)}")

print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)
print(f"""
✅ Invoice criada: {invoice_id}
✅ Pagamento aprovado: {payment_id}
⏳ Webhook: Verificar acima

💡 OBSERVAÇÕES:
   - Se webhook NÃO chegou: Adiq não está configurada para enviar
   - Se webhook chegou: Adiq está enviando automaticamente!
   
📝 PRÓXIMOS PASSOS:
   1. Se webhook NÃO chegou: Configurar na Adiq
   2. Se webhook chegou: Está funcionando!
""")

print("=" * 80)
print("✅ TESTE CONCLUÍDO")
print("=" * 80)
