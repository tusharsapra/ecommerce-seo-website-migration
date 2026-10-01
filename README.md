# E-commerce SEO Website Migration

I am Tushar Sapra, a marketing expert with experience across clients and campaigns. I built this skill to help e-commerce teams plan website migrations, protect valuable organic pages, verify launch quality, and diagnose SEO changes using evidence.

A skill for Claude Code and Codex that helps a marketer plan a website migration, protect the organic landing
pages that matter, verify what was actually built, coordinate the developer work, and investigate problems after
launch.

It is brand-neutral and platform-portable, with Shopify specifics in their own module. It works from the exports
you already have (crawls, CMS and product exports, Search Console, analytics, backlinks), with optional bounded
live redirect checks. It needs no paid SEO subscription and no API keys.

**It never changes your site.** The deliverable is plans, maps, QA evidence, developer handoffs, a readiness
recommendation and diagnoses. It never promises that a migration will keep all its traffic, and never invents
live results or completed fixes.

## Five modes, chosen from where you actually are

| Mode | When | You get |
| --- | --- | --- |
| Plan | Before implementation | A migration brief: scope, migration types and branches, risks, dependencies, inputs, owners |
| Map | Deciding each legacy URL | A prioritised inventory and a URL decision map (retain, redirect, consolidate, remove, investigate) |
| Pre-launch QA | Old site against staging | A QA evidence register, a developer handoff and a launch assessment |
| Launch QA | Right after cutover | Production smoke checks with evidence, and issues with owners and retest conditions |
| Recovery | After launch, when traffic, rankings or sales moved | A diagnosis by mapped page group, alternative explanations, and ordered actions |

## The rules it works by

- **Classify first.** A hosting move with unchanged URLs, a platform change, a domain move, a URL restructure, a
  redesign and a language change each have their own branch; real migrations combine them.
- **A crawl is not the inventory.** URLs come from crawls, sitemaps, CMS and product exports, Search Console,
  analytics, backlinks and logs, each with its source recorded.
- **Stable IDs before names.** URLs are matched by approved mapping, then product IDs or SKUs, then verified
  equivalence. Name and slug similarity only suggest candidates for human review. Nothing unrelated is sent to
  the homepage.
- **Verify responses, not spreadsheets.** Every hop, the final URL, its status, relevance, language, indexability
  and canonical. A 200 in the wrong language is a failure.
- **Five evidence states:** `passed`, `failed`, `not_tested`, `not_applicable`, `blocked`. Missing evidence on a
  priority page is never a pass, and network failures are never counted as defects.
- **Label issues against the baseline:** existing, introduced, fixed or unresolved, so old problems are not
  blamed on the migration.
- **Compare mapped page groups,** not old URLs, and keep a measurement drop apart from a visibility drop.

## The checks script

`scripts/migration_checks.py` is standard-library Python:

| Command | What it checks |
| --- | --- |
| `map` | Missing or invalid decisions, conflicting rows, chains, loops, homepage dumps, unapproved fuzzy matches, locale mismatches, consolidations without a rationale, destinations that fail in the new crawl |
| `redirects` | Live, bounded and rate-limited: every hop, permanent versus temporary, chains, loops, final status, destination match, noindex (meta and header), canonical, language, homepage endings, removals and retained URLs. Network failures are `blocked` |
| `links` | Duplicated hostnames, old and staging or preview hosts, document-relative links, `javascript:` links, http links, broken links and links to redirects |
| `hreflang` | Invalid codes (including `en-uk`), relative alternates, missing self-references, missing return links, conflicting alternates, and alternates that do not return 200 or canonicalise elsewhere |
| `crawl-diff` | Old against new crawl by mapped pair: status, indexability, canonical, title, H1, content drop and structured data, labelled existing or introduced |
| `performance` | Search Console or analytics before and after, aggregated by mapped page group and page type, with impression-weighted position |

```bash
cd skills/ecommerce-seo-website-migration/assets/synthetic-examples
python3 ../../scripts/migration_checks.py map url-map.csv --new-crawl crawl-new.csv
python3 ../../scripts/migration_checks.py performance gsc-before.csv gsc-after.csv --map url-map.csv
```

Run `redirects` only against sites you own or are authorised to test. It defaults to 200 URLs at 2 requests a
second, a 10-second timeout and at most 10 hops.

## Install

```bash
./install.sh            # links the skill into ~/.claude/skills and ~/.agents/skills (and ~/.codex/skills)
./install.sh --copy     # copy instead of link
./install.sh --project /path/to/repo
./install.sh --uninstall
```

The repo also ships Claude Code and Codex plugin manifests over the same `skills/` folder, and works with
`npx skills add`. Use it with `/ecommerce-seo-website-migration` in Claude Code or `$ecommerce-seo-website-migration`
in Codex, or just describe the migration.

## Files

```
skills/ecommerce-seo-website-migration/
  SKILL.md                              triggering, modes, intake, the workflow, evidence states, outputs
  references/migration-types.md         the branches, and the migration brief
  references/inventory-and-mapping.md   baseline, inventory sources, prioritisation, the URL decision map
  references/technical-qa.md            redirects, links and content, indexing and canonicals, e-commerce, tracking
  references/multilingual-qa.md         locale mapping and hreflang
  references/shopify.md                 Shopify's native redirect constraints and checks
  references/launch-readiness.md        cutover preparation, readiness states, launch QA, the handoff
  references/recovery-diagnosis.md      monitoring, the diagnostic sequence, interpretation
  references/sources.md                 the primary-source register
  assets/templates/                     migration brief, URL map, QA evidence register, issue register,
                                        developer handoff, launch assessment, monitoring plan
  assets/synthetic-examples/            a fictional store's migration inputs, with planted problems
  scripts/migration_checks.py           the deterministic checks
  agents/openai.yaml                    Codex display metadata
docs/research-spec.md                   the research and design blueprint this skill implements
tests/test_migration_checks.py          tests; redirect checks run against a local server
```

## Sources

Google and Shopify documentation reviewed on 1 October 2026, listed in `references/sources.md`. Platform details
change: the skill tells the agent to check the live documentation before implementing platform-specific changes.

All examples use reserved `.example` domains and invented records. No client data is included.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT.
