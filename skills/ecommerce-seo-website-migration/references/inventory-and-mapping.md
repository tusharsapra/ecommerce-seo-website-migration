# Baseline, inventory, prioritisation and URL mapping

## The inventory comes from many sources

A crawl is not the inventory. Combine what is available, and record the source of every URL:

- Crawl exports and existing sitemaps.
- CMS, product, category and article exports.
- Search Console landing pages and queries.
- Analytics landing pages, conversions, orders and revenue.
- Backlink destinations, and server logs where available.
- Image, video and document URLs that matter to discovery or users.

An orphan URL or a retired page can still receive search traffic or backlinks. Keep separate inventories, and
separate test coverage, for every important page type: products, variants, collections or categories, pages,
articles, and any landing pages. Collections are easy to forget when the work starts from products.

## The baseline

Record the extraction date, timezone, property, filters and metric definitions of every export. Use a recent
baseline plus a longer seasonal view where the data supports it; those periods are operating defaults, not
universal requirements.

Segment by page type, locale, country, device and branded versus non-branded queries where feasible. Keep
organic clicks, impressions, CTR, position, visits, conversions and revenue separate: they describe different
things.

Store the current technical state of the priority URLs: status, indexability, canonical, title, headings,
important content, internal links, hreflang and structured data. That is what lets you label later issues as
**existing, introduced, fixed or unresolved**, so a historical problem is not mistaken for a migration regression,
and an expected change is not mistaken for an accidental loss.

## Prioritise by value and risk

Use the evidence there is:

- organic demand and clicks;
- orders, revenue or other business conversions;
- valuable backlinks and referring domains;
- strategic importance and seasonal demand;
- technical exposure, such as a template that many pages depend on.

Unavailable revenue is not zero revenue. If you score, explain the weights and let the business change them.

| Priority | Meaning |
| --- | --- |
| Critical | Commercial or technical failures that need immediate attention |
| High | Important landing pages, and defects affecting large page groups |
| Standard | The rest of the eligible inventory, and lower-impact issues |

Check every critical URL. If the rest is sampled, disclose the sampling method, the page-type and locale
coverage, and the population left untested.

## The URL decision map

Use `assets/templates/url-map.csv`. `scripts/migration_checks.py map` validates it.

| Group | Fields |
| --- | --- |
| Identity | Old URL, page type, locale, stable product or content ID |
| Value | Organic clicks, conversions, revenue, referring domains |
| Decision | Retain, redirect, consolidate, remove or investigate; proposed destination; rationale |
| Confidence | Match method, confidence, reviewer, owner, approval state |
| Verification | Actual final URL, status, hops, indexability, canonical, evidence, test time |

### Matching order

1. An approved explicit mapping.
2. Stable identifiers: product IDs, SKUs or content IDs, with locale and variant checks.
3. Verified semantic equivalence of the old and the new content.
4. Name or slug similarity, as a way to generate candidates only.
5. Human review when the match is still ambiguous.

Never approve a fuzzy match because the strings look alike. A different variant, language or intent makes it
wrong. Product names and slugs often change in a migration, which is exactly why stable IDs come first.

### Dispositions

| Disposition | Use when |
| --- | --- |
| Retain | The URL and the intended page stay valid; a redirect may not be needed |
| Redirect | A relevant replacement exists at another URL |
| Consolidate | Several old pages are genuinely covered by one new destination |
| Remove | The content is permanently gone with no suitable replacement |
| Investigate | The evidence is insufficient or the decisions conflict |

Many-to-one is not automatically wrong: check that the consolidated destination serves each old page's intent.
Do not send unrelated pages to the homepage. A removed page should not be given an irrelevant destination just
to avoid a 404 or 410.

Google recommends permanent server-side redirects for URL moves, straight to the final destination (no
chains), kept for a long time, generally at least a year [S1].

Redirects depend on their destinations: prepare the map in advance, verify the destinations exist and are
correct, and coordinate switching the redirects on with the cutover.
