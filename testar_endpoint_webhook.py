"""
Testar endpoint de webhook do Render
"""
import requests

URL = "https://spd-gateway.onrender.com/v1/webhooks/adiq"

print(f"Testando endpoint: {URL}")

# Simular webhook da Adiq
payload = {
    "Date": "2025-10-30T14:35:00",
    "OrderNumber": "TEST001",
    "PaymentId": "020061252510301733450001281820620000000000",
    "PaymentMethod": "Credit",
    "Amount": "1000",
    "StatusCode": "0",
    "StatusDescription": "Captura - Sucesso"
}

print(f"\nPayload:")
print(payload)

print(f"\nEnviando POST...")
response = requests.post(
    URL,
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=30
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print(f"\n✅ Endpoint funcionando!")
else:
    print(f"\n❌ Endpoint com problema")
