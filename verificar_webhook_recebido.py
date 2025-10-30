"""
Verificar se webhook foi recebido
"""
from src.db.client import supabase
import time

PAYMENT_ID = "020061252510301733450001281820620000000000"

print("Verificando webhooks...")
print(f"Payment ID: {PAYMENT_ID}")

for i in range(6):
    print(f"\nTentativa {i+1}/6...")
    
    webhooks = supabase.table("webhook_logs")\
        .select("*")\
        .eq("payment_id", PAYMENT_ID)\
        .execute()
    
    if webhooks.data:
        print(f"✅ WEBHOOK RECEBIDO!")
        for w in webhooks.data:
            print(f"\nEvent: {w['event_type']}")
            print(f"Processado: {w['processed']}")
            print(f"Recebido em: {w['received_at']}")
            print(f"Payload: {w['payload']}")
        break
    else:
        print(f"❌ Ainda não recebido")
        if i < 5:
            print("Aguardando 10 segundos...")
            time.sleep(10)

if not webhooks.data:
    print(f"\n⚠️  Webhook não chegou após 60 segundos")
    print(f"\nVerificando últimos webhooks...")
    
    all_webhooks = supabase.table("webhook_logs")\
        .select("*")\
        .order("received_at", desc=True)\
        .limit(3)\
        .execute()
    
    if all_webhooks.data:
        print(f"\nÚltimos webhooks:")
        for w in all_webhooks.data:
            print(f"  • {w['event_type']} - {w['payment_id']} - {w['received_at']}")
    else:
        print(f"Nenhum webhook no banco")
