# -*- coding: utf-8 -*-
"""
Script simplificado para executar testes de certificacao Adiq
"""
import csv
import requests
import json
import sys
from datetime import datetime

# Configuracoes
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "password"
MERCHANT_ID = "fb93c667-fbab-47ea-b3c7-9dd27231244a"
CUSTOMER_ID = "3b415031-7236-425e-bc8f-35c7a5f572ab"

# Cartoes de teste (Tokens frescos - gerar antes de cada execução)
# IMPORTANTE: Rodar 'python scripts/gerar_token.py' antes de executar os testes!
CARTOES = {
    "Visa": {
        "card_token": "4D2745DC-A299-4A72-B374-8FDC3A11ECAB",
        "brand": "visa",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123"
    },
    "Mastercard": {
        "card_token": "72F2FD4E-45FA-43A6-BA95-8153DA5FE7D0",
        "brand": "mastercard",
        "expiration_month": "12",
        "expiration_year": "25",
        "cvv": "123"
    }
}


def criar_invoice(amount, description):
    """Cria uma invoice via API"""
    url = f"{BASE_URL}/v1/invoices"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "merchant_id": MERCHANT_ID,
        "customer_id": CUSTOMER_ID,
        "amount": amount,
        "currency": "BRL",
        "description": description
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["id"]
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao criar invoice: {e}")
        if hasattr(e.response, 'text'):
            print(f"Detalhes: {e.response.text}")
        return None


def processar_pagamento(invoice_id, bandeira, installments, capture_type="ac"):
    """Processa um pagamento via API"""
    url = f"{BASE_URL}/v1/payments/"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    if bandeira not in CARTOES:
        print(f"AVISO: Bandeira {bandeira} nao configurada")
        return None
    
    cartao = CARTOES[bandeira]
    
    if not cartao.get("card_token"):
        print(f"  ERRO: Token não disponível! Execute: python gerar_token.py")
        return None
    
    # Usar token pré-gerado
    payload = {
        "invoice_id": invoice_id,
        "card_token": cartao["card_token"],
        "brand": cartao["brand"],
        "cardholder_name": "JOSE DA SILVA",
        "expiration_month": cartao["expiration_month"],
        "expiration_year": cartao["expiration_year"],
        "security_code": cartao["cvv"],
        "installments": installments,
        "capture_type": capture_type
    }
    
    print(f"  Usando token: {cartao['card_token'][:20]}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao processar pagamento: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Detalhes: {e.response.text}")
        return None


def executar_teste(teste_num, tipo_transacao, bandeira, parcelas, valor):
    """Executa um teste especifico"""
    print(f"\n--- Teste #{teste_num} ---")
    print(f"Tipo: {tipo_transacao} | Bandeira: {bandeira}")
    print(f"Parcelas: {parcelas} | Valor: R$ {valor/100:.2f}")
    
    # Determinar capture_type
    capture_type = "ac" if tipo_transacao == "Auto-Captura" else "pa"
    
    # Determinar numero de parcelas
    if parcelas == "1":
        num_parcelas = 1
    elif parcelas == ">1":
        num_parcelas = 3
    else:
        try:
            num_parcelas = int(parcelas)
        except:
            num_parcelas = 1
    
    # Criar invoice
    description = f"Teste #{teste_num} - {tipo_transacao} {bandeira}"
    invoice_id = criar_invoice(valor, description)
    
    if not invoice_id:
        print("FALHOU: Nao foi possivel criar invoice")
        return None
    
    print(f"Invoice criada: {invoice_id}")
    
    # Processar pagamento
    resultado = processar_pagamento(
        invoice_id=invoice_id,
        bandeira=bandeira,
        installments=num_parcelas,
        capture_type=capture_type
    )
    
    if resultado:
        print(f"SUCESSO!")
        print(f"  Payment ID: {resultado.get('payment_id', 'N/A')}")
        print(f"  Auth Code: {resultado.get('authorization_code', 'N/A')}")
        print(f"  Status: {resultado.get('status', 'N/A')}")
        
        return {
            "teste_num": teste_num,
            "invoice_id": invoice_id,
            "payment_id": resultado.get("payment_id", ""),
            "authorization_code": resultado.get("authorization_code", ""),
            "tid": resultado.get("tid", ""),
            "nsu": resultado.get("nsu", ""),
            "status": resultado.get("status", ""),
            "amount": valor,
            "installments": num_parcelas
        }
    else:
        print("FALHOU: Nao foi possivel processar pagamento")
        return None


def main():
    print("=" * 60)
    print("Testes de Certificacao Adiq - Spdpay Gateway")
    print(f"Horario: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Ler planilha
    print("\nLendo planilha de testes...")
    try:
        with open('docs/gateway-ecommerce-roteito-testes 3.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            testes = list(reader)
    except Exception as e:
        print(f"ERRO ao ler planilha: {e}")
        return
    
    print(f"Total de testes na planilha: {len(testes)}")
    
    # Testes prioritarios
    testes_prioritarios = [1, 3, 4]
    print(f"Executando testes: {testes_prioritarios}")
    
    resultados = []
    
    for teste in testes:
        # Pegar numero do teste (primeira coluna)
        valores = list(teste.values())
        if not valores:
            continue
            
        teste_num_str = valores[0].strip()
        
        # Pular se nao for numero
        if not teste_num_str.isdigit():
            continue
        
        teste_num = int(teste_num_str)
        
        # Pular se nao for prioritario
        if teste_num not in testes_prioritarios:
            continue
        
        # Extrair dados do teste
        # REAL: 0=#, 1=TipoCredito, 2=Ação, 3=Bandeira, 4=TipoProduto, 5=Parcelas, 6=Valor, 7=Cofre
        tipo_credito = valores[1].strip() if len(valores) > 1 else "Credito"
        acao = valores[2].strip() if len(valores) > 2 else "Autorizar"
        bandeira = valores[3].strip() if len(valores) > 3 else "Visa"
        tipo_produto = valores[4].strip() if len(valores) > 4 else "a Vista"
        parcelas = valores[5].strip() if len(valores) > 5 else "1"
        valor_str = valores[6].strip() if len(valores) > 6 else "1000"
        
        # Determinar tipo de transacao baseado na acao
        tipo_transacao = "Auto-Captura" if "Autorizar" in acao and "Capturar" not in acao else "Pre-Autorizacao"
        
        # Debug - mostrar TODOS os valores
        print(f"  Valores completos: {valores[:10]}")
        print(f"  Lido: tipo={tipo_transacao}, bandeira={bandeira}, parcelas={parcelas}, valor={valor_str}")
        
        # Converter valor
        try:
            valor = int(valor_str)
        except:
            print(f"AVISO: Valor invalido para teste #{teste_num}, usando 1000")
            valor = 1000
        
        # Executar teste
        resultado = executar_teste(
            teste_num=teste_num,
            tipo_transacao=tipo_transacao,
            bandeira=bandeira,
            parcelas=parcelas,
            valor=valor
        )
        
        if resultado:
            resultados.append(resultado)
    
    # Salvar resultados
    print("\n" + "=" * 60)
    print("Salvando resultados...")
    
    with open('docs/resultados_testes.json', 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"Resultados salvos em: docs/resultados_testes.json")
    print(f"Total de testes executados: {len(resultados)}")
    
    # Mostrar resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    for r in resultados:
        print(f"\nTeste #{r['teste_num']}:")
        print(f"  Payment ID: {r['payment_id']}")
        print(f"  Auth Code: {r['authorization_code']}")
        print(f"  Status: {r['status']}")
    
    print("\n" + "=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)


if __name__ == "__main__":
    main()
