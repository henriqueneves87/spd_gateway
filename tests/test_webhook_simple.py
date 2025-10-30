"""
Teste Simples de Webhook - Apenas verifica se o endpoint responde
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Webhook simples
webhook_payload = {
    "eventType": "payment.captured",
    "paymentId": "020048967410301230120007230412810000000000",
    "status": "Captured",
    "authorizationCode": "223899"
}

print("=" * 70)
print("TESTE SIMPLES DE WEBHOOK")
print("=" * 70)

print("\n📝 Payload:")
print(json.dumps(webhook_payload, indent=2))

print("\n📤 Enviando para:", f"{BASE_URL}/v1/webhooks/adiq")

headers = {
    "Content-Type": "application/json",
    "X-Webhook-Signature": "test_signature"
}

try:
    response = requests.post(
        f"{BASE_URL}/v1/webhooks/adiq",
        headers=headers,
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
        print("\n✅ Webhook recebido com sucesso!")
    else:
        print(f"\n❌ Erro ao processar webhook")
        
except Exception as e:
    print(f"\n❌ Erro na requisição: {e}")

print("\n" + "=" * 70)
print("\n💡 Dica: Verifique os logs do servidor para mais detalhes")
print("=" * 70)
