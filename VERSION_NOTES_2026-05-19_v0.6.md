# v0.6 Market Voice and Trend Layer

Date: 2026-05-19

## Goal

v0.6 starts turning the platform from a source-linked research cockpit into a market radar with visible change over time. The focus is not more raw crawling; it is market voice, trend direction, weekly actions, and a cloud-friendly snapshot layer.

## What Changed

- Page title now shows `v0.6`.
- Added `lending_ops_radar/trends.py` for:
  - market voice theme classification,
  - latest-window vs previous-window trend rows,
  - source health trend rows,
  - weekly action recommendations.
- Added `lending_ops_radar/snapshot_exporter.py`.
- Added checked-in dashboard snapshot output:
  - `data/snapshots/lending_ops_dashboard_snapshot.json`
- Added Streamlit tabs:
  - `市场声音 / Market Voice`,
  - `趋势变化 / Trends`,
  - `本周行动 / Actions`.
- Deployment health now shows whether the snapshot is available.
- Google Play and public app-listing sources remain candidate sources and disabled by default.

## Why It Matters

v0.5 answered "what does this signal mean?" v0.6 begins answering "what is changing, and what should I review this week?"

The new layer keeps the platform useful even when the cloud app should not rely on live crawling or mutable local SQLite behavior. The snapshot gives Streamlit Cloud a stable read model while SQLite remains the local research store.

## Guardrail

Public app listings and public comments can contain public user names or sensitive context. They should remain disabled until the review boundary is explicit: public pages only, no login, no private groups, no borrower records, no identity-focused collection.
