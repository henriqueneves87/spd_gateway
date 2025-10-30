"""
Teste Completo: Pagamento + Webhook
1. Cria invoice
2. Processa pagamento
3. Simula webhook da Adiq
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 70)
print("TESTE COMPLETO: PAGAMENTO + WEBHOOK")
print("=" * 70)

# 1. Criar Invoice
print("\n1️⃣ Criando Invoice...")
invoice_payload = {
    "merchant_id": MERCHANT_ID,
    "customer_id": CUSTOMER_ID,
    "amount": 1000,
    "currency": "BRL",
    "description": "Teste webhook"
}

response = requests.post(f"{BASE_URL}/v1/invoices", headers=headers, json=invoice_payload)
if response.status_code != 201:
    print(f"❌ Erro ao criar invoice: {response.text}")
    exit(1)

invoice = response.json()
invoice_id = invoice["id"]
print(f"✅ Invoice criada: {invoice_id}")

# 2. Processar Pagamento
print("\n2️⃣ Processando Pagamento...")
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

response = requests.post(f"{BASE_URL}/v1/payments/", headers=headers, json=payment_payload, timeout=120)
if response.status_code != 201:
    print(f"❌ Erro ao processar pagamento: {response.text}")
    exit(1)

payment = response.json()
payment_id = payment["payment_id"]
transaction_id = payment["transaction_id"]
auth_code = payment["authorization_code"]

print(f"✅ Pagamento aprovado!")
print(f"   Payment ID: {payment_id}")
print(f"   Transaction ID: {transaction_id}")
print(f"   Auth Code: {auth_code}")

# 3. Aguardar 2 segundos
print("\n⏳ Aguardando 2 segundos...")
time.sleep(2)

# 4. Simular Webhook da Adiq
print("\n3️⃣ Simulando Webhook da Adiq...")
webhook_payload = {
    "eventType": "payment.settled",
    "eventId": f"evt_{int(time.time())}",
    "timestamp": "2025-10-30T12:00:00Z",
    "paymentId": payment_id,
    "status": "Settled",
    "authorizationCode": auth_code,
    "amount": 1000
}

webhook_headers = {
    "Content-Type": "application/json",
    "X-Webhook-Signature": "test_signature_123"
}

response = requests.post(
    f"{BASE_URL}/v1/webhooks/adiq",
    headers=webhook_headers,
    json=webhook_payload,
    timeout=10
)

print(f"\n📊 Status Code: {response.status_code}")

try:
    response_data = response.json()
    print(f"📄 Response:")
    print(json.dumps(response_data, indent=2))
except:
    print(f"📄 Response (text): {response.text}")

if response.status_code == 200:
    print("\n✅ Webhook processado com sucesso!")
    print("\n🎯 Verificações:")
    print(f"   1. Transaction {transaction_id} deve estar como SETTLED")
    print(f"   2. Invoice {invoice_id} deve estar como PAID")
    print(f"   3. Webhook deve estar logado em webhook_logs")
else:
    print(f"\n❌ Erro ao processar webhook")

print("\n" + "=" * 70)
