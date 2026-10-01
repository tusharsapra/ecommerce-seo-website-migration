# Multilingual and international QA

Keep a mapping for every language and market. Different language versions need different URL decisions:
map each locale, verify language equivalence, then validate the relationships between locales.

## What to verify

- The product or content is genuinely equivalent across locales.
- The destination is in the intended language, and the product is available in that market.
- Language and region codes are valid (ISO 639-1 language, optional ISO 3166-1 alpha-2 region, or `x-default`).
- Alternate URLs are absolute, each page includes itself, and every relationship is reciprocal.
- Canonicals align with the hreflang cluster, and the final destination of each alternate is the alternate
  itself, not a redirect.
- Language selectors work and fallback handling is intended.
- Every alternate URL is accessible and appropriate for its cluster.

Google's hreflang guidance requires reciprocal references and each version's own inclusion [S5]. Hreflang
identifies alternate versions; it does not translate missing content and does not fix a wrong canonical design.
A page that canonicalises to another language version breaks the cluster.

## Decisions to make explicitly

- Not every market has the same catalogue. A product missing in one market needs an explicit decision (no
  alternate, a market-specific substitute, or a removal), not a guess.
- Not every slug is translated. Do not assume a locale's URL from another locale's slug.
- Locale subfolder redirects need explicit handling on some platforms (for Shopify, see `shopify.md`).

## Checks the script runs

`scripts/migration_checks.py hreflang` reads an export of `page_url, hreflang, alternate_url` rows (one per
annotation, from a crawler or sitemaps) and reports:

- invalid or malformed codes;
- relative alternate URLs;
- pages that do not include themselves;
- missing return links (A lists B, B does not list A);
- one code pointing to two different URLs on the same page;
- alternates that are not in the crawl, or that do not return 200 (when a crawl export is supplied);
- clusters without an `x-default`, reported as information, not as a failure.

Language equivalence of the content itself still needs a human or a rendered review: the script checks the
annotations, not the translation.
