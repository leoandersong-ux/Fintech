# v0.3 Intelligence Quality Layer

Date: 2026-05-11

## What Changed

This node moves the platform from a public-source collection dashboard toward a judgment-support research platform.

## Five Iteration Lines

1. Deploy stability
   - Added a Streamlit `健康 Health` tab for deploy entrypoint, database, reviewed signals, latest notes, and source-run status.
   - Kept Streamlit Cloud dependency surface minimal to avoid pyarrow rebuild issues.

2. Information quality scoring
   - Added `lending_ops_radar/quality.py`.
   - Each signal can now receive source credibility, lending relevance, manual review need, and brief candidate scores.
   - Added priority-read and brief-candidate tiers.

3. Business impact interpretation
   - Added priority reads to the `业务解读 Intelligence` tab.
   - Weekly notes now include a signal quality and reading-priority section before the impact matrix.

4. Competitor product matrix 2.0
   - Added competitor positioning and operating-risk focus fields.
   - Matrix now separates app-first microcash, salary-linked credit, SME finance, agriculture-cycle finance, payment/wallet capability, and privacy/account-control capability.

5. Weekly research workflow
   - Added `WEEKLY_RESEARCH_WORKFLOW.md`.
   - Friday milestone sync remains governed by `SYNC_POLICY.md`.

## Guardrails

- Public sources only.
- No borrower data.
- No private social groups, logged-in pages, or paywalled/CAPTCHA captures.
- No employer-internal or proprietary lender material.
- Not legal advice, not regulatory certification, not commercial delivery.

## Deployment

Streamlit Cloud:

- Repository: `leoandersong-ux/Fintech`
- Branch: `main`
- Main file: `streamlit_app.py`
- Python version: choose Python 3.12 in Streamlit Cloud Advanced settings when creating the app.
