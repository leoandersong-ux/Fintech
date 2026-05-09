# Digital Lending Personal Research - Weekly Routine

Version: v0.1  
Purpose: turn public-source collection into repeatable market learning

## 1. Weekly Objective

Each week should produce one private research note that answers:

- What public signals changed?
- Which sources were reliable or noisy?
- Which lending-ops taxonomy buckets appeared?
- What market questions became clearer?
- What should I investigate next week?

## 2. Run Sequence

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py init
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-learning
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-questions
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source ccpc_public_notices
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_regulatory_documents_api
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py source-health
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py stats
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py reclassify
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py list-signals --status new --limit 10
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\brief_generator.py --week current
```

Then open the dashboard:

```powershell
& '.\.venv-lending\Scripts\streamlit.exe' run .\lending_ops_radar\app.py --server.port 8501
```

## 3. Manual Review Steps

1. Open `Review Queue`.
2. Mark 5-10 useful signals as `reviewed`.
3. For each useful signal, write one note:
   - source fact
   - personal interpretation
   - market question
   - confidence level
4. Open `Market Questions`.
5. Update at least one hypothesis or evidence field.
6. Open `Capability Tracker`.
7. Add evidence for the learning goal advanced this week.

If Streamlit is not open, use:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py review-signal --signal-id 1 --status reviewed --priority 2 --notes "Why this signal matters." --action "Next research action."
```

## 4. Weekly Personal Note Structure

Use the generated markdown in `data/briefs/` and refine it manually:

- Executive summary
- Regulatory watch
- Competitor / public-page changes
- App review and complaint themes
- Reputation and news signals
- Operating pattern notes
- Research notes
- Market questions
- Source health
- Top risks to watch
- Next learning actions

## 5. Source Health Decision Rules

| Pattern | Decision |
| --- | --- |
| Repeated success, useful signals | Keep automated weekly run |
| Repeated success, noisy signals | Tighten keywords/selectors |
| Repeated failure, important source | Move to manual review list |
| Blocks, login, CAPTCHA, or access warning | Stop automation and use manual review only |
| Public official page has local issuer-chain SSL failure | Use source-scoped `verify_ssl: false` only after documenting the reason |
| No useful signals after 4 weeks | Archive or lower frequency |

Current source notes:

- `ccpc_public_notices`: useful for broad consumer-protection and disclosure principles, but requires noise filtering for goods seizures, hashtags, footer text, and duplicate homepage fragments.
- `data_protection_commission_home`: useful for privacy/data-protection research, but currently needs source-scoped SSL fallback in this environment. Review manually if the fallback behavior changes.
- `boz_regulatory_documents_api`: strongest source for the payment-rails capability line. It uses BoZ's public JSON:API regulatory document metadata, currently narrowed to 2018+ and filtered away from recurring returns/fee-administration noise.
- BoZ PDF directive sources: several official PDFs are scanned/image-like and may produce metadata-only records. Keep those as manual-read/OCR anchors rather than pretending the pipeline extracted legal substance.

## 6. Capability Evidence

At the end of each week, capture one proof item:

- a source-health observation
- an improved classification rule
- a useful market question
- a reviewed signal that changed your understanding
- a note about what should remain manual
- a source-specific technical exception and why it is acceptable for public-source research
- a payment-rails observation that links BoZ rules/circulars to lending ops only at the level of public-source research

This keeps the platform focused on learning, not just accumulating scraped rows.
