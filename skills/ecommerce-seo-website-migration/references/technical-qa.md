# Technical QA

Every check ends in one of five evidence states, used consistently everywhere:

`passed | failed | not_tested | not_applicable | blocked`

`blocked` means the check could not be run (no access, a network failure, a missing export). It is never
counted as passed. Keep observation, interpretation and recommendation apart in every finding.

## Redirect verification

For each eligible redirect, record:

- the old URL's response and its Location header;
- every hop, and the final URL;
- the final status, whether the content is relevant, and whether it is the intended locale;
- indexability and canonical signals at the destination;
- any unexpected change of host, protocol or path;
- conflicts, loops, duplicate source decisions, and redirects that end in errors.

Keep the raw evidence. A successful spreadsheet import, or a final 200, does not prove the right page was
reached: a 200 in the wrong language or on an unrelated page is a failed check.

Test representative host variants (with and without www, http and https), encoded paths and URLs with query
strings where they exist in the inventory. Keep the original URLs: do not normalise case, trailing slashes or
meaningful parameters on assumption.

`scripts/migration_checks.py redirects` makes bounded, rate-limited requests with timeouts, keeps the full hop
sequence, and reports network failures as `blocked`, separately from confirmed defects. Run it only against
sites the user owns or is authorised to test, and keep the rate low on production.

## Internal links and migrated content

Inspect navigation, footer, breadcrumbs, product descriptions, collection copy, articles, related-product
modules and components added by apps. Look for:

- old or staging hostnames;
- a hostname prepended to an already absolute URL, for example
  `https://store.example/https://store.example/products/sample-item`;
- relative URLs resolving under the wrong directory;
- links that reach a chain or an error;
- links to the wrong locale;
- missing images, documents or other assets;
- important content lost during import or template replacement.

Inspect stored content, HTML templates and rendered links, not just the redirect configuration. Evaluate links by
parsing them and observing their responses; do not mark every unusual string as broken.
`scripts/migration_checks.py links` finds malformed links and stale hosts in a link export.

Prefer direct links to the intended canonical destination; consistent internal linking supports the canonical
choice [S4].

**An editing exclusion is not a QA exclusion.** If, say, product-description links are outside someone's editing
scope, still report the problem, its owner and its consequence in the handoff.

## Indexing and canonical signals

Compare the intended behaviour with:

- robots.txt rules;
- meta robots and X-Robots-Tag headers;
- the declared canonical;
- sitemap inclusion;
- where internal links point;
- the canonical Google selected, where Search Console evidence exists.

A canonical is a signal, not a guarantee that Google selects the declared URL. Avoid contradictory signals, and
keep language equivalence in mind when choosing canonical targets [S4].

Crawling and indexing are separate. Blocking crawling can stop Google from reading a noindex directive, and a
robots.txt block alone does not guarantee removal from search [S9]. Check that staging controls (password,
noindex, robots blocks) are removed from production, without exposing staging unnecessarily.

Some URLs are excluded or treated as duplicates by design. Record them as intentional where the design supports
it; not every non-indexed URL is a migration failure.

## E-commerce checks

**Products and variants.** Validate product identity, variant selection, product links and query parameters.
Compare price, currency, availability and structured data with the visible page and the intended catalogue
[S6] [S11]. Distinguish temporary unavailability from permanent retirement: do not remove or redirect every
unavailable item without looking at its demand, content and future availability.

**Categories, collections and pagination.** Products beyond the first listing page need crawlable discovery
paths. Google advises distinct URLs for paginated pages, each with its own canonical, rather than canonicalising
the whole sequence to page one; its crawler generally does not click "load more" buttons [S7].

**Faceted navigation.** Separate filters that serve real search demand from combinations that only multiply
low-value URLs. Decide whether the goal is discovery, index control or crawl-resource control. Canonicals alone
do not stop faceted crawling [S8].

**JavaScript and rendering.** For pages that rely on JavaScript, inspect the rendered page as well as the initial
response: important text, product links, metadata and canonical consistency [S10]. A plain HTTP fetch is not
evidence of rendered behaviour; if you only have that, the rendered checks are `not_tested`.

## Tracking and wider marketing continuity

Check:

- the analytics property and tag deployment;
- consent behaviour and the conditions tracking depends on;
- page-view duplication or loss;
- e-commerce events firing, and transaction deduplication;
- purchase value, currency and event definitions;
- attribution parameters surviving the relevant redirects;
- checkout-domain behaviour, and cross-domain measurement where the journey spans domains [S12] (it is not
  needed for every migration);
- Search Console ownership verification;
- paid ads, email and profile links that point at changed URLs.

Validate tracking against observed events and business records where available. Keep a visibility decline apart
from a measurement decline: a changed consent setup or a missing event can move reported traffic or revenue more
than the business actually moved.

## Every finding needs

the affected URLs (or URL pattern), the impact, the evidence, the proposed fix, the owner, any dependency, and the
retest condition. Use `assets/templates/issue-register.csv`.
