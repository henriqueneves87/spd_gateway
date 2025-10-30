"""
Teste que simula exatamente o que o Swagger faz
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 70)
print("TESTE: Simulando fluxo do Swagger")
print("=" * 70)

# 1. Criar Invoice
print("\n1. Criando Invoice...")
invoice_payload = {
    "merchant_id": MERCHANT_ID,
    "customer_id": CUSTOMER_ID,
    "amount": 1000,
    "currency": "BRL",
    "description": "Teste Swagger Flow"
}

response = requests.post(f"{BASE_URL}/v1/invoices", headers=headers, json=invoice_payload)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    invoice = response.json()
    invoice_id = invoice["id"]
    print(f"✅ Invoice criada: {invoice_id}")
else:
    print(f"❌ Erro: {response.text}")
    exit(1)

# 2. Processar Pagamento com PAN (como no Swagger)
print("\n2. Processando Pagamento com PAN...")
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

print(f"Payload: {json.dumps(payment_payload, indent=2)}")
print("\nEnviando requisição...")

try:
    response = requests.post(
        f"{BASE_URL}/v1/payments/", 
        headers=headers, 
        json=payment_payload,
        timeout=120  # 2 minutos
    )
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        payment = response.json()
        print("\n✅ SUCESSO!")
        print(f"Payment ID: {payment.get('payment_id')}")
        print(f"Auth Code: {payment.get('authorization_code')}")
        print(f"Status: {payment.get('status')}")
        print(f"Transaction ID: {payment.get('transaction_id')}")
    else:
        print(f"\n❌ ERRO:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n⏰ TIMEOUT - Servidor demorou mais de 2 minutos")
except Exception as e:
    print(f"\n❌ ERRO: {e}")

print("\n" + "=" * 70)
