# v0.8.1 Competitor Matrix and Watch Visual Layer

v0.8.1 closes the gap between the expanded competitor map and the matrix / watch pages.

## Why This Node Exists

v0.8 expanded the competitor universe, but the older product matrix still only showed competitors with reviewed product-field evidence. That separation was intentional, but visually it made the matrix and watch pages look incomplete.

## What Changed

- Added `build_competitor_overview_rows()` and `build_watch_panel_rows()`.
- The snapshot now includes:
  - `competitor_overview_rows`
  - `competitor_watch_panel_rows`
- The `竞品矩阵 / Competitor Matrix` page now starts with a concise overview matrix that covers all 19 watch targets.
- The original product matrix remains below the overview and still only includes reviewed product-field evidence.
- The `竞品观察 / Competitor Watch` page now shows a compact card for every competitor / ecosystem candidate.
- Each card shows:
  - current matrix status,
  - evidence level,
  - watch priority,
  - watch fields,
  - policy-pressure count,
  - product-matrix row count,
  - source candidate link.

## Practical Effect

Every target is now visible in both the matrix and observation workflow, while the platform still keeps candidate sources separate from reviewed product facts. This reduces the feeling of missing competitors without flooding the product matrix with weak evidence.

## Verification

- `python -m unittest tests.test_reading_brief tests.test_competitor_intelligence`
- `python -m py_compile streamlit_app.py lending_ops_radar/app.py lending_ops_radar/competitor_intelligence.py lending_ops_radar/snapshot_exporter.py lending_ops_radar/reading_brief.py`
- `python lending_ops_radar/snapshot_exporter.py`
