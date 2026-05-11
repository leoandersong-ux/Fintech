# v0.4 Review Workflow Layer

Date: 2026-05-11

## Goal

v0.4 turns the platform from "which signals matter" into "how to process the important signals quickly and consistently."

v0.3 introduced signal quality scoring. v0.4 uses those scores inside a review cockpit so the research workflow becomes easier to operate week after week.

## What Changed

- Page title now shows the current version: `v0.4`.
- Added `lending_ops_radar/version.py` for version metadata.
- Added a Streamlit `复核驾驶舱 Cockpit` tab.
- The cockpit ranks signals by brief-candidate score and manual-review need.
- Added one-click review decisions:
  - keep as reviewed,
  - add to brief candidate,
  - needs source review,
  - keep as background,
  - reject.
- Added classification-specific action templates for fees, repayment, disbursement, privacy, complaint, collections, fraud, regulatory, competitor, and news signals.
- Added a brief-candidate pool and market-question view inside the cockpit.
- Weekly notes now include the platform version label.

## Why It Matters

The platform should not merely collect public-source rows. It should help turn reviewed signals into durable research assets:

- clearer next actions,
- fewer repeated manual notes,
- shorter and higher-quality weekly notes,
- better tracking of open market questions,
- safer source-linked interpretation.

## Deployment Note

After this commit is pushed to `leoandersong-ux/Fintech`, Streamlit Cloud should update automatically if the app is connected to the repository's `main` branch. If the app is still in a failed state, use **Reboot app** or redeploy with Python 3.12 selected in Advanced settings.
