# Post-launch monitoring and recovery diagnosis

## Monitoring cadence

- Immediate production smoke checks after cutover.
- Frequent technical checks during the early stabilisation period.
- Regular performance reviews while the new URLs are being processed.
- Long-term redirect retention and maintenance.

Adjust the frequency to the inventory size, the risk, the data volume and the failures observed. This is an
operating framework, not a universal recovery timetable. Use `assets/templates/monitoring-plan.md`.

## What to track

Redirect failures, errors, intended indexing, canonical changes, clicks, impressions, CTR, position, visits,
orders, revenue and conversion rate, segmented where feasible by locale, page type, device, country and query
group.

**Compare mapped page groups, not old URLs.** Inspect the old URL alone and a successful move looks like a total
loss. Aggregate each old URL with the new URL it maps to, and compare the group before and after
(`scripts/migration_checks.py performance` does this from Search Console or analytics exports and the URL map).
Combine domain properties carefully and do not double-count overlapping exports.

## The diagnostic sequence

1. Confirm the metric definitions, the extraction dates and the reporting lag.
2. Check availability, redirects, indexing controls and canonical regressions.
3. Compare the important content and the discovery paths with the baseline.
4. Check analytics, consent, attribution and e-commerce tracking.
5. Review stock, promotions, seasonality and demand.
6. Review wider search changes, where the evidence makes them relevant.
7. Prioritise the findings by observed impact, each with a clear retest condition.

For each finding, label it **existing** (in the pre-migration baseline), **introduced** (by the migration),
**fixed** or **unresolved**. Without a baseline, say that the label cannot be established.

## Interpreting what you see

- Google notes that search visibility can fluctuate while a move is processed [S1]. Do not promise a fixed
  recovery deadline, and do not dismiss every decline as normal either.
- **Search Console clicks stable, analytics visits down:** investigate measurement and consent before
  asserting an SEO collapse.
- **Clicks down on one page group only:** look at that template, its redirects and its content first.
- **Impressions stable, clicks down:** check titles, snippets and rich results (structured data) on the new
  templates.
- **Orders down, organic visits stable:** look at checkout, stock, prices, promotions and tracking before SEO.

Before-and-after comparisons alone cannot prove what caused a change. Set alert thresholds from the baseline's
normal variability and the business importance of each page group; a fixed traffic-drop percentage is an
illustrative configuration choice, not a universal rule.

## The recovery diagnosis output

Findings, each with its evidence and label; the alternative explanations considered and why each was kept or
ruled out; and the ordered actions, each with an owner and a retest condition. Never invent live results, rank
improvements, traffic preservation or completed fixes.
