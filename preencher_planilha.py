"""
Script para preencher a planilha de certificação com os resultados dos testes
"""
import csv
import json
from datetime import datetime

# Ler resultados dos testes
with open('docs/resultados_testes.json', 'r', encoding='utf-8') as f:
    resultados = json.load(f)

print("=" * 80)
print("PREENCHIMENTO DA PLANILHA DE CERTIFICAÇÃO")
print("=" * 80)
print(f"\nData: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"Total de resultados: {len(resultados)}")

# Ler planilha original
planilha_entrada = 'docs/gateway-ecommerce-roteito-testes 3.csv'
planilha_saida = 'docs/gateway-ecommerce-roteito-testes-preenchida.csv'

linhas = []
with open(planilha_entrada, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    linhas = list(reader)

print(f"\nLinhas na planilha: {len(linhas)}")
print(f"Header: {linhas[0]}")

# Preencher resultados
testes_preenchidos = 0
for resultado in resultados:
    teste_num = resultado.get('teste_num')
    payment_id = resultado.get('payment_id', '')
    auth_code = resultado.get('authorization_code', '')
    tid = resultado.get('tid', payment_id)  # TID geralmente é o payment_id
    
    # Encontrar linha correspondente (teste_num é o índice da linha, header é linha 0)
    if teste_num is not None and teste_num < len(linhas):
        linha = linhas[teste_num]
        
        # Preencher colunas (índices baseados no header)
        # Nº Autorização está na coluna 10
        # TID está na coluna 11
        if len(linha) >= 12:
            linha[10] = auth_code  # Nº Autorização
            linha[11] = tid  # TID
            testes_preenchidos += 1
            
            print(f"\n✅ Teste #{teste_num} preenchido:")
            print(f"   Auth Code: {auth_code}")
            print(f"   TID: {tid}")

# Salvar planilha preenchida
with open(planilha_saida, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(linhas)

print("\n" + "=" * 80)
print(f"✅ Planilha preenchida com sucesso!")
print(f"📄 Arquivo salvo: {planilha_saida}")
print(f"📊 Testes preenchidos: {testes_preenchidos}")
print("=" * 80)

# Mostrar resumo
print("\n📋 RESUMO DOS TESTES PREENCHIDOS:")
print("-" * 80)
for resultado in resultados:
    teste_num = resultado.get('teste_numero')
    bandeira = resultado.get('bandeira', 'N/A')
    parcelas = resultado.get('parcelas', 'N/A')
    auth_code = resultado.get('authorization_code', 'N/A')
    status = resultado.get('status', 'N/A')
    
    print(f"Teste #{teste_num}: {bandeira} {parcelas}x - Auth: {auth_code} - Status: {status}")

print("\n💡 Próximos passos:")
print("   1. Revisar arquivo: docs/gateway-ecommerce-roteito-testes-preenchida.csv")
print("   2. Abrir no Excel/Google Sheets")
print("   3. Validar dados preenchidos")
print("   4. Enviar para Adiq")
