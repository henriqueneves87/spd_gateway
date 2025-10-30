# 🗺️ Roadmap — Spdpay Gateway

Documenta as fases evolutivas do produto, garantindo escalabilidade de features e segurança PCI.

---

## 🚧 Fase 1 — MVP do Gateway
**Objetivo:** parceiros conseguem criar faturas e pagar via cartão usando o gateway Spdpay + Adiq.

Escopo:
- [ ] API FastAPI + Render + Supabase
- [ ] Domain model: merchants, customers, invoices, transactions
- [ ] States: `PENDING → PROCESSING → PAID / FAILED`
- [ ] Adiq Authorization + Capture (`captureType=ac`)
- [ ] Webhook Adiq: update transaction & invoice status
- [ ] API Key por merchant (mínimo viável)
- [ ] Logs estruturados (correlação por `invoice_id`)
- [ ] Healthcheck + API docs

Critérios de aceitação:
- ERP consegue gerar cobranças em produção
- Certificação Adiq concluída para cartão de crédito

Entrega: ✅ Gateway operacional

---

## 📦 Fase 2 — Dev Experience e Segurança Avançada
**Objetivo:** Desenvolvedores amam integrar com a Spdpay ❤️

- [ ] **Postman Collection Spdpay** (exemplos de todos os endpoints)
- [ ] SDK JS para integradores (`@spdpay/sdk`)
- [ ] Idempotência robusta (store requestId)
- [ ] Antifraude via `sellerInfo` + e-mail rules
- [ ] 3DS com `DeviceInfo`
- [ ] API Keys rotacionáveis
- [ ] Tracking e Observabilidade
- [ ] Rate Limiting por merchant
- [ ] Playground interativo (Swagger UI customizado)

Entrega: integração simples e segura

---

## 🛍️ Fase 3 — UX e White-Label
**Objetivo:** Gateway completo para e-commerce

- [ ] Hosted Checkout
- [ ] Tokenização client-side (fora do PCI)
- [ ] Zero-Auth Tests
- [ ] Temas/branding por merchant

Entrega: ERP pode integrar sem desenvolver front-end

---

## 🔁 Fase 4 — Recorrência
**Objetivo:** Soluções para assinaturas

- [ ] Recurrence Engine (rebills automáticos)
- [ ] Captura tardia (`PA → Capture`)
- [ ] Refunds e cancelamentos por API
- [ ] Vencimento inteligente + retentativa

Entrega: modelo de negócio SaaS completo

---

## 🧩 Fase 5 — Arranjo Completo
**Objetivo:** Produto de pagamentos full stack

- [ ] Split Marketplace
- [ ] Pix e Boleto
- [ ] Portal Lojista evoluído + Dashboard
- [ ] Notificações 360º
- [ ] Exportações para contabilidade e conciliação

Entrega: ecossistema Spdpay forte e competitivo

---

## 📌 RFCs e Mudanças Futuras

Toda feature que altere:
- Estados de pagamento
- Regras PCI
- Autenticação
- Campos da integração

deve ser formalizada via RFC interna antes da implementação.

---

> Evolução guiada pela certificação Adiq e pela experiência dos parceiros.

