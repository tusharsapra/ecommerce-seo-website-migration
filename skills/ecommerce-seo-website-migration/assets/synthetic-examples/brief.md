# Example brief: Trailhead Supply (fictional)

Synthetic example. The company, domains (reserved `.example` names), products, URLs and numbers are invented to
exercise the skill and its scripts. They are not a case study and not benchmarks.

- **Stage:** pre-launch QA on staging; launch planned for 2026-10-20.
- **Migration:** a legacy platform at `old-store.example` moves to Shopify at `store.example` (domain move,
  platform change and URL restructuring together). Staging is `staging.store.example`.
- **Locales:** English (root) and German (`/de/`). Not every product exists in both markets.
- **What changes:** product and collection URLs (`/p/<id>-<slug>` becomes `/products/<handle>`, `/c/<slug>`
  becomes `/collections/<handle>`), templates, navigation and the blog. Checkout moves to Shopify's checkout.
- **Removed or consolidated:** two discontinued products; two old buying-guide articles merged into one.
- **Inputs:** a URL map draft, crawls of the old site and of staging, a link export, an hreflang export, and
  Search Console page exports for 28 days before and 28 days after a test cutover of the blog.
- **Owners:** SEO lead (map, QA), Shopify developer (redirects, templates), content editor (descriptions and
  articles), analytics lead (tracking). Product descriptions are outside the developer's editing scope.
- **Known gaps:** no backlink export yet; no revenue by landing page.
