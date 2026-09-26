# magicpin AI Challenge — Vera Merchant Assistant Solution

## Team & Overview
- **Team**: Team Vera Elite
- **Model / Approach**: Deterministic 4-Context Semantic Composer with Zero-Latency Intent Execution & Automated Auto-Reply Elimination
- **Version**: 1.0.0

---

## 1. Architecture & 4-Context Composition

The solution implements the exact 4-context architecture requested by magicpin:
1. **CategoryContext**: Ingests category voice profiles, clinical/operational taboos, peer benchmarks, digests, and localized catalogs across 5 verticals (`dentists`, `salons`, `restaurants`, `gyms`, `pharmacies`).
2. **MerchantContext**: Grounded in real Google Business Profile metrics (CTR, views, calls), active catalog offers (service + price rather than generic discounts), customer aggregates, and locality anchors.
3. **TriggerContext**: Handles all external events (research digests, regulatory compliance deadlines, festivals, competitor openings) and internal signals (performance spikes, dips, milestone achievements, renewals, dormant states, curious asks).
4. **CustomerContext**: Powers WhatsApp customer outreach on behalf of merchants (`merchant_on_behalf`) honoring language preferences (e.g. natural Hindi-English code-mixing), recall windows, and appointment dates.

---

## 2. Solving Production Vera's Biggest Weaknesses

1. **Auto-Reply Elimination**: WhatsApp Business automated canned replies ("Thank you for contacting...", "hamari team tak pahuncha deti hoon") are detected at turn 1. Rather than burning multiple turns, the bot backs off or politely concludes with zero chat pollution.
2. **Immediate Intent Handoff**: When a merchant indicates commitment ("yes", "ok let's do it", "what's next"), the bot immediately switches to **ACTION mode**—executing the task and confirming completion without looping back to qualifying questions.
3. **Zero Hallucination & High Specificity**: Every message is anchored in verifiable numbers (trial sample size, CTR delta %, exact dates, rupee values) directly from the provided context.
4. **Single Binary CTA**: Replaces multi-choice clutter with high-converting binary commitments (`Reply YES to publish`).

---

## 3. Endpoints & Deliverables

- `bot.py`: Complete core composition and reply engine.
- `server.py`: Standard HTTP server exposing all 5 judge endpoints:
  - `GET /v1/healthz`
  - `GET /v1/metadata`
  - `POST /v1/context`
  - `POST /v1/tick`
  - `POST /v1/reply`
- `submission.jsonl`: 30 canonical test pair responses scored against the evaluation rubric.
- `test_harness.py`: Automated verification running warmup, auto-reply detection, intent handoff, and hostile message tests.
