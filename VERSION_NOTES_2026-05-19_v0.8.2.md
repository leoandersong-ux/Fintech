# v0.8.2 All-Target Competitor Positioning Matrix

v0.8.2 fixes the readability gap in the competitor matrix.

## Why This Node Exists

v0.8.1 made all 19 competitors and ecosystem targets visible, but many rows still read as "candidate watch / not yet in product matrix." That was evidence-safe, but not useful enough for horizontal market reading.

## What Changed

- Added `build_competitor_comparison_rows()` for an all-target comparison matrix.
- Added `build_positioning_group_rows()` to compress 19 targets into readable positioning groups.
- The matrix page now starts with:
  - positioning map,
  - all-target product matrix,
  - comparison table across positioning, product lane, segment, channel, ops impact, evidence mode, and policy pressure.
- Candidate targets now have provisional positioning, product lane, target segment, channel model, and micro-lending ops impact.
- Reviewed product facts remain clearly separated from provisional source-candidate reads.
- Competitor watch cards now show positioning and product lane, not only watch status.

## Practical Effect

The platform can now answer:

- Which players are app-first microcash lenders?
- Which players are salary/payroll or traditional microfinance benchmarks?
- Which players are payment rails rather than direct lending competitors?
- Which candidate targets still need source review before entering the reviewed product matrix?
- What each competitor type may change for payout, repayment, pricing disclosure, support, complaints, privacy, and collections operations?

## Verification

- `python -m unittest tests.test_reading_brief tests.test_competitor_intelligence`
- `python -m py_compile streamlit_app.py lending_ops_radar/app.py lending_ops_radar/competitor_intelligence.py lending_ops_radar/snapshot_exporter.py lending_ops_radar/reading_brief.py`
- `python lending_ops_radar/snapshot_exporter.py`
