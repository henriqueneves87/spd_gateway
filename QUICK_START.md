# ⚡ Quick Start - Spdpay Gateway

## 🎯 Objetivo

Testar o gateway de pagamentos em **5 minutos**!

---

## 1️⃣ Iniciar o Servidor

```bash
cd c:\spdpay_gateway
uvicorn src.main:app --reload
```

✅ Servidor rodando em: http://localhost:8000

---

## 2️⃣ Testar com Postman

### Importar Collection

1. Abra o Postman
2. **Import** → Selecione: `docs/Spdpay_Gateway.postman_collection.json`
3. Pronto!

### Configurar Environment

1. **Environments** → **Create Environment**
2. Nome: `Spdpay Local`
3. Adicione:

```
base_url = http://localhost:8000
api_key = password
merchant_id = fb93c667-fbab-47ea-b3c7-9dd27231244a
customer_id = 3b415031-7236-425e-bc8f-35c7a5f572ab
```

4. **Save** e selecione o environment

---

## 3️⃣ Executar Testes

### Teste 1: Health Check ✅

**Request:** `Health Check`

Deve retornar:
```json
{"status": "healthy"}
```

### Teste 2: Criar Invoice ✅

**Request:** `Invoices > Create Invoice`

Clique em **Send**

✅ Invoice criada! (variável `invoice_id` preenchida automaticamente)

### Teste 3: Processar Pagamento ✅

**IMPORTANTE:** Gere um token fresco primeiro!

```bash
python gerar_token.py
```

Copie o **Visa Token** e cole na variável `card_token` do environment.

**Request:** `Payments > Create Payment (with Token)`

Clique em **Send**

✅ **PAGAMENTO APROVADO!** 🎉

---

## 🎴 Ou use PAN diretamente (mais fácil!)

**Request:** `Payments > Create Payment (with PAN)`

Body já vem com o PAN do Visa:
```json
{
  "pan": "4761739001010036",
  ...
}
```

Clique em **Send**

✅ **Gateway tokeniza automaticamente!** 🚀

---

## 📊 Ver Resultado

**Request:** `Payments > Get Payment`

Retorna:
```json
{
  "status": "CAPTURED",
  "payment_id": "020085619310292014490007157884210000000000",
  "authorization_code": "275505",
  ...
}
```

---

## 🎯 Pronto!

Você testou:
- ✅ Health Check
- ✅ Criar Invoice
- ✅ Processar Pagamento
- ✅ Consultar Resultado

**Gateway 100% funcional!** 🎉

---

## 📚 Próximos Passos

- Ver documentação completa: `docs/API_DOCUMENTATION.md`
- Guia do Postman: `docs/POSTMAN_GUIDE.md`
- Swagger interativo: http://localhost:8000/docs

---

## ⚠️ Problemas?

### Token expirado
```bash
python gerar_token.py
```

### Servidor não inicia
```bash
pip install -r requirements.txt
```

### 401 Unauthorized
Verifique se `X-API-Key: password` está no header

---

**Bons testes!** 🚀
