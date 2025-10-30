"""
Teste de Todas as Bandeiras de Cartão
Testa Visa, Mastercard, Amex, Hipercard e Elo
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

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
print("TESTE DE TODAS AS BANDEIRAS")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"🌐 Base URL: {BASE_URL}")
print(f"🔑 Merchant ID: {MERCHANT_ID}")
print(f"\n📊 Total de bandeiras: {len(CARTOES)}")

resultados = []

for bandeira, dados_cartao in CARTOES.items():
    print("\n" + "=" * 80)
    print(f"🎴 TESTANDO: {bandeira.upper()}")
    print("=" * 80)
    
    # 1. Criar Invoice
    print(f"\n1️⃣ Criando invoice...")
    invoice_payload = {
        "merchant_id": MERCHANT_ID,
        "customer_id": CUSTOMER_ID,
        "amount": 1000,
        "currency": "BRL",
        "description": f"Teste {bandeira}"
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
            resultados.append({
                "bandeira": bandeira,
                "status": "FALHOU",
                "erro": "Erro ao criar invoice"
            })
            continue
        
        invoice = response.json()
        invoice_id = invoice["id"]
        print(f"✅ Invoice criada: {invoice_id}")
        
        # 2. Processar Pagamento
        print(f"\n2️⃣ Processando pagamento...")
        payment_payload = {
            "invoice_id": invoice_id,
            "pan": dados_cartao["pan"],
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
                "transaction_status": payment['status'],
                "invoice_id": invoice_id
            })
        else:
            print(f"❌ PAGAMENTO RECUSADO")
            print(f"   Status Code: {response.status_code}")
            print(f"   Erro: {response.text[:200]}")
            
            resultados.append({
                "bandeira": bandeira,
                "status": "RECUSADO",
                "erro": response.text[:200],
                "invoice_id": invoice_id
            })
        
        # Aguardar 2 segundos entre testes
        time.sleep(2)
        
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Servidor demorou mais de 120 segundos")
        resultados.append({
            "bandeira": bandeira,
            "status": "TIMEOUT",
            "erro": "Timeout após 120 segundos"
        })
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        resultados.append({
            "bandeira": bandeira,
            "status": "ERRO",
            "erro": str(e)
        })

# Resumo Final
print("\n" + "=" * 80)
print("📊 RESUMO DOS TESTES")
print("=" * 80)

aprovados = [r for r in resultados if r["status"] == "APROVADO"]
recusados = [r for r in resultados if r["status"] == "RECUSADO"]
erros = [r for r in resultados if r["status"] not in ["APROVADO", "RECUSADO"]]

print(f"\n✅ Aprovados: {len(aprovados)}/{len(CARTOES)}")
print(f"❌ Recusados: {len(recusados)}/{len(CARTOES)}")
print(f"⚠️  Erros: {len(erros)}/{len(CARTOES)}")

if aprovados:
    print("\n✅ BANDEIRAS APROVADAS:")
    for r in aprovados:
        print(f"   • {r['bandeira']}")
        print(f"     Payment ID: {r['payment_id']}")
        print(f"     Auth Code: {r['authorization_code']}")

if recusados:
    print("\n❌ BANDEIRAS RECUSADAS:")
    for r in recusados:
        print(f"   • {r['bandeira']}")
        print(f"     Erro: {r['erro'][:100]}")

if erros:
    print("\n⚠️  ERROS:")
    for r in erros:
        print(f"   • {r['bandeira']}: {r['status']}")
        if 'erro' in r:
            print(f"     {r['erro'][:100]}")

# Salvar resultados
print("\n" + "=" * 80)
print("💾 Salvando resultados...")
with open('docs/resultados_todas_bandeiras.json', 'w', encoding='utf-8') as f:
    json.dump({
        "data_execucao": datetime.now().isoformat(),
        "total_testes": len(CARTOES),
        "aprovados": len(aprovados),
        "recusados": len(recusados),
        "erros": len(erros),
        "taxa_sucesso": f"{(len(aprovados)/len(CARTOES)*100):.1f}%",
        "resultados": resultados
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Resultados salvos em: docs/resultados_todas_bandeiras.json")

print("\n" + "=" * 80)
print("🎉 TESTES CONCLUÍDOS!")
print("=" * 80)

# Taxa de sucesso
taxa = (len(aprovados) / len(CARTOES)) * 100
if taxa == 100:
    print("\n🎊 PERFEITO! Todas as bandeiras funcionando!")
elif taxa >= 80:
    print(f"\n✅ ÓTIMO! {taxa:.1f}% das bandeiras funcionando!")
elif taxa >= 60:
    print(f"\n👍 BOM! {taxa:.1f}% das bandeiras funcionando!")
else:
    print(f"\n⚠️  ATENÇÃO! Apenas {taxa:.1f}% das bandeiras funcionando!")
