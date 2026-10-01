# Shopify

Platform details are kept here so the core workflow stays portable. They come from Shopify's documentation on
URL redirects as reviewed on 1 October 2026 [S3]. Shopify changes; refresh this against the live documentation
before implementation, and say when you could not.

## Native redirect constraints [S3]

- **A live page wins.** A native URL redirect cannot override a source path that still serves a valid page. If
  the old URL still resolves (for example a product or page that was not deleted or renamed), the redirect will
  not fire. Treatment: remove, unpublish or rename the source resource first, or handle the route another way,
  then retest.
- **Reserved paths and patterns.** Some paths and URL patterns cannot be redirected natively. Check each
  pattern the map relies on.
- **Locales and subfolders.** Redirects for locale subfolders need explicit handling; do not assume a redirect
  for one locale covers the others.
- **Query strings** can behave unexpectedly. Test the query-bearing URLs that exist in the inventory, including
  tracking parameters.
- **Caching.** Browsers and search engines cache redirects, so a retest from the same browser can show an old
  result. Retest with a clean client (the redirect script does not cache).

## Shopify URL structure to inventory

Inventory each resource type separately: products (`/products/`), collections (`/collections/`), products
inside collection paths (`/collections/<handle>/products/<handle>`), pages (`/pages/`), blog articles
(`/blogs/<blog>/<article>`), and locale or market subfolders. Product URLs reachable through collection paths
usually canonicalise to the plain product URL; check what the theme declares.

## Domain moves onto or off Shopify

Establish who controls the old domain, and how its requests will reach the redirect infrastructure. Redirect
entries created in the new store do not prove that traffic to the old host reaches them: the old host needs DNS
and a server, proxy or platform setting that answers with the redirects.

## Migrated content

Content imported into Shopify (product descriptions, collection copy, pages, articles) often carries old-host
links, duplicated hostnames and broken relative links. Check stored content and rendered pages, not only the
redirect table (`technical-qa.md`). Apps can inject components with their own links; include them.

## What to verify after any Shopify redirect change

The source returns a permanent redirect (not a 200 from a still-live page); the hop count is one; the destination
is the intended resource and locale; the destination is indexable and self-canonical (or canonical as designed);
and query strings that matter survive or are handled as intended.
