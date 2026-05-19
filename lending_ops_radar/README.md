# Digital Lending Personal Research Radar

This folder contains a private research platform for understanding Zambia digital lending market signals.

It follows the same open-source crawler direction used in `Zambia Opportunity Radar CN`: Scrapling is the primary public-source collection layer, SQLite stores normalized signals, and Streamlit provides the personal review dashboard.

The current target is **capability-building**, not commercialization.

## Reading Mode

The Streamlit dashboard now defaults to a cleaner Chinese reading mode:

- Chinese is the default for personal reading.
- A prominent top button switches the app to English-only mode for future reuse.
- Tables keep original source text intact, while UI labels, section titles, guardrails, weekly notes, and matrix previews follow the selected language.

## What It Does

- Fetches configured public sources with Scrapling.
- Falls back to a conservative standard-library HTTP parser for simple public pages if Scrapling fetchers are unavailable.
- Reads official public PDF documents when `fetcher` is `pdf`; scanned PDFs may become metadata-only signals until manually read or OCRed.
- Reads public Drupal JSON:API document feeds when `fetcher` is `jsonapi`, currently used for the BoZ regulatory documents feed.
- Normalizes source items into `signals`.
- Classifies each signal into lending-ops categories such as `complaint`, `fraud`, `privacy`, `regulatory`, and `competitor_change`.
- Adds rule-based business interpretation for reviewed signals: impact domain, lending impact, affected process, recommended action, and follow-up questions.
- Scores reviewed signals for source credibility, lending relevance, manual review need, and weekly-brief priority.
- Filters obvious boilerplate such as copyright footers before new inserts.
- Stores data in SQLite for review.
- Records source runs, personal research notes, and learning goals.
- Generates weekly personal market notes from reviewed items only.

## Intelligence Reading Layer

The main reading entry is now the Streamlit tab `研究首页 Brief`.

It puts the existing intelligence layers into a clearer reading order:

- top public signals to read first,
- micro-lending operating impact lines,
- this-week research actions,
- coverage gaps that still need source work.

The detailed `业务影响 Ops Impact` tab still converts reviewed public signals into:

- `业务判断 | Business interpretation`
- `小微贷款业务影响矩阵 | Micro-lending impact matrix`
- `情报覆盖缺口 | Intelligence coverage gaps`
- `建议动作 | Recommended actions`
- `后续问题 | Follow-up questions`

This layer is intentionally rule-based first. It helps you learn the market and lending-ops risk surface without pretending to be an autonomous compliance engine.

Coverage roadmap: [INTELLIGENCE_COVERAGE_PLAN.md](./INTELLIGENCE_COVERAGE_PLAN.md)

## Signal Quality Layer

`quality.py` is the v0.3 judgment layer. It helps decide what deserves attention first:

- `source_credibility_score`: whether the signal comes from an official, competitor, app-listing, or weaker public source.
- `lending_relevance_score`: how directly the signal affects lending operations.
- `manual_review_need_score`: whether it should be checked manually before entering weekly notes.
- `brief_candidate_score`: whether it belongs in the weekly research note.

Generate a quality snapshot:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\quality.py
```

## Review Workflow Layer

`v0.4` adds the Streamlit tab `复核驾驶舱 Cockpit`.

Use it to:

- See the highest-priority signals first.
- Apply classification-specific review templates.
- Mark signals as reviewed, brief candidates, source-review items, background, or rejected.
- Keep weekly notes focused on high-quality, source-linked signals.

## Business Interpretation Layer

`v0.5` adds a five-lane action board and cleaner language modes.

Use the intelligence tab to read:

- regulatory and payment-rail impact,
- competitor product-matrix direction,
- complaint, support, and reputation themes,
- collections and customer-communication risk,
- weekly-brief and deployment data-layer next actions.

Generated notes and competitor matrices now support `--language zh|en`.

## Market Voice and Trend Layer

`v0.6` adds the first market-change layer:

- `trends.py` classifies signals into market-voice themes and compares the latest signal window with the previous one.
- `snapshot_exporter.py` writes a cloud-friendly JSON read model to `data/snapshots/lending_ops_dashboard_snapshot.json`.
- Streamlit now has `市场声音`, `趋势变化`, and `本周行动` tabs.
- Google Play/public app-listing sources remain disabled candidates until public-review boundaries are explicitly approved.

Generate the snapshot:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\snapshot_exporter.py
```

View trend rows from CLI:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\trends.py --mode trends --language zh
```

## Research Brief Readability Layer

`v0.7` improves the platform as a personal research workspace:

- Page title and snapshot now show `v0.7`.
- Top navigation is reduced to six research areas instead of many scattered tabs.
- `reading_brief.py` turns snapshot data into a compact brief model for Streamlit.
- The first tab reads like a research brief: conclusion, impact, action, and gap.
- The snapshot JSON includes `reading_brief_zh` and `reading_brief_en` for cloud deployment.
- A small unittest suite guards the brief model and obvious garbled text handling.

## Guardrails

- Public pages only.
- Low request volume.
- No login, paywall, CAPTCHA, private groups, or restricted content.
- No borrower data, customer lists, private complaints, employer records, or proprietary lender data.
- No automatic legal or regulatory conclusions.
- No commercial distribution while conflict-of-interest risk remains.
- Every personal conclusion should keep a source link.

## Setup

From the project root:

```powershell
& 'C:\Users\leoan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv-lending
& '.\.venv-lending\Scripts\python.exe' -m pip install -r requirements-lending-radar.txt
```

If browser rendering is needed later, install Scrapling browser dependencies:

```powershell
& '.\.venv-lending\Scripts\scrapling.exe' install
```

Use that browser install only for public pages that genuinely need rendering.

## Commands

Initialize the database and source list:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py init
```

Run all configured sources:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source all
```

Run one source:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source ccpc_public_notices
```

Run the BoZ payment-rails capability line:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_regulatory_documents_api
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_e_money_directives_2023
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_customer_complaints_directives
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_mobile_payments_directive_2020
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source boz_money_transfer_services_directives_2021
```

Run a manually approved watchlist file:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py --sources .\lending_ops_radar\watchlist.example.json run --source all
```

The example watchlist is disabled by default. Copy it to a private local file, replace URLs with public pages you approve, and set `enabled` to `true`.

Review the competitor watchlist:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py --sources .\lending_ops_radar\watchlist.competitors.json init
```

Run all enabled phase-1 competitor website/FAQ sources:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py --sources .\lending_ops_radar\watchlist.competitors.json run --source all
```

Pre-triage new competitor signals without marking them reviewed:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py competitor-triage --status new --limit 20
```

Apply suggested priority and next-action text to the review queue:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py competitor-triage --status new --apply
```

Generate a Markdown competitor-watch snapshot:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\competitor_snapshot.py --status new
```

Generate the source-linked competitor product matrix:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\competitor_matrix.py
```

The matrix now includes derived comparison fields for product layer, limit tier, speed tier, payment maturity, support/privacy maturity, research completeness, evidence gaps, and matrix priority.

The competitor watchlist enables phase-1 public website/FAQ/product pages by default. Google Play listing sources remain disabled. See [COMPETITOR_WATCHLIST_NOTES.md](./COMPETITOR_WATCHLIST_NOTES.md) before enabling app-listing sources, because public review snippets may include public user names.

Seed reviewed sample records for offline testing:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-sample
```

Seed capability-building goals:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-learning
```

Seed market research questions:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-questions
```

Add a personal research note:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py add-note --title "DFS incident categories" --note "Mobile payment fraud and incomplete transactions are useful risk-taxonomy anchors." --question "Which public complaint themes matter most for lending ops?"
```

List signals without opening Streamlit:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py list-signals --status new --limit 10
```

Review one signal without opening Streamlit:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py review-signal --signal-id 1 --status reviewed --priority 2 --notes "Useful source-linked observation." --action "Track this theme next week."
```

Update a market question:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py answer-question --question-key source_reliability --hypothesis "CCPC is stable enough for weekly Scrapling runs; ZICTA DFS may need manual fallback if it times out." --evidence "Source runs and errors recorded in source_quality."
```

Show platform stats:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py stats
```

Show business interpretation in the CLI:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py intelligence --limit 8 --show-gaps
```

Recalculate classifications after taxonomy changes:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py reclassify
```

Show Scrapling source health:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py source-health
```

Export the signal review table:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py export-csv
```

Generate current-week personal notes:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\brief_generator.py --week current
```

Run the dashboard:

```powershell
& '.\.venv-lending\Scripts\streamlit.exe' run .\lending_ops_radar\app.py --server.port 8501
```

## Source Config

`sources.json` uses this shape:

```json
{
  "source_id": "ccpc_public_notices",
  "name": "Competition and Consumer Protection Commission Notices",
  "source_type": "consumer_protection",
  "url": "https://www.ccpc.org.zm/",
  "fetcher": "http",
  "frequency": "weekly",
  "category": "regulatory",
  "keywords": ["consumer", "rights", "misleading"],
  "exclude_keywords": ["copyright", "all rights reserved"],
  "exclude_exact_titles": [],
  "min_year": 2018,
  "max_json_pages": 10,
  "max_pdf_pages": 40,
  "verify_ssl": true,
  "compliance_notes": "Public notices only."
}
```

Fetcher values:

- `http`: Scrapling `Fetcher`, suitable for normal public pages.
- `dynamic`: Scrapling `DynamicFetcher`, only when a public source needs browser rendering.
- `pdf`: standard-library public PDF download plus `pypdf` text extraction. If a PDF is scanned or image-only, the pipeline keeps a metadata-only signal for manual reading/OCR.
- `jsonapi`: public Drupal JSON:API document metadata feed. The BoZ regulatory documents source uses this because the current BoZ website routes old HTML/PDF root URLs through its SPA shell.
- `stealthy`: reserved for legitimate public pages with high rendering friction; not a default mode.

Use `exclude_keywords` to remove recurring source noise such as footer text, hashtag-only snippets, unrelated goods seizures, or other patterns discovered during manual review.
Use `exclude_exact_titles` for generic navigation items whose title is only useful as page chrome, not as a research signal.
Use `min_year` to keep long official archives focused on current market learning instead of old historical noise.

Use `verify_ssl: false` only for a manually approved public source that fails local issuer-chain validation, and record the reason in `compliance_notes`. Do not use it for login pages, private systems, payment pages, or anything involving personal data.

Current BoZ note: the legacy `regulatory-framework.htm` endpoint is disabled because the public crawler currently receives a loader/404 shell. Use `boz_regulatory_documents_api` for monitoring and the confirmed `/sites/default/files/...` PDF sources for manual-read anchors.

## Output

Runtime output is intentionally ignored by git:

- `data/lending_ops_radar.sqlite3`
- `data/briefs/`
- `data/lending_ops_signals_export.csv`

Keep public-source research methodology in project-root markdown files, and keep working data in `data/`.
