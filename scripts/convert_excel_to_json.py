"""
Script para converter planilha Excel em JSON
"""
import pandas as pd
import json

# Ler a planilha
excel_file = "docs/gateway-ecommerce-roteito-testes 3.xlsx"
df = pd.read_excel(excel_file)

# Converter para JSON
json_data = df.to_json(orient='records', indent=2, force_ascii=False)

# Salvar
with open('docs/testes_certificacao.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

print("✅ Arquivo convertido para: docs/testes_certificacao.json")
print(f"Total de testes: {len(df)}")
