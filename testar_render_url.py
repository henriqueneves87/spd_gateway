"""
Testar se Render está no ar
"""
import requests
import time

URL = "https://spd-gateway.onrender.com"

print("Testando Render...")
print(f"URL: {URL}")

for i in range(3):
    print(f"\nTentativa {i+1}/3...")
    try:
        response = requests.get(f"{URL}/health", timeout=30)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ ESTÁ NO AR!")
            print(f"Response: {response.json()}")
            break
        else:
            print(f"⚠️  Retornou {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"⏳ Timeout - Ainda não está pronto")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Ainda não está no ar")
    except Exception as e:
        print(f"⚠️  Erro: {str(e)}")
    
    if i < 2:
        print("Aguardando 10 segundos...")
        time.sleep(10)

print("\n" + "="*50)
print("Se não funcionou, aguarde mais 2-3 minutos")
