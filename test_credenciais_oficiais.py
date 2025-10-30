"""
Teste das Credenciais Oficiais da Adiq
Recebidas em 30/10/2025
"""
import requests
import json
from datetime import datetime

# Credenciais Oficiais
CLIENT_ID = "A40A208C-0914-479D-BA17-BBD6E9063991"
CLIENT_SECRET = "D597E2B5-2BF2-48D1-A682-26C58F83D0EF"
BASE_URL = "https://ecommerce-hml.adiq.io"

print("=" * 80)
print("TESTE DE CREDENCIAIS OFICIAIS DA ADIQ")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"\n🔑 Client ID: {CLIENT_ID}")
print(f"🔐 Client Secret: {CLIENT_SECRET[:8]}...{CLIENT_SECRET[-8:]}")
print(f"🌐 Base URL: {BASE_URL}")

# 1. Testar Autenticação
print("\n" + "=" * 80)
print("1️⃣ TESTE DE AUTENTICAÇÃO")
print("=" * 80)

auth_url = f"{BASE_URL}/auth/oauth2/v1/token"

# Basic Auth
import base64
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
basic_auth = base64.b64encode(credentials.encode()).decode()

auth_payload = {
    "grantType": "client_credentials"
}

print(f"\n📤 POST {auth_url}")
print(f"📝 Payload: {json.dumps(auth_payload, indent=2)}")

try:
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/json"
    }
    response = requests.post(auth_url, json=auth_payload, headers=headers, timeout=30)
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        auth_data = response.json()
        access_token = auth_data.get("accessToken")
        expires_in = auth_data.get("expiresIn")
        
        print(f"✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
        print(f"\n🎫 Access Token: {access_token[:20]}...{access_token[-20:]}")
        if expires_in:
            print(f"⏱️  Expira em: {expires_in} segundos ({int(expires_in)/60:.1f} minutos)")
        else:
            print(f"⏱️  Expira em: Não informado")
        
        # 2. Testar Tokenização
        print("\n" + "=" * 80)
        print("2️⃣ TESTE DE TOKENIZAÇÃO")
        print("=" * 80)
        
        token_url = f"{BASE_URL}/v1/tokens/cards"
        token_payload = {
            "cardNumber": "4761739001010036"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n📤 POST {token_url}")
        print(f"📝 Payload: {json.dumps(token_payload, indent=2)}")
        
        token_response = requests.post(token_url, json=token_payload, headers=headers, timeout=30)
        
        print(f"\n📊 Status Code: {token_response.status_code}")
        
        if token_response.status_code in [200, 201]:
            token_data = token_response.json()
            card_token = token_data.get("numberToken") or token_data.get("token")
            
            print(f"✅ TOKENIZAÇÃO BEM-SUCEDIDA!")
            print(f"\n🎴 Card Token: {card_token}")
            print(f"📋 Response completo:")
            print(json.dumps(token_data, indent=2))
            
            # 3. Resumo Final
            print("\n" + "=" * 80)
            print("📊 RESUMO DOS TESTES")
            print("=" * 80)
            print("\n✅ Autenticação: SUCESSO")
            print("✅ Tokenização: SUCESSO")
            print("\n🎉 CREDENCIAIS OFICIAIS FUNCIONANDO PERFEITAMENTE!")
            print("\n💡 Próximos passos:")
            print("   1. Atualizar .env com as novas credenciais")
            print("   2. Executar testes completos: python run_tests.py")
            print("   3. Testar no Swagger: http://localhost:8000/docs")
            
        else:
            print(f"❌ ERRO NA TOKENIZAÇÃO")
            print(f"📄 Response: {token_response.text}")
            
    else:
        print(f"❌ ERRO NA AUTENTICAÇÃO")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 401:
            print("\n⚠️  ERRO 401: Credenciais inválidas")
            print("   - Verifique Client ID e Client Secret")
            print("   - Confirme se as credenciais estão ativas no portal Adiq")
        elif response.status_code == 403:
            print("\n⚠️  ERRO 403: Acesso negado")
            print("   - Credenciais podem não ter permissões necessárias")
        elif response.status_code == 404:
            print("\n⚠️  ERRO 404: Endpoint não encontrado")
            print("   - Verifique a URL base")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT: Servidor demorou mais de 30 segundos para responder")
    print("   - Tente novamente")
    print("   - Verifique sua conexão com a internet")
    
except requests.exceptions.ConnectionError:
    print("\n❌ ERRO DE CONEXÃO: Não foi possível conectar ao servidor")
    print("   - Verifique sua conexão com a internet")
    print("   - Verifique se a URL está correta")
    
except Exception as e:
    print(f"\n❌ ERRO INESPERADO: {str(e)}")

print("\n" + "=" * 80)
print("FIM DOS TESTES")
print("=" * 80)
