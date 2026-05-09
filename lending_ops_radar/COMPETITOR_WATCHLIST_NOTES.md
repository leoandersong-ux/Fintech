# Competitor Watchlist Notes

中文：这个 watchlist 是个人市场研究候选清单，不是商业交付清单，也不是对任何机构的合规评价。

English: This watchlist is a personal market-research candidate list, not a commercial deliverable and not a compliance judgement on any institution.

## Current File

Candidate sources live in:

```powershell
.\lending_ops_radar\watchlist.competitors.json
```

Phase-1 public website, FAQ, and loan-product pages are enabled by default. Google Play listing sources remain disabled because public review snippets can include public user names.

To enable a disabled app-listing source, manually change only that source:

```json
"enabled": true
```

Then run:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py --sources .\lending_ops_radar\watchlist.competitors.json init
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\pipeline.py --sources .\lending_ops_radar\watchlist.competitors.json run --source competitor_lupiya_loans
```

## Why These Sources

The first candidate set focuses on public pages that can answer lending-ops questions:

- Product and pricing: loan amount, tenure, APR, interest, service fees, repayment examples.
- Customer journey: sign-up, approval speed, disbursement path, mobile money/bank-wallet dependence.
- Support and complaints: hotline, email, FAQ, support promises, public app support channel.
- Privacy and permissions: privacy policy, data safety, account deletion, app listing data declarations.
- Public sentiment: ratings and visible review themes, only if you manually approve app-listing monitoring.

## Candidate Groups

| Group | Candidate Sources | First Use |
| --- | --- | --- |
| Established fintech / neobank | Lupiya public website, loans page, Google Play listing | Product breadth, loan terms, app positioning, repayment language |
| Multi-product lender | PremierCredit website, borrow page, Google Play listing | Instant-loan positioning, wallet/payment integration, disbursement channels |
| Regional digital lender | FairMoney Zambia loan page, FAQ, Google Play listing | Loan amount, tenure, APR language, eligibility and support |
| App-first instant lenders | PowerKwacha, SuperKwacha, iBatFasta, FLoan | Fees, app permissions, reviews, support, collections/sentiment keywords |

## Enable Order

Recommended order:

1. Run enabled public websites and FAQ pages first.
2. Review the first signals manually.
3. Enable Google Play app listings only after confirming you are comfortable with public review snippets appearing in the research database.
4. Keep all app-listing outputs source-linked and conservative.

## Guardrails

- Use only public pages.
- Do not log in.
- Do not collect private borrower data.
- Do not scrape private social groups, WhatsApp, Facebook login-only content, or paywalled sources.
- Do not treat reviews as verified facts; treat them as public sentiment signals.
- Do not infer legal or regulatory conclusions from competitor wording.
- Avoid adding employer/internal/proprietary sources to this watchlist.

## Review Questions

When reviewing competitor signals, ask:

- Has the competitor changed loan amount, term, APR, service fee, or eligibility wording?
- Are there repeated public complaints about disbursement delay, failed repayment, over-deduction, support silence, privacy, or collections pressure?
- Does the app listing disclose data sharing/collection in a way that changes privacy-risk understanding?
- Is the claimed speed or availability dependent on a payment rail or mobile-money partner?
- Are support channels and dispute routes visible enough for a borrower?

## Product Matrix

After first-pass review, generate the product matrix:

```powershell
& '.\.venv-lending\Scripts\python.exe' .\lending_ops_radar\competitor_matrix.py
```

Outputs:

- `data/lending_ops_competitor_product_matrix.csv`
- `data/briefs/zambia_digital_lending_competitor_product_matrix_<date>.md`

The matrix should compare different product layers separately: short-term microloans, salary advances, larger personal loans, SME finance, agriculture finance, payment/wallet capability, and privacy/account-control signals.

Current matrix fields include:

- Product layer: keeps K500 instant loans, K250,000 personal loans, K1,000,000 SME loans, payment capability, and privacy/account-control signals in separate lanes.
- Limit tier: turns public limits into comparable ZMW bands where possible.
- Speed tier: separates instant/minute-level wording, 24-hour wording, conditional wording, and missing speed evidence.
- Payment maturity: flags whether public evidence shows mobile-money/bank rails, account/creditor payout, operating cash-flow repayment, or no captured rail.
- Support/privacy maturity: captures visible support, hotline, privacy, or account-deletion routes.
- Completeness and gap flags: show research-field coverage, not product quality. Low completeness means the next step is source review, not that the competitor product is weak.
