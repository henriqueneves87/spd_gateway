"""
Teste de Todas as Bandeiras com Tokens
Usa tokens pré-gerados ao invés de PAN
"""
import requests
import json
from datetime import datetime
import time
import base64

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

# Credenciais Adiq
CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"
ADIQ_BASE_URL = "https://ecommerce-hml.adiq.io"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Cartões de teste
CARTOES = {
    "Visa": {
        "pan": "4761739001010036",
        "brand": "visa",
        "expiration_month": "12",
        "expiration_year": "25",
        "security_code": "123"
    },
    "Mastercard": {
        "pan": "5201561050025011",
        "brand": "mastercard",
        "expiration_month": "09",
        "expiration_year": "25",
        "security_code": "123"
    },
    "Amex": {
        "pan": "376470814541000",
        "brand": "amex",
        "expiration_month": "10",
        "expiration_year": "25",
        "security_code": "1234"
    },
    "Hipercard": {
        "pan": "6062828898541988",
        "brand": "hipercard",
        "expiration_month": "09",
        "expiration_year": "25",
        "security_code": "123"
    },
    "Elo": {
        "pan": "5067224275805500",
        "brand": "elo",
        "expiration_month": "11",
        "expiration_year": "25",
        "security_code": "123"
    }
}

print("=" * 80)
print("TESTE DE TODAS AS BANDEIRAS (COM TOKENS)")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

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

access_token = auth_response.json()["accessToken"]
print(f"✅ Token obtido: {access_token[:30]}...")

# 2. Tokenizar todos os cartões
print("\n2️⃣ Tokenizando cartões...")
tokens = {}

for bandeira, dados in CARTOES.items():
    print(f"   Tokenizando {bandeira}...", end=" ")
    
    try:
        token_response = requests.post(
            f"{ADIQ_BASE_URL}/v1/tokens/cards",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"cardNumber": dados["pan"]},
            timeout=30
        )
        
        if token_response.status_code == 200:
            token = token_response.json()["numberToken"]
            tokens[bandeira] = {
                **dados,
                "card_token": token
            }
            print(f"✅ {token}")
        else:
            print(f"❌ Erro: {token_response.status_code}")
            tokens[bandeira] = None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        tokens[bandeira] = None

# 3. Testar pagamentos
print("\n" + "=" * 80)
print("3️⃣ TESTANDO PAGAMENTOS")
print("=" * 80)

resultados = []

for bandeira, dados_cartao in tokens.items():
    if dados_cartao is None:
        print(f"\n❌ {bandeira}: Pulando (tokenização falhou)")
        continue
    
    print("\n" + "=" * 80)
    print(f"🎴 TESTANDO: {bandeira.upper()}")
    print("=" * 80)
    
    # Criar Invoice
    print(f"\n📝 Criando invoice...")
    invoice_payload = {
        "merchant_id": MERCHANT_ID,
        "customer_id": CUSTOMER_ID,
        "amount": 1000,
        "currency": "BRL",
        "description": f"Teste {bandeira} com token"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/invoices",
            headers=headers,
            json=invoice_payload,
            timeout=30
        )
        
        if response.status_code != 201:
            print(f"❌ Erro ao criar invoice")
            continue
        
        invoice_id = response.json()["id"]
        print(f"✅ Invoice: {invoice_id}")
        
        # Processar Pagamento com TOKEN
        print(f"\n💳 Processando pagamento com TOKEN...")
        payment_payload = {
            "invoice_id": invoice_id,
            "card_token": dados_cartao["card_token"],  # ← Usando TOKEN
            "brand": dados_cartao["brand"],
            "cardholder_name": "JOSE DA SILVA",
            "expiration_month": dados_cartao["expiration_month"],
            "expiration_year": dados_cartao["expiration_year"],
            "security_code": dados_cartao["security_code"],
            "installments": 1,
            "capture_type": "ac"
        }
        
        response = requests.post(
            f"{BASE_URL}/v1/payments/",
            headers=headers,
            json=payment_payload,
            timeout=120
        )
        
        if response.status_code == 201:
            payment = response.json()
            print(f"✅ PAGAMENTO APROVADO!")
            print(f"   Payment ID: {payment['payment_id']}")
            print(f"   Auth Code: {payment['authorization_code']}")
            print(f"   Status: {payment['status']}")
            
            resultados.append({
                "bandeira": bandeira,
                "status": "APROVADO",
                "payment_id": payment['payment_id'],
                "authorization_code": payment['authorization_code'],
                "metodo": "TOKEN"
            })
        else:
            print(f"❌ PAGAMENTO RECUSADO: {response.status_code}")
            print(f"   {response.text[:200]}")
            
            resultados.append({
                "bandeira": bandeira,
                "status": "RECUSADO",
                "erro": response.text[:200],
                "metodo": "TOKEN"
            })
        
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        resultados.append({
            "bandeira": bandeira,
            "status": "ERRO",
            "erro": str(e)
        })

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO DOS TESTES (COM TOKENS)")
print("=" * 80)

aprovados = [r for r in resultados if r["status"] == "APROVADO"]
print(f"\n✅ Aprovados: {len(aprovados)}/{len(tokens)}")

if aprovados:
    print("\n✅ BANDEIRAS APROVADAS:")
    for r in aprovados:
        print(f"   • {r['bandeira']}")
        print(f"     Payment ID: {r['payment_id']}")
        print(f"     Auth Code: {r['authorization_code']}")

taxa = (len(aprovados) / len(tokens)) * 100
print(f"\n🎯 Taxa de Sucesso: {taxa:.1f}%")

if taxa == 100:
    print("🎊 PERFEITO! Todas as bandeiras funcionando com tokens!")
