# Scrapling Integration - Zambia Digital Lending Ops Radar

Version: v0.1  
Repository: https://github.com/D4Vinci/Scrapling  
Purpose: public-source collection layer for a personal lending market research platform

## 1. Decision

Use **Scrapling** as the primary open-source crawler for the Zambia digital lending personal research platform, matching the technical direction already used for `Zambia Opportunity Radar CN`.

For this fintech research project, Scrapling is a collection tool, not the product. The current value is capability-building:

- lending-specific source selection
- complaint and risk classification
- weekly human-reviewed personal notes
- better understanding of support, collections, competitor, fraud, privacy, and regulatory public signals

## 2. Why Scrapling Fits

Scrapling is useful here because it supports:

- HTTP fetching for simple public pages.
- Browser-style dynamic fetching for public pages that require rendering.
- CSS/XPath-style parsing that fits source-config driven extraction.
- A path from single-source fetches to larger spiders later.
- Development caching and crawler patterns that can reduce repeated source hits.

For the current MVP, use the simplest `http` fetcher first. Dynamic/browser fetching should be added only when a public source cannot be collected reliably with HTTP.

For BoZ, the current website exposes important regulatory documents through a public Drupal JSON:API feed and confirmed `/sites/default/files/...` PDF URLs. The lending radar therefore uses Scrapling for normal public pages, plus conservative standard-library fetchers for `jsonapi` metadata and `pdf` manual-read anchors.

## 3. Compliance Boundary

Use Scrapling only for:

- official public regulator pages
- public consumer protection pages
- public data protection pages
- public app listings
- public competitor pages approved by a client watchlist
- public news or public notices

Do not use Scrapling for:

- login pages
- private dashboards
- borrower data
- private Facebook or WhatsApp groups
- CAPTCHA bypass
- paywall bypass
- scraping employer/client proprietary systems
- collecting personally identifying incident details
- high-frequency scanning
- commercial delivery while conflict-of-interest risk remains

If a site blocks, challenges, or asks for login, stop automated collection and review manually.

## 4. Current Local Implementation

Files:

- `requirements-lending-radar.txt`: includes `scrapling[fetchers]==0.4.7`.
- `requirements-lending-radar.txt`: also includes `pypdf` for public PDF text extraction when the PDF contains extractable text.
- `lending_ops_radar/sources.json`: fintech-specific public sources.
- `lending_ops_radar/pipeline.py`: imports Scrapling fetchers and stores normalized signals in SQLite.
- `lending_ops_radar/README.md`: operator setup and run instructions.

Pipeline behavior:

```text
sources.json
  -> Scrapling Fetcher / DynamicFetcher / StealthyFetcher
  -> public JSON:API/PDF fallback fetchers where needed
  -> conservative HTML fallback for simple HTTP pages
  -> keyword filtering
  -> lending-risk classification
  -> SQLite signals and reviews
  -> research notes and brief_generator.py
```

## 5. Operating Defaults

- Run official sources weekly during the pilot.
- Run app/competitor watchlists only when they are manually approved public sources for personal research.
- Keep selectors broad in v0 so the operator can review signals manually.
- Do not distribute unreviewed scraped items externally.
- Do not use Scrapling stealth features as a sales claim.

## 6. Upgrade Path

Phase 1:

- Keep `http` sources for CCPC, DPC, and simple public pages.
- Use `boz_regulatory_documents_api` for BoZ regulatory/payment-rails metadata because legacy BoZ HTML endpoints currently return a SPA loader/404 shell.
- Keep BoZ PDF directive sources as manual-read/OCR anchors when `pypdf` reports no extractable text.
- Use reviewed records to generate weekly markdown briefs.

Phase 2:

- Add personally approved Google Play and competitor URL watchlists.
- Add page hash change detection for FAQ, pricing, eligibility, and disclosure pages.
- Add CSV export for manual review.

Phase 3:

- Add dynamic fetching only for public pages that require rendering.
- Add scheduled runs.
- Add LLM summarization behind explicit API-key configuration.
- Consider Scrapling spiders if source count grows beyond simple scheduled source fetches.
