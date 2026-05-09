# Fintech Research Platform Sync Policy

This repository is the deployment and research-data store for the Zambia Digital Lending Ops Radar personal research platform.

## Standing Rule

After every milestone-level update to the personal research platform, sync the approved deployment set to:

`https://github.com/leoandersong-ux/Fintech`

Milestone-level updates include:

- Streamlit UI or dashboard changes.
- `lending_ops_radar/` pipeline, intelligence, brief, competitor matrix, or watchlist changes.
- Source/watchlist config changes.
- Reviewed public-source SQLite database updates.
- Generated reviewed briefs, competitor watch outputs, or product matrix exports.
- Deployment entrypoint or dependency changes.

## Required Preflight

Before syncing:

- Run Python compile checks for changed Python files.
- Confirm `streamlit_app.py` remains the Streamlit Cloud entrypoint.
- Confirm `requirements.txt` contains required deploy dependencies.
- Confirm Streamlit Cloud deploy settings use Python 3.12 in Advanced settings; do not rely on `runtime.txt`.
- Scan intended files for secrets, passwords, API keys, private borrower data, logged-in/private-source material, employer-internal data, and unrelated Zambia Opportunity Radar assets.

## Allowed Sync Set

- `streamlit_app.py`
- `requirements.txt`
- `requirements-lending-radar.txt`
- `README.md`
- `.gitignore`
- `SYNC_POLICY.md`
- `lending_ops_radar/`
- `data/lending_ops_radar.sqlite3`
- `data/lending_ops_competitor_product_matrix.csv`
- `data/lending_ops_signals_export.csv`
- selected reviewed/generated files under `data/briefs/`
- fintech/digital-lending research handoff and operating notes

## Never Sync

- Private borrower data.
- Logged-in pages, private WhatsApp/Facebook groups, paywalled/CAPTCHA captures.
- Employer-internal or proprietary lender materials.
- Unrelated Zambia Opportunity Radar commercial assets.
- PDF/DOCX/image render artifacts unrelated to this fintech platform.
- API keys, tokens, passwords, or secrets.

## Commit Convention

Use concise commit messages such as:

- `Update lending ops radar milestone`
- `Refresh lending ops research data`
- `Improve competitor matrix dashboard`

Push to `origin main` after successful checks.
