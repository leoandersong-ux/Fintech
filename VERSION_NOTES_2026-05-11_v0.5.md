# v0.5 Business Interpretation Layer

Date: 2026-05-11

## Goal

v0.5 moves the platform from bilingual information display toward a cleaner personal research cockpit: default Chinese reading, one-click English mode, and stronger business interpretation for micro-lending operations.

## What Changed

- Page title now shows `v0.5`.
- Added a prominent top language switcher:
  - default view: Chinese only,
  - one-click switch: English-only interface and generated note preview.
- Added the `V0.5 五条迭代线行动板` inside the intelligence tab.
- Added operating-lane interpretation for:
  - regulatory and payment rails,
  - competitor product matrix,
  - complaints, support, and reputation,
  - collections and customer communication,
  - weekly brief and deployment data layer.
- Weekly note generation now supports `--language zh|en`.
- Competitor matrix Markdown generation now supports `--language zh|en`.
- The impact matrix remains card-based to avoid narrow, unreadable table layout.

## Why It Matters

The platform should answer "what does this public signal mean for micro-lending operations?" before it asks for more crawling. This version makes the research loop easier to read and turns reviewed signals into next actions around product, payments, complaints, privacy, collections, and operating risk.

## Deployment Note

After this commit is pushed to `leoandersong-ux/Fintech`, Streamlit Cloud should update automatically if the app is connected to the repository's `main` branch. If the deployed app still shows the previous version, reboot the app from Streamlit Cloud.
