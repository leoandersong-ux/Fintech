# v0.7 Research Brief Readability Layer

v0.7 turns the Streamlit workspace from a set of useful but scattered analysis tabs into a clearer personal research brief.

## Why This Node Exists

The platform already had source monitoring, review workflow, business interpretation, market voice, trends, weekly actions, and competitor matrices. The weak point was readability: the user had to jump between too many tabs and mentally stitch together what mattered for micro-lending operations.

## What Changed

- Page title and snapshot metadata now show `v0.7`.
- Added `lending_ops_radar/reading_brief.py`, a small read model that compresses snapshot data into:
  - top signals to read first,
  - micro-lending impact lines,
  - this-week research actions,
  - coverage gaps.
- Added a new first Streamlit tab: `研究首页 / Brief`.
- Reduced the top-level navigation to six areas:
  - `研究首页 / Brief`
  - `业务影响 / Ops Impact`
  - `市场竞品 / Market & Competitors`
  - `复核工作台 / Review`
  - `来源健康 / Sources & Health`
  - `输出与边界 / Outputs & Guardrails`
- Moved detailed pages into nested tabs so the app reads from summary to evidence instead of showing every module at the same level.
- Added `reading_brief_zh` and `reading_brief_en` to the cloud snapshot JSON.
- Added `tests/test_reading_brief.py` for brief-model behavior and obvious garbled-text handling.

## Practical Effect

The first screen now answers:

1. What should I read first?
2. Which micro-lending operating line does it affect?
3. What should I do this week?
4. What source gap should I close next?

This keeps the project aligned with the personal capability-building goal, while still preserving detailed review, source, competitor, and weekly-note workflows below the main brief.

## Verification

- `python -m unittest tests.test_reading_brief`
- `python -m py_compile streamlit_app.py lending_ops_radar/app.py lending_ops_radar/reading_brief.py lending_ops_radar/snapshot_exporter.py`
- `python lending_ops_radar/snapshot_exporter.py`
