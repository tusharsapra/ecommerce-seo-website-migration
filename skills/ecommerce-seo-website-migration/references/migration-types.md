# Migration types and their branches

Classify the migration before planning or testing anything. Most real migrations combine several types; run
every branch that applies and track the dependencies between them, because the risk is cumulative.

| Migration type | Focus |
| --- | --- |
| Hosting or CDN change, URLs unchanged | Availability, DNS, certificates, crawler access, content parity, measurement continuity |
| CMS or e-commerce platform change | Routes, templates, content, links, metadata, platform constraints |
| Domain or subdomain move | Old-host redirect infrastructure, ownership verification, the applicable move procedures |
| URL restructuring | Inventory coverage, destination relevance, redirect behaviour |
| Redesign or headless rebuild | Rendered content, crawlable navigation, template regressions |
| Language or market restructuring | Locale destinations, canonical signals, hreflang, selectors |
| Combined migration | Dependencies and cumulative risk across every applicable branch |

Google has separate guidance for moves that change URLs [S1] and for hosting changes that keep the URLs users
see [S2]. Apply the branch that fits. Do not treat every migration as a domain move, and do not invent URL
redirects for a hosting move whose URLs do not change.

## Branch: hosting or CDN change, URLs unchanged [S2]

- Inventory stays the same; the job is parity and availability.
- Check DNS cutover planning (TTL lowered in advance), certificates on every host variant, and that crawlers are
  not blocked by the new infrastructure (firewall, bot protection, rate limits).
- Compare old and new responses for the priority URLs: status, indexing controls, canonical, rendered content.
- Keep Search Console verification working through the change (a DNS or file verification can break).
- Check analytics tags and consent behaviour still fire after the switch.

## Branch: CMS or e-commerce platform change

- Every URL pattern may change: products, variants, collections or categories, pages, articles, search,
  pagination, filters.
- Templates are rebuilt: titles, headings, canonical, structured data, internal links and indexing controls are
  all regenerated and need checking per template, not just per page.
- Content is imported: check stored content, templates and rendered links for import damage
  (`technical-qa.md`).
- Platform constraints decide what is possible (for Shopify, see `shopify.md`).

## Branch: domain or subdomain move [S1]

- The old host must keep answering: someone must control the old domain and its DNS, and its requests must
  reach redirect infrastructure. Redirect entries in the new store alone do not prove that old-host traffic
  reaches them.
- Permanent, server-side redirects from each old URL directly to its final new URL.
- Search Console's Change of Address tool applies to domain and subdomain moves, not to ordinary path changes.
- Verify ownership of both properties before the move.

## Branch: URL restructuring

- Build the inventory from every source, not just a crawl (`inventory-and-mapping.md`).
- Every old URL gets a decision; redirects point to relevant destinations, directly, with no chains.

## Branch: redesign or headless rebuild

- The URLs may stay the same while the content changes. Compare rendered content, navigation links and
  metadata, template by template.
- JavaScript-rendered content needs rendered evidence; a plain HTTP fetch is not enough [S10].
- Check that navigation and product links are real crawlable links, not only click handlers, and that
  products beyond the first listing page stay discoverable [S7].

## Branch: language or market restructuring

- Map every locale separately and verify language equivalence (`multilingual-qa.md`).
- Do not assume every market has the same catalogue or translated slugs.

## The migration brief

Record, before any work: the stage (planned, implementing, launching, launched), the migration types and
branches, the old and new platforms and hostnames, what is changing (URLs, navigation, templates, content,
languages, checkout, tracking), the priority markets and page types, the inputs available, the owners, what is
out of scope or cannot be inspected, the launch window and the incident arrangements. Use
`assets/templates/migration-brief.md`.
