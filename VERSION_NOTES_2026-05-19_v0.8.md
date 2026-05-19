# v0.8 Competitor Scope and Policy Impact Layer

v0.8 expands the platform from a source-linked product matrix into a broader competitor-intelligence workspace.

## Why This Node Exists

The previous matrix was useful but too narrow. It over-weighted a few visible app or website sources and did not clearly show how public policy signals affect competitor products, operations, disclosures, payment rails, support, privacy, or public voice.

## What Changed

- Page title and snapshot metadata now show `v0.8`.
- Added `lending_ops_radar/competitor_intelligence.py`.
- Added a broader competitor universe with 19 candidates across:
  - core digital lending apps,
  - adjacent microfinance / payroll lenders,
  - payment rails and ecosystem partners.
- Added a policy-impact read model that maps public regulatory / consumer-protection themes to competitor watch fields:
  - fees and APR disclosure,
  - privacy and app permissions,
  - complaints and dispute handling,
  - payment rails and failed-transaction handling,
  - company, financial, and social-impact signals.
- Added company/product/financial/social/voice event candidates.
- Added `lending_ops_radar/watchlist.competitors.expanded.json` as a manually reviewed source candidate list.
- Reshaped the Streamlit `市场竞品` section so the first view is now a competitor map and policy-impact dashboard, not a flat table.
- Added `tests/test_competitor_intelligence.py`.

## Practical Effect

The platform can now answer better research questions:

1. Which market players should be watched beyond FLoan, Lupiya, PowerKwacha, and PremierCredit?
2. Which players are direct app-first lenders, adjacent MFIs/payroll lenders, or payment/ecosystem actors?
3. Which policy themes pressure which competitor fields?
4. Which company, product, financial, social, and public-voice sources should be checked next?

## Guardrails

- Expanded sources are candidates first, not automatically trusted.
- Public app listings remain disabled by default unless manually approved.
- Public-review monitoring should aggregate themes only and avoid storing usernames, identity data, or sensitive raw narratives.
- LinkedIn and similar company-social pages are manual-review candidates; do not scrape logged-in views.
- This remains a personal public-source research platform, not a legal or compliance conclusion.

## Verification

- `python -m unittest tests.test_reading_brief tests.test_competitor_intelligence`
- `python -m py_compile streamlit_app.py lending_ops_radar/app.py lending_ops_radar/competitor_intelligence.py lending_ops_radar/snapshot_exporter.py lending_ops_radar/reading_brief.py`
- `python lending_ops_radar/snapshot_exporter.py`
