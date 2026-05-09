# Zambia Digital Lending Ops Radar - Build Plan

Version: v0.2  
Implementation target: personal public-source research platform plus capability-building workflow

## 1. Product Shape

The current build is not a SaaS platform or commercial intelligence product. It is a **personal public-source research workflow**:

```text
Public sources
  -> fetch and normalize
  -> classify by lending-risk theme
  -> store in SQLite
  -> review queue
  -> personal research notes
  -> weekly personal market notes
  -> capability tracker
```

The goal is to build market understanding and technical capability without crossing professional or conflict-of-interest boundaries.

## 2. Deliverables

Research files:

- `zambia_digital_lending_ops_brief_pilot_001.md`
- `zambia_digital_lending_ops_sales_materials.md`
- `zambia_digital_lending_ops_build_plan.md`
- `zambia_digital_lending_personal_research_platform.md`

Commercial files are retained as historical drafts only. Current operating mode is personal research.

MVP files:

- `requirements-lending-radar.txt`
- `lending_ops_radar/README.md`
- `lending_ops_radar/sources.json`
- `lending_ops_radar/pipeline.py`
- `lending_ops_radar/brief_generator.py`
- `lending_ops_radar/app.py`

Crawler integration:

- Use `D4Vinci/Scrapling` as the open-source crawler, matching the direction used in `Zambia Opportunity Radar CN`.
- Keep Scrapling as the collection layer only; the current product surface is a private research workspace.
- Default to low-frequency public HTTP fetching, and only use browser/dynamic fetching when a public page genuinely requires rendering.
- Do not use anti-bot, CAPTCHA, login, paywall, or private-source capabilities in the MVP.

## 3. Data Model

SQLite database:

- `sources`: configured public sources.
- `signals`: normalized extracted items.
- `reviews`: review status, notes, priority, and action recommendation.
- `page_snapshots`: source page text hash for change detection.
- `brief_items`: reviewed items selected for weekly personal notes.
- `source_runs`: source run status, signal counts, and errors.
- `research_notes`: personal observations, questions, and interpretations.
- `learning_goals`: capability-building goals and evidence.
- `source_quality`: recurring source reliability, last status, and signal counts.
- `market_questions`: durable market questions, hypotheses, and evidence.

Classification labels:

- `complaint`
- `fees`
- `disbursement`
- `repayment`
- `collections`
- `privacy`
- `fraud`
- `regulatory`
- `competitor_change`
- `news_signal`

## 4. Operating Rules

- Use public webpages, official pages, public app listings, public reviews, public news, and manually approved public watchlists only.
- Do not use borrower records, private messages, client databases, proprietary rules, non-public reports, or restricted pages.
- Do not bypass login, paywall, CAPTCHA, or access controls.
- Every customer-facing claim must include a source link or be labeled as a recommendation.
- High-risk language must be conservative: "potential signal", "requires verification", "management should review".
- Do not sell, pitch, or distribute the outputs while occupational or conflict-of-interest risk remains.

## 5. CLI Workflow

Initialize or update the database:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py init
```

Run all enabled sources:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source all
```

Run one configured public source:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py run --source ccpc_public_notices
```

Install Scrapling browser dependencies only if a public source needs rendering:

```powershell
& '.\.venv-lending\Scripts\scrapling.exe' install
```

Seed reviewed sample records for offline template testing:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-sample
```

Seed capability-building goals:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-learning
```

Seed market questions:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py seed-questions
```

Add a personal research note:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py add-note --title "Example note" --note "Write a source-linked market observation." --question "What does this signal imply for Zambia lending ops?"
```

Update a market question:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py answer-question --question-key source_reliability --hypothesis "Write the current working answer." --evidence "Record source-linked evidence or source-run observations."
```

Show platform stats:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py stats
```

Show source health:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py source-health
```

Generate current-week personal notes:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\brief_generator.py --week current
```

Run the dashboard after installing Streamlit:

```powershell
& '.\.venv-lending\Scripts\streamlit.exe' run .\lending_ops_radar\app.py --server.port 8501
```

## 6. First Validation Metrics

Technical:

- At least 1 Scrapling source fetch inserts rows into SQLite.
- Dedupe prevents duplicate `source_id + item_url + title` rows.
- Dashboard loads source, review-queue, research-notes, and capability-tracker tabs.
- Personal notes generator writes a markdown draft from reviewed/sample rows.

Capability-building:

- 5 public sources tested.
- 30 public signals reviewed.
- 12 personal research notes written.
- 4 weekly personal notes generated.
- The taxonomy helps explain market patterns without using private knowledge.

## 7. Next Extensions

Only after the personal research routine is stable:

- Add personally approved public Google Play app watchlists.
- Add scheduled runs with APScheduler.
- Add LLM summarization behind an API key.
- Add local reminders or private email-to-self delivery.
- Add CSV export for client review.
- Add deeper personal market maps and source-quality scoring.
