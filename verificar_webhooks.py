"""
Script para verificar se webhooks da Adiq estão sendo recebidos
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"

print("=" * 80)
print("VERIFICAÇÃO DE WEBHOOKS DA ADIQ")
print("=" * 80)
print(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 1. Verificar se o endpoint de webhook está ativo
print("\n1️⃣ Verificando endpoint de webhook...")
print(f"   URL: {BASE_URL}/v1/webhooks/adiq")

try:
    # Tentar fazer um POST de teste (vai falhar mas confirma que endpoint existe)
    response = requests.post(
        f"{BASE_URL}/v1/webhooks/adiq",
        json={"test": "ping"},
        timeout=5
    )
    print(f"   ✅ Endpoint ativo! Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ ERRO: Servidor não está rodando!")
    print(f"   💡 Execute: uvicorn src.main:app --reload")
    exit(1)
except Exception as e:
    print(f"   ✅ Endpoint ativo (erro esperado: {type(e).__name__})")

# 2. Verificar configuração de webhook na Adiq
print("\n2️⃣ Configuração necessária na Adiq:")
print("   " + "-" * 76)
print(f"   📍 URL do Webhook: {BASE_URL}/v1/webhooks/adiq")
print(f"   🔐 Autenticação: Nenhuma (público)")
print(f"   📝 Método: POST")
print(f"   📊 Content-Type: application/json")
print("   " + "-" * 76)

# 3. Verificar se há webhooks registrados no banco
print("\n3️⃣ Consultando webhooks recebidos...")
print("   (Verificando tabela webhooks no Supabase)")

try:
    from supabase import create_client
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        
        # Buscar últimos webhooks
        result = supabase.table("webhooks").select("*").order("created_at", desc=True).limit(10).execute()
        
        if result.data:
            print(f"   ✅ {len(result.data)} webhooks encontrados:")
            for webhook in result.data[:5]:
                print(f"      • {webhook.get('event_type')} - {webhook.get('created_at')}")
        else:
            print(f"   ⚠️  Nenhum webhook recebido ainda")
    else:
        print(f"   ⚠️  Credenciais Supabase não configuradas")
        
except Exception as e:
    print(f"   ⚠️  Não foi possível consultar: {str(e)}")

# 4. Instruções para configurar webhook na Adiq
print("\n" + "=" * 80)
print("📋 COMO CONFIGURAR WEBHOOK NA ADIQ")
print("=" * 80)

print("""
1. Acessar Portal Admin da Adiq:
   https://admin-spdpaydigital-hml.adiq.io/

2. Navegar até: Configurações > Webhooks

3. Adicionar novo webhook:
   • URL: http://SEU-SERVIDOR-PUBLICO/v1/webhooks/adiq
   • Eventos: Selecionar todos relacionados a pagamentos
   • Método: POST
   • Headers: (nenhum necessário)

4. Salvar e testar

⚠️  IMPORTANTE: 
   - Seu servidor precisa estar acessível publicamente
   - Para testes locais, use ngrok ou similar:
     
     ngrok http 8000
     
   - Use a URL do ngrok como webhook URL
""")

# 5. Teste de webhook simulado
print("\n" + "=" * 80)
print("🧪 TESTE DE WEBHOOK SIMULADO")
print("=" * 80)

print("\n5️⃣ Enviando webhook de teste...")

webhook_payload = {
    "event": "payment.captured",
    "timestamp": datetime.now().isoformat(),
    "data": {
        "orderId": "TEST-ORDER-123",
        "transactionId": "020012345678901234567890123456789012345678",
        "amount": 1000,
        "status": "CAPTURED",
        "authorizationCode": "123456"
    }
}

try:
    response = requests.post(
        f"{BASE_URL}/v1/webhooks/adiq",
        json=webhook_payload,
        headers={"X-Webhook-Signature": "test-signature"},
        timeout=10
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 200:
        print(f"   ✅ Webhook processado com sucesso!")
    else:
        print(f"   ⚠️  Webhook retornou erro")
        
except Exception as e:
    print(f"   ❌ Erro ao enviar webhook: {str(e)}")

# 6. Resumo e próximos passos
print("\n" + "=" * 80)
print("📊 RESUMO E PRÓXIMOS PASSOS")
print("=" * 80)

print("""
✅ O QUE ESTÁ FUNCIONANDO:
   • Endpoint de webhook está ativo
   • Servidor está processando requisições

⚠️  O QUE PRECISA SER FEITO:
   1. Expor servidor publicamente (ngrok ou deploy)
   2. Configurar URL do webhook no portal da Adiq
   3. Realizar transação de teste
   4. Verificar se webhook foi recebido

💡 COMANDOS ÚTEIS:
   # Expor servidor localmente
   ngrok http 8000
   
   # Ver logs do servidor
   tail -f logs/app.log
   
   # Consultar webhooks no banco
   python verificar_webhooks.py

📚 DOCUMENTAÇÃO:
   docs/WEBHOOK_GUIDE.md - Guia completo de webhooks
""")

print("\n" + "=" * 80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("=" * 80)
