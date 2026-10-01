# Primary-source register

Reviewed on 1 October 2026. Summaries in this skill are brief; the workflow, schemas, examples and acceptance
criteria are original synthesis. Consult the live documentation before implementing platform-specific changes,
and record the date you checked it.

| ID | Source | Used for |
| --- | --- | --- |
| S1 | Google: Site moves with URL changes. https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes | Preparation, URL mapping, permanent server-side redirects, retention, Change of Address, monitoring |
| S2 | Google: Hosting changes with unchanged URLs. https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes | Infrastructure preparation, testing, crawler access, DNS cutover, verification continuity |
| S3 | Shopify: Creating and managing URL redirects. https://help.shopify.com/en/manual/online-store/menus-and-links/url-redirect | Native redirect behaviour, restrictions, locale handling, caching |
| S4 | Google: Canonical URLs. https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls | Canonical signals, consistency, duplicates, internal links |
| S5 | Google: Localized page versions. https://developers.google.com/search/docs/specialty/international/localized-versions | Hreflang methods, valid codes, self-inclusion, reciprocity |
| S6 | Google: Ecommerce URL structure. https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites | Product variants, parameters, consistent URLs |
| S7 | Google: Pagination and incremental loading. https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading | Crawlable pagination, unique URLs, canonical handling |
| S8 | Google: Faceted navigation crawling. https://developers.google.com/crawling/docs/faceted-navigation | Filter URL expansion, crawl resources, crawl strategies |
| S9 | Google: Robots meta tags and headers. https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag | Indexing directives; crawler access needed to see them |
| S10 | Google: JavaScript SEO basics. https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics | Crawling, rendering, content discovery, metadata |
| S11 | Google: Product structured data. https://developers.google.com/search/docs/appearance/structured-data/product | Product search appearance and structured data |
| S12 | Google Analytics: Cross-domain measurement. https://support.google.com/analytics/answer/10071811?hl=en | Measurement continuity when journeys span domains |

## Updating the register

When a rule you rely on is not here, or one here has changed: use the platform's current official documentation
as the source, update this table with the URL and the date checked, update the reference file that uses it, and
never generalise one platform's rule to another.
