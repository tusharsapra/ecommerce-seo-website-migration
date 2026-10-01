---
name: ecommerce-seo-website-migration
description: >-
  Plan, map, QA and recover an e-commerce website migration for SEO. Use when a store is changing platform,
  domain, hosting, URL structure, design, templates or languages (for example moving to Shopify), and needs a
  migration plan, a URL redirect map, pre-launch or launch QA, a developer handoff, a launch readiness call,
  a monitoring plan, or a diagnosis of traffic, ranking or sales drops after a migration. Works from crawl,
  CMS, product, Search Console, analytics and backlink exports, with optional bounded live checks. Validates
  redirect maps, tests redirects hop by hop, finds malformed links and stale hosts, checks hreflang, compares
  old and new crawls and performance by mapped page group. Records every check as passed, failed,
  not_tested, not_applicable or blocked, and never promises traffic preservation or invents results.
license: MIT
compatibility: Works in any Agent Skills host. The optional checks script needs Python 3.8+ (standard library only); its redirects check needs network access to the sites being tested.
metadata:
  short-description: SEO-safe e-commerce migrations, from URL map to recovery
  version: "1.0.0"
---

# E-commerce SEO website migration

Help a marketer plan a website migration, protect the organic landing pages that matter, verify what was
actually built, coordinate the developer work, and investigate problems after launch. Brand-neutral and
platform-portable; Shopify specifics live in their own reference.

What the user typed after the skill name: `$ARGUMENTS`. If that is blank, or still reads literally as a
placeholder, take the request from the conversation.

All file paths below are relative to this skill's folder (the folder that holds this SKILL.md).

## Boundaries

- The deliverable is plans, maps, QA evidence, handoffs and diagnoses. It does not change the site, the
  redirects, DNS or any account. A readiness call is a recommendation, never an authorisation.
- Never invent live results, rank changes, traffic preservation or completed fixes. Never promise that a
  migration will keep all traffic, or give a fixed recovery date.
- Live checks only against sites the user owns or is authorised to test, bounded and rate-limited.
- Keep observation, interpretation and recommendation apart in every finding.

## Step 1: find the stage, choose the mode

Choose from the user's actual stage. An already-launched site needs diagnosis before an idealised checklist.

| Mode | When | Load |
| --- | --- | --- |
| Plan | Before implementation: scope, risks, dependencies, inputs, owners | `references/migration-types.md`, `references/inventory-and-mapping.md` |
| Map | Deciding what happens to each legacy URL | `references/inventory-and-mapping.md` (+ `references/multilingual-qa.md` for several locales) |
| Pre-launch QA | Comparing the old site with staging, assessing readiness | `references/technical-qa.md`, `references/launch-readiness.md` (+ multilingual, + `references/shopify.md`) |
| Launch QA | Verifying production immediately after cutover | `references/launch-readiness.md`, `references/technical-qa.md` |
| Recovery | Visibility, traffic or sales changed after a completed migration | `references/recovery-diagnosis.md`, `references/technical-qa.md` |

Then classify the migration (hosting or CDN, platform, domain or subdomain, URL restructuring, redesign or
headless, language or market, combined) with `references/migration-types.md` and run only the branches that
apply. A hosting move with unchanged URLs gets no invented redirects. Load `references/shopify.md` for any
Shopify site, and `references/sources.md` when you cite Google or Shopify guidance.

## Step 2: intake

Reuse what the user supplied, and ask only what changes the workflow:

- current and destination platforms, and the old and new hostnames;
- what changes: URLs, navigation, templates, content, languages, checkout, tracking;
- the stage: planned, implementing, launching now, or already complete;
- the countries, languages, page types and commercial pages that matter most;
- which exports exist: crawl, CMS, product, analytics, Search Console, backlinks;
- what is being removed, consolidated, renamed or created;
- who owns SEO, development, content, merchandising, analytics and the launch decision;
- what is out of scope or cannot be inspected;
- the launch window, the content freeze and the incident arrangements.

Do not demand every input before starting. Produce useful work from the exports there are, say what needs live
access, rendered pages or more data, and let missing data limit the conclusions rather than disappear from the
report. Record it all in `assets/templates/migration-brief.md`.

## Step 3: do the work

- **Baseline and inventory.** Combine every URL source (crawl, sitemaps, CMS and product exports, Search
  Console, analytics, backlinks, logs), keep page types separate, and record the current technical state, so
  later issues can be labelled existing, introduced, fixed or unresolved.
- **Prioritise** by organic value, conversions and revenue, backlinks, strategic and seasonal importance, and
  technical exposure. Unknown revenue is not zero. Check every critical URL; disclose any sampling.
- **Map** every old URL to retain, redirect, consolidate, remove or investigate, matching by approved mapping,
  then stable IDs, then verified equivalence; name and slug similarity only generate candidates for human review.
  No irrelevant homepage redirects. Use `assets/templates/url-map.csv`.
- **Verify** actual responses, not the spreadsheet: every hop, the final URL, status, relevance, locale,
  indexability and canonical; then internal links and migrated content, indexing controls, products and
  variants, pagination, facets, rendering, international relationships and tracking continuity.
- **Hand off** each issue with affected URLs, impact, evidence, the fix, owner, dependency and retest condition
  (`assets/templates/issue-register.csv`, `assets/templates/developer-handoff.md`). An editing exclusion is not a
  QA exclusion: report problems in excluded fields with their owner.
- **Assess readiness** as Ready, Ready with recorded exceptions, or Blocked
  (`assets/templates/launch-assessment.md`). Missing evidence on priority pages is never a pass.
- **Monitor and diagnose** by mapped page group, in the order given in `references/recovery-diagnosis.md`, and
  separate a visibility decline from a measurement decline (`assets/templates/monitoring-plan.md`).

## Evidence states (always)

Every check is exactly one of:

`passed | failed | not_tested | not_applicable | blocked`

`blocked` is a check that could not run (no access, a network failure, a missing export). Network failures are
reported apart from confirmed defects. A final 200 does not prove the right page was reached: wrong language,
wrong product or an unrelated page is `failed`. A plain HTTP fetch does not prove rendered behaviour: without
rendered evidence those checks are `not_tested`. Keep raw evidence and the test time for each result.

## The checks script

`scripts/migration_checks.py` (standard-library Python) does the deterministic work. Run it whenever the user
has the inputs, and quote its findings rather than re-deriving them:

```bash
python3 scripts/migration_checks.py map URL_MAP.csv [--new-crawl NEW_CRAWL.csv]
python3 scripts/migration_checks.py redirects URL_MAP.csv --priority critical,high --rate 2 --out results.csv
python3 scripts/migration_checks.py links LINKS.csv --host store.example --old-host old.example --staging-host staging.example
python3 scripts/migration_checks.py hreflang HREFLANG.csv [--crawl NEW_CRAWL.csv]
python3 scripts/migration_checks.py crawl-diff OLD_CRAWL.csv NEW_CRAWL.csv --map URL_MAP.csv
python3 scripts/migration_checks.py performance BEFORE.csv AFTER.csv --map URL_MAP.csv
```

- `map` finds missing or invalid decisions, conflicting rows, chains, loops, homepage dumps, unapproved fuzzy
  matches, locale mismatches, consolidations without a rationale, and destinations that fail in the new crawl.
- `redirects` makes live requests (bounded by `--limit`, `--rate` requests a second, `--timeout`, `--max-hops`),
  keeps the full hop sequence and grades each URL against its decision. Ask before running it on production,
  keep the rate low, and remember that browsers cache redirects but the script does not.
- `links`, `hreflang`, `crawl-diff` and `performance` work offline from exports.

If Python is not available, apply the same rules by hand from the references.

## Outputs

Choose what the request needs: a migration brief, a prioritised inventory, a URL decision map, a QA evidence
register (`assets/templates/qa-evidence-register.csv`), a developer handoff, a launch assessment, a monitoring
plan, or a recovery diagnosis. Each should tell a marketer or developer what to change and how to verify it.

## Files

- `references/`: migration types, inventory and mapping, technical QA, multilingual QA, Shopify, launch
  readiness, recovery diagnosis, sources.
- `assets/templates/`: migration brief, URL map, QA evidence register, issue register, developer handoff, launch
  assessment, monitoring plan.
- `assets/synthetic-examples/`: a fictional store's migration inputs with planted problems.
- `scripts/migration_checks.py`: the deterministic checks.
