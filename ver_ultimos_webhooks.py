"""
Ver últimos webhooks no banco
"""
from src.db.client import supabase

print("Consultando últimos webhooks...")

webhooks = supabase.table("webhook_logs")\
    .select("*")\
    .order("created_at", desc=True)\
    .limit(5)\
    .execute()

if webhooks.data:
    print(f"\n✅ Total: {len(webhooks.data)} webhooks\n")
    for w in webhooks.data:
        print(f"ID: {w['id']}")
        print(f"Event: {w['event_type']}")
        print(f"Payment ID: {w.get('payment_id', 'N/A')}")
        print(f"Processado: {w['processed']}")
        print(f"Erro: {w.get('error', 'N/A')}")
        print(f"Recebido em: {w['received_at']}")
        print(f"Criado em: {w['created_at']}")
        print("-" * 50)
else:
    print("❌ Nenhum webhook no banco")
