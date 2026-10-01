# Ecommerce SEO Website Migration: Learnings and Skill Blueprint

Research reviewed: 1 October 2026.

Suggested skill name: `ecommerce-seo-website-migration`.

## Purpose

Create a reusable, brand-neutral workflow that helps marketers plan a website migration, protect valuable organic landing pages, verify implementation, coordinate developer work and investigate problems after launch.

This document is a research and design blueprint. It is not an installed skill, a completed website audit or a promise that a migration will preserve all traffic. It contains anonymized operational lessons, concise summaries of primary documentation and proposed workflow rules. Examples and acceptance criteria are illustrative.

## 1. Core operational learnings

| Learning | Reusable practice |
|---|---|
| Preparing a redirect spreadsheet is only one part of migration delivery. | Verify actual production responses, final destinations, content relevance, indexability and internal links. |
| Product names and slugs can change during migration. | Match using stable identifiers and confirmed destinations before relying on names or slug similarity. |
| Collections and categories can be overlooked when the work starts with products. | Maintain separate inventories and test coverage for every important page type. |
| Redirects depend on destination readiness. | Prepare the map in advance, verify destinations and coordinate redirect activation with the cutover. |
| Migrated content can contain duplicated hostnames and other malformed links. | Inspect stored content, HTML templates and rendered links, rather than checking only the redirect configuration. |
| Different language versions require different URL decisions. | Map each locale, verify language equivalence and then validate relationships between locales. |
| Some content fields may be excluded from an individual's assignment. | Record excluded fields, unresolved issues and responsible owners in the handoff. |
| A website can appear to work while important SEO signals are wrong. | Evaluate HTTP responses, indexing rules, canonical signals, rendered content and discovery paths alongside visual checks. |
| Historical problems can be mistaken for migration regressions. | Capture a pre-migration baseline and label issues as existing, introduced, fixed or unresolved. |
| Missing evidence can create false confidence. | Distinguish passed, failed, not tested, not applicable and blocked checks. |

Do not publish historical audit counts or performance improvements unless the underlying evidence supports them and publication is authorized. The reusable value lies in the method and decisions.

## 2. Scope and operating modes

Support five modes:

1. **Plan:** Define scope, risks, dependencies, inputs and responsibilities before implementation.
2. **Map:** Create or review decisions for legacy URLs.
3. **Pre-launch QA:** Compare the old website with staging and assess readiness.
4. **Launch QA:** Verify the production website immediately after cutover.
5. **Recovery:** Investigate visibility, traffic or sales changes after a completed migration.

Choose the mode from the user's actual stage. An already-launched website needs diagnosis before an idealized planning checklist.

Produce useful work from available exports. Clearly identify what requires live access, rendered-page inspection or additional data.

## 3. Intake questions

Reuse supplied information and ask only questions that change the workflow:

- What are the current platform, destination platform and old/new hostnames?
- Are URLs, navigation, templates, content, languages, checkout or tracking changing?
- Is the migration planned, being implemented, launching now or already complete?
- Which countries, languages, page types and commercial pages matter most?
- What crawl, CMS, product, analytics, Search Console and backlink exports are available?
- Which products or pages will be removed, consolidated, renamed or newly created?
- Who owns SEO, development, content, merchandising, analytics and final launch decisions?
- Which areas are outside scope or unavailable for inspection?
- What is the launch window, content freeze process and incident response arrangement?

Do not demand every input before beginning. Missing data must limit conclusions rather than disappear from the report.

## 4. Classify the migration

| Migration type | Focus |
|---|---|
| Hosting or CDN change with unchanged URLs | Availability, DNS, certificates, crawler access, content parity and measurement continuity |
| CMS or ecommerce platform change | Routes, templates, content, links, metadata and platform constraints |
| Domain or subdomain move | Old-host redirect infrastructure, ownership verification and applicable move procedures |
| URL restructuring | Inventory coverage, destination relevance and redirect behavior |
| Redesign or headless rebuild | Rendered content, crawlable navigation and template regressions |
| Language or market restructuring | Locale destinations, canonical signals, hreflang and selectors |
| Combined migration | Dependencies and cumulative risk across the applicable branches |

Google provides separate guidance for URL-changing moves and hosting changes that preserve user-visible URLs. Apply the relevant branch rather than assuming every migration is a domain move. See [S1](#s1) and [S2](#s2).

## 5. Establish the baseline and URL inventory

### Inventory inputs

Combine available sources instead of treating a crawl as the complete inventory:

- Crawl exports and existing sitemaps.
- CMS, product, category and article exports.
- Search Console landing pages and queries.
- Analytics landing pages, conversions, orders and revenue.
- Backlink destinations and server logs where available.
- Image, video and document URLs that matter to discovery or users.

Record the source of each URL. An orphan URL or retired page can still receive search traffic or backlinks.

### Baseline design

Record the extraction date, timezone, property, filters and metric definitions. Use a recent baseline plus a longer seasonal view when the data supports it. These periods are proposed operating defaults, not universal migration requirements.

Segment by page type, locale, country, device and branded/non-branded queries where feasible. Capture organic clicks, impressions, CTR, position, visits, conversions and revenue separately; they describe different aspects of performance.

Store the current technical state: status, indexability, canonical, titles, headings, important content, internal links, hreflang and structured data. Distinguish expected changes from accidental losses.

## 6. Prioritize according to value and risk

Prioritize URLs using the available evidence:

- Organic search demand and clicks.
- Orders, revenue or other business conversions.
- Valuable backlinks and referring domains.
- Strategic importance and seasonal demand.
- Technical exposure, such as template-wide dependencies.

Do not treat unavailable revenue as zero revenue. Explain any scoring weights and allow the business to adjust them.

Proposed priority groups:

- **Critical:** Commercial or technical failures that require immediate attention.
- **High:** Important landing pages and defects affecting substantial page groups.
- **Standard:** Remaining eligible inventory and lower-impact issues.

Check every critical URL. If the remaining inventory is sampled, disclose the sampling method, page/locale coverage and untested population.

## 7. URL mapping as a decision process

### Recommended fields

| Group | Fields |
|---|---|
| Identity | Old URL, page type, locale, stable product/content ID |
| Value | Organic clicks, conversions, revenue, referring domains |
| Decision | Retain, redirect, consolidate, remove or investigate; proposed destination; rationale |
| Confidence | Match method, confidence, reviewer, owner and approval state |
| Verification | Actual final URL, status, hops, indexability, canonical, evidence and test time |

### Matching order

1. Approved explicit mapping.
2. Stable identifiers such as product IDs, SKUs or content IDs, with locale and variant checks.
3. Verified semantic equivalence of the old and new content.
4. Name or slug similarity as a candidate-generation method.
5. Human review when the match remains ambiguous.

Never automatically approve a fuzzy match solely because the strings look similar. Differences in product variants, language or user intent can make it wrong.

### Dispositions

- **Retain:** The URL and intended page remain valid; a redirect may not be needed.
- **Redirect:** A relevant replacement exists at another URL.
- **Consolidate:** Several old pages are genuinely covered by one new destination.
- **Remove:** The content is permanently gone with no suitable replacement.
- **Investigate:** Evidence is insufficient or decisions conflict.

Many-to-one mappings are not automatically wrong. Review whether the consolidated destination satisfies the old intent. Avoid sending unrelated pages to the homepage.

Google recommends permanent server-side redirects for URL moves, direct final destinations and long-lived redirect retention, generally at least one year. Change of Address is relevant to applicable domain/subdomain moves rather than ordinary path changes. See [S1](#s1).

## 8. Redirect verification

For each eligible redirect, record:

- The old URL response and Location header.
- Every hop and the final URL.
- Final status, content relevance and intended locale.
- Indexability and canonical signals at the destination.
- Unexpected host, protocol or path changes.
- Conflicts, loops, duplicate source decisions and redirects to errors.

Preserve raw evidence. A successful spreadsheet import or a final 200 response alone does not prove that the correct page was reached.

Test representative host variants, encoded paths and query-bearing URLs where these exist in the inventory. Preserve the original URLs; do not destructively normalize case, trailing slashes or meaningful parameters on assumptions.

Use bounded, rate-limited checks with timeouts. Report network failures separately from confirmed website defects.

## 9. Internal links and migrated content

Inspect navigation, footer, breadcrumbs, descriptions, collection copy, articles, related-product modules and app-generated components.

Look for:

- Old or staging hostnames.
- A hostname prepended to an already absolute URL.
- Relative URLs resolving under the wrong directory.
- Links reaching chains or error pages.
- Wrong-locale destinations.
- Missing images, documents or other assets.
- Important content lost during import or template replacement.

Illustrative malformed link:

```text
https://store.example/https://store.example/products/sample-item
```

Use URL parsing and observed responses to evaluate links; avoid a simplistic rule that labels every unusual string as broken. Prefer direct links to the intended canonical destination. Google's canonical documentation supports consistent internal linking; see [S4](#s4).

An editing exclusion is not a QA exclusion. If product-description links are outside the assigned editing scope, report the problem, owner and consequence.

## 10. Indexing and canonical signals

Compare intended behavior with:

- robots.txt access rules.
- Meta robots and X-Robots-Tag headers.
- Declared canonicals.
- Sitemap inclusion.
- Internal-link destinations.
- Google's selected canonical where Search Console evidence is available.

Canonical annotations are signals, not a guarantee that Google selects the declared URL. Avoid contradictory canonical signals. Keep language equivalence in mind when deciding canonical targets. See [S4](#s4).

Separate crawling from indexing. Blocking crawling can prevent Google from reading a noindex directive. A robots.txt block does not by itself guarantee removal from search. Check staging controls and their production removal without exposing staging unnecessarily. See [S9](#s9).

Record excluded or duplicate URLs as intentional when supported by the design; do not label every non-indexed URL as a migration failure.

## 11. Multilingual and international QA

Maintain a mapping for every applicable language/market. Verify:

- Correct product or content equivalence.
- Intended destination language and market availability.
- Valid language/region identifiers.
- Absolute alternate URLs, self-inclusion and reciprocal relationships.
- Canonical alignment and final destination behavior.
- Language selectors and fallback handling.
- Whether alternate URLs are actually accessible and appropriate for the cluster.

Google's hreflang guidance requires reciprocal references and each version's own inclusion. Hreflang identifies alternate versions; it does not translate missing content or replace a correct canonical design. See [S5](#s5).

Do not assume every market has the same catalog or a translated slug. Missing equivalents require explicit decisions.

## 12. Ecommerce-specific technical QA

### Products and variants

Validate product identity, variant selection, product links and query parameters. Compare price, currency, availability and structured data with the visible page and intended catalog. See [S6](#s6) and [S11](#s11).

Proposed merchandising rule: distinguish temporary unavailability from permanent retirement. Avoid removing or redirecting every unavailable item without reviewing its demand, content and future availability.

### Categories, collections and pagination

Verify crawlable discovery paths to products beyond the first listing page. Google advises distinct pagination URLs and a canonical for each page rather than automatically canonicalizing the entire sequence to page one. Its crawler generally does not click a load-more button. See [S7](#s7).

### Faceted navigation

Identify filters that serve meaningful search demand separately from combinations that generate low-value URL expansion. Decide whether the goal is discovery, index control or crawl-resource control. Canonicalization alone is not a comprehensive way to prevent faceted crawling. See [S8](#s8).

### JavaScript and rendering

For pages relying on JavaScript, inspect the rendered content as well as the initial response. Verify important text, product links, metadata and canonical consistency. Treat a plain HTTP fetch as insufficient evidence for rendered behavior. See [S10](#s10).

## 13. Shopify-specific considerations

Keep platform details in a separate reference module so the core workflow remains portable.

Shopify's current documentation describes important native redirect constraints:

- A source that still serves a valid page cannot be overridden by a native URL redirect.
- Reserved paths and certain URL patterns have restrictions.
- Locale/subfolder redirects need explicit handling.
- Query strings can behave unexpectedly and require testing.
- Browser/search-engine caching can affect redirect retests.

See [S3](#s3). Refresh platform guidance before implementation rather than treating this document as a permanent specification.

For domain moves, establish who controls the old domain and how its requests will reach the redirect infrastructure. New-store redirect entries alone do not establish that old-host traffic reaches them.

## 14. Tracking and wider marketing continuity

Proposed QA coverage:

- Analytics property and tag deployment continuity.
- Consent behavior and relevant tracking conditions.
- Page-view duplication or loss.
- Ecommerce event firing and transaction deduplication.
- Purchase value, currency and event definitions.
- Attribution parameters across relevant redirects.
- Checkout-domain behavior and cross-domain measurement where needed.
- Search Console ownership verification continuity.
- Paid-ad, email and profile landing links affected by URL changes.

Validate tracking against observed events and business records where available. Cross-domain measurement is conditional on the journey spanning domains, not mandatory for every migration. See [S12](#s12).

Separate a visibility decline from a measurement decline. A changed consent implementation or missing event can alter reported traffic/revenue even if the underlying business has not changed by the same amount.

## 15. Launch coordination and readiness

Prepare the following before cutover:

- Approved URL decisions and destination verification.
- Content freeze and final export/delta process.
- Redirect activation steps and responsible owner.
- Production indexing controls and sitemap checks.
- Availability, certificate and host checks.
- Measurement smoke checks.
- Incident contacts, backups and recovery procedures.

Proposed assessment states:

| State | Meaning |
|---|---|
| Ready | Required checks passed with current evidence. |
| Ready with recorded exceptions | Remaining issues have explicit owners and accepted treatment. |
| Blocked | Critical defects or evidence gaps prevent a reliable readiness recommendation. |

Potential blockers include inaccessible priority destinations, widespread staging canonicals, unintended indexing restrictions, failed priority redirects and loss of important content.

Every issue should include affected URLs, impact, evidence, proposed fix, owner, dependency and retest condition. Readiness is a recommendation; it does not independently authorize production changes.

Recovery planning should identify reversible actions and dependencies. Avoid assuming a DNS reversal is a complete rollback when orders, content, redirects or other systems have changed.

## 16. Post-launch monitoring and diagnosis

### Proposed cadence

- Immediate production smoke checks after cutover.
- Frequent technical checks during the early stabilization period.
- Regular performance reviews while pages are being processed.
- Longer-term redirect retention and maintenance.

Adjust frequency to inventory size, risk, data volume and observed failures. This is an operating framework, not a universal recovery timetable.

### Metrics

Track redirect failures, errors, intended indexing, canonical changes, clicks, impressions, CTR, position, visits, orders, revenue and conversion rate. Segment where feasible by locale, page type, device, country and query group.

Compare old/new URLs as mapped page groups. Otherwise a successful move may look like a total loss when only the old URL is inspected. Aggregate domain properties carefully and avoid double-counting overlapping exports.

### Diagnostic sequence

1. Confirm metric definitions, extraction dates and reporting lag.
2. Check availability, redirects, indexing controls and canonical regressions.
3. Compare important content and discovery paths.
4. Check analytics, consent, attribution and ecommerce tracking.
5. Review stock, promotions, seasonality and demand.
6. Review wider search changes where evidence makes them relevant.
7. Prioritize findings with observed impact and clear retest conditions.

Google notes that search visibility can fluctuate while a move is processed. Do not promise a fixed recovery deadline or dismiss all declines as normal. See [S1](#s1).

Use alert thresholds tied to baseline variability and business importance. A fixed traffic-drop percentage is an illustrative configuration choice, not a universal rule. Before/after comparisons alone cannot prove causality.

## 17. Required outputs for the future skill

1. **Migration brief:** Stage, scope, assumptions, evidence gaps and applicable branches.
2. **Prioritized inventory:** Page types, locales, value and risk.
3. **URL decision map:** Dispositions, destinations, rationale and review state.
4. **QA evidence register:** Observations, actual responses, test dates and coverage.
5. **Developer handoff:** Clear fixes, ownership, dependencies and acceptance criteria.
6. **Launch assessment:** Recommendation, blockers, exceptions and unresolved tests.
7. **Monitoring plan:** Metrics, segmentation, cadence and alert logic.
8. **Recovery diagnosis:** Findings, alternative explanations and ordered actions.

Use the following evidence states consistently:

```text
passed | failed | not_tested | not_applicable | blocked
```

Keep observation, interpretation and recommendation distinct. Never invent live results, rank improvements, traffic preservation or completed fixes.

## 18. Skill architecture

| Component | Purpose |
|---|---|
| SKILL.md | Concise trigger description, mode routing, intake, core workflow and output requirements |
| references/migration-types.md | Conditional workflows for hosting, domain, platform and combined changes |
| references/technical-qa.md | Links, indexing, rendering, pagination, facets and ecommerce checks |
| references/multilingual-qa.md | Locale mapping and international relationships |
| references/shopify.md | Current platform constraints and verification steps |
| references/recovery-diagnosis.md | Performance interpretation and evidence-based triage |
| templates/ | URL mapping, issue register, developer handoff and monitoring schemas |
| scripts/ | Optional deterministic checks |
| Synthetic examples | Realistic inputs and expected issue classifications without private data |

Repository-level usage documentation can explain installation, inputs and capabilities separately from the agent's core instructions. This document proposes an architecture; it does not contain those implemented resources.

Start with export-based inputs and optional live checks. Do not require paid SEO subscriptions or a paid LLM API for the deterministic scripts.

Suggested scripts:

- Validate URL-map schema, conflicting source decisions and missing dispositions.
- Test redirects with bounded requests and retain the full hop sequence.
- Compare old/new crawl exports by mapped page group.
- Identify malformed links and stale hosts.
- Validate hreflang relationships from supplied exports.
- Compare performance by mapped landing-page groups and declared segments.

Scripts should disclose their limits, preserve inputs and report failures. Authenticated access or rendered evidence may still require additional tools and authorization.

## 19. Evaluation scenarios

| Scenario | Expected behavior |
|---|---|
| Hosting move with unchanged URLs | Select the infrastructure branch; do not invent URL redirects. |
| Similar names but different product variants | Flag the ambiguous match for review. |
| Deleted page without a suitable replacement | Record a removal decision rather than inventing an irrelevant destination. |
| Several articles genuinely consolidated | Allow many-to-one mapping with a documented rationale. |
| Redirect destination returns 200 but is the wrong language | Fail the relevance/locale check. |
| Shopify source still serves a valid page | Explain the native redirect conflict and identify a treatment. |
| Important links exist only after user interaction | Request rendered/discovery evidence; do not declare a plain fetch sufficient. |
| Migrated copy contains a duplicated hostname | Report the malformed link with location, evidence and owner. |
| Product descriptions excluded from editing scope | Preserve the exclusion and assign unresolved QA findings. |
| Search Console clicks stable but analytics visits fall | Investigate measurement and consent before asserting an SEO collapse. |
| Missing priority-page evidence | Mark readiness as unresolved rather than passed. |
| Redirect graph contains a loop | Report the loop and affected sources. |

Test both output correctness and usefulness: the handoff must tell a marketer or developer what to change and how to verify it.

## 20. Potential companion skills

| Skill name | Primary output |
|---|---|
| ecommerce-seo-website-migration | Full migration plan, evidence register and launch/recovery assessment |
| seo-redirect-mapping-audit | Mapping gaps, conflicts, relevance issues and failed redirects |
| multilingual-seo-migration-qa | Locale and alternate-version issues |
| website-content-link-migration-qa | Malformed links, stale hosts, missing assets and content differences |
| seo-migration-performance-diagnosis | Segmented diagnosis and prioritized recovery actions |
| marketing-tracking-migration-qa | Measurement continuity checks and tracking gaps |

Build these as modules first. Split them into standalone skills when each has a clear independent trigger, useful inputs and an output that does not require the entire migration workflow.

## 21. Publication and confidentiality

- Publish decision rules, original templates and synthetic examples.
- Exclude private domains, identifiers, correspondence, screenshots and raw client exports.
- Check filenames, metadata, sample data and comments for identifying information.
- Use reserved example domains and invented product/content records.
- Substantiate any author-experience statements separately from measured case outcomes.
- Avoid claims that all traffic or rankings will be preserved.
- Link primary documentation and refresh changeable platform details before implementation.
- Do not reproduce entire third-party checklists or documentation.

## 22. Primary-source register

These sources were reviewed during research on 1 October 2026. Source summaries above are brief; the operational framework, schemas, examples and proposed acceptance criteria are original synthesis. Consult the live documentation before implementing platform-specific changes.

<a id="s1"></a>
### S1 — Google: Site moves with URL changes

Migration preparation, URL mapping, redirect strategy, applicable Change of Address procedures and monitoring.

https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

<a id="s2"></a>
### S2 — Google: Hosting changes with unchanged URLs

Infrastructure preparation, testing, crawler access, DNS cutover and verification continuity.

https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes

<a id="s3"></a>
### S3 — Shopify: Creating and managing URL redirects

Native redirect behavior, restrictions, locale handling and caching considerations.

https://help.shopify.com/en/manual/online-store/menus-and-links/url-redirect

<a id="s4"></a>
### S4 — Google: Canonical URLs

Canonical signals, consistency, duplicate-page handling and internal links.

https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls

<a id="s5"></a>
### S5 — Google: Localized page versions

Hreflang methods, valid codes, self-inclusion and reciprocal relationships.

https://developers.google.com/search/docs/specialty/international/localized-versions

<a id="s6"></a>
### S6 — Google: Ecommerce URL structure

Product variants, parameters and consistent URL use.

https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites

<a id="s7"></a>
### S7 — Google: Pagination and incremental loading

Crawlable pagination, unique URLs and canonical handling.

https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading

<a id="s8"></a>
### S8 — Google: Faceted navigation crawling

Filter URL expansion, crawl-resource implications and conditional crawl strategies.

https://developers.google.com/crawling/docs/faceted-navigation

<a id="s9"></a>
### S9 — Google: Robots meta tags and headers

Indexing directives and the requirement for crawler access to discover them.

https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

<a id="s10"></a>
### S10 — Google: JavaScript SEO basics

Crawling, rendering, content discovery and metadata handling.

https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics

<a id="s11"></a>
### S11 — Google: Product structured data

Product search appearance and structured-data implementation references.

https://developers.google.com/search/docs/appearance/structured-data/product

<a id="s12"></a>
### S12 — Google Analytics: Cross-domain measurement

Measurement continuity when relevant journeys span multiple domains.

https://support.google.com/analytics/answer/10071811?hl=en
