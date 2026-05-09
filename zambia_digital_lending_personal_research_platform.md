# Zambia Digital Lending Personal Research Platform

Version: v0.1  
Current mode: personal research and capability-building  
Commercial status: paused until conflict-of-interest risk is clearly lower

## 1. Positioning

This project is now a private **public-source digital lending market research platform**.

It is designed to help me understand the Zambia digital lending market through public signals:

- regulator and policy pages
- consumer protection pages
- data protection pages
- payment-system and payment-rail regulatory documents
- digital financial services incident categories
- public app listings
- public competitor websites
- public news and notices

The goal is not to sell an intelligence product right now. The goal is to build market understanding and technical capability while keeping strict professional boundaries.

## 2. Current Target: Capability-Building Layer

The platform should help me build four capabilities:

| Capability | What It Means | Evidence |
| --- | --- | --- |
| Public-source collection | Use Scrapling to collect official and public pages conservatively | Source runs recorded in SQLite |
| Lending taxonomy | Classify signals into complaint, fraud, privacy, fees, repayment, disbursement, regulatory, and competitor-change themes | Reviewed signals and category counts |
| Research discipline | Separate source facts from personal interpretation | Research notes linked to signals |
| Weekly synthesis | Turn reviewed signals into personal market notes | Generated weekly markdown notes |
| Source reliability | Decide which public sources can be automated and which need manual review | Source health records |
| Market questioning | Build durable market questions and update hypotheses over time | Market question tracker |
| Privacy lens | Understand how data protection rights, controllers/processors, enforcement, and cross-border transfer themes affect digital lending | Reviewed DPC signals and Data Protection Act follow-up |
| Payment rails lens | Understand how public BoZ payment-system rules, rail changes, and mobile-money/payment-service directives may affect lending disbursement, repayment, failed transactions, complaints, fees, and partner risk | Reviewed BoZ JSON:API/PDF metadata signals and manual-read/OCR follow-up |

## 3. Workflow

```text
Scrapling public-source fetch
  -> SQLite signals
  -> human review queue
  -> personal research notes
  -> weekly personal market notes
  -> capability tracker
```

## 4. Non-Commercial Guardrails

- Do not sell, pitch, or distribute the output as a commercial product while there is occupational risk.
- Do not monitor private competitor information.
- Do not use employer data, internal reports, internal rules, private customer complaints, borrower records, or proprietary workflows.
- Do not run this on employer devices, employer accounts, or employer time.
- Do not submit complaints, forms, or incidents through public portals as part of the crawler.
- Do not bypass login, CAPTCHA, paywalls, rate limits, or access controls.

## 5. Scrapling Role

Scrapling is the crawler layer, not the product.

Use it for:

- simple public HTTP pages through `Fetcher`
- dynamic public pages only when rendering is necessary
- official public PDF and JSON:API feeds where the public site itself exposes documents that normal HTML fetching cannot reach cleanly
- future spider patterns if source count grows

Do not use it for:

- anti-bot bypass as a default strategy
- CAPTCHA solving
- private data access
- high-frequency scanning

## 6. Weekly Research Routine

1. Run one or more public-source fetches.
2. Review new signals.
3. Mark useful signals as `reviewed`.
4. Write at least one research note:
   - What does the source actually say?
   - What market question does it raise?
   - Is this a complaint, policy, fraud, privacy, support, repayment, or competitor signal?
5. Generate personal weekly notes.
6. Update the capability tracker.
7. Update source-health decisions and at least one market question.
8. Record source-specific technical exceptions, such as the DPC SSL fallback or BoZ scanned-PDF/manual-read cases, so they remain deliberate and reviewable.

## 7. Success Criteria For Layer 2

After 4 weeks, the platform is working if:

- at least 5 public sources have been tested
- at least 30 public signals have been reviewed
- at least 12 research notes have been written
- at least 4 weekly personal notes have been generated
- at least 5 market questions have hypotheses or evidence
- source health is used to decide automated vs manual review sources
- the taxonomy feels useful enough to explain market patterns without using private knowledge
- the project remains clearly personal, public-source, and non-commercial

## 8. Future Optional Commercial Review

Commercialization should only be reconsidered later if:

- conflict-of-interest risk is substantially lower
- the product can be framed as broad public-source market research
- no employer/client/private knowledge is necessary
- the deliverable can stand on public sources and transparent methodology alone

Until then, this remains a personal market-learning and capability-building platform.
