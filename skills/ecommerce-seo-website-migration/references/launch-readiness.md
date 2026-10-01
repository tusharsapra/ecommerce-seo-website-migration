# Launch coordination and readiness

## Before cutover

Prepare and confirm:

- approved URL decisions, with the destinations verified on staging;
- a content freeze, and the final export and delta process for changes made during the freeze;
- the redirect activation steps and their owner;
- production indexing controls and sitemap checks (staging controls removed, production ones correct);
- availability, certificate and host checks for every host variant;
- measurement smoke checks;
- incident contacts, backups and recovery procedures.

## The readiness assessment

| State | Meaning |
| --- | --- |
| Ready | The required checks passed, with current evidence |
| Ready with recorded exceptions | The remaining issues have explicit owners and an accepted treatment |
| Blocked | Critical defects, or gaps in evidence, prevent a reliable readiness recommendation |

Typical blockers: priority destinations that are not accessible, staging canonicals across templates, unintended
indexing restrictions, failed priority redirects, and loss of important content.

Missing evidence for priority pages is not a pass. If a critical check is `not_tested` or `blocked`, the
assessment cannot be "Ready".

Readiness is a recommendation. It does not authorise production changes on its own; the launch decision belongs
to the named owner. Use `assets/templates/launch-assessment.md`.

## Recovery planning

Identify the reversible actions and their dependencies before launch. A DNS reversal is not a complete rollback
when orders, content, redirects or other systems have changed in the meantime; say what a rollback would and
would not restore.

## Immediately after cutover (launch QA)

Run, against production:

1. Availability and certificates on every host variant; the old host reaches the redirects.
2. The priority redirects: status, hops, final URL, locale and indexability (`scripts/migration_checks.py
   redirects`).
3. Indexing controls: robots.txt, meta robots and X-Robots-Tag on each template; staging controls gone.
4. Canonicals on each template point at production URLs.
5. Sitemaps list the new production URLs and are reachable.
6. Measurement smoke checks: page views, e-commerce events, a test order where the process allows it.
7. A sample of internal links and migrated content per template.

Record each check with its evidence state and time. Anything failing on a priority page goes straight into the
issue register with an owner and a retest condition.

## The developer handoff

Use `assets/templates/developer-handoff.md` and `assets/templates/issue-register.csv`. Each item says what to
change, where, why it matters, how to verify it (the retest condition), who owns it and what it depends on.
Record excluded fields and areas, unresolved issues and their owners, so nothing falls between assignments.
