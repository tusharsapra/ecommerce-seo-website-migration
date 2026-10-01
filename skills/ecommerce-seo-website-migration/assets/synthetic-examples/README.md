# Synthetic examples

Everything here is invented: Trailhead Supply, its reserved `.example` domains, its products, URLs and numbers.
The files exist to show the inputs the skill works with and to exercise `scripts/migration_checks.py`. Each one
has planted problems.

| File | What is planted |
| --- | --- |
| `brief.md` | A combined domain, platform and URL-structure migration with two locales |
| `url-map.csv` | An unapproved slug match to a different variant, a collection sent to the homepage, a consolidation without a rationale, a chain, a loop, conflicting rows for one source, a missing decision, a German page sent to an English destination, a critical decision not yet approved |
| `crawl-old.csv`, `crawl-new.csv` | A staging canonical with noindex and a missing H1, a destination returning 404, a large content drop, a page that was already noindex before (existing, not introduced) |
| `links-export.csv` | A duplicated hostname, an old-host link, a staging link, a preview-host link, a document-relative link, a javascript: link, an http link |
| `hreflang-export.csv` | A missing return link, an invalid `en-uk`, a relative alternate, a page without a self-reference |
| `gsc-before.csv`, `gsc-after.csv` | Mapped page groups that held, one that collapsed (a collection sent to the homepage), and an unmapped new URL |

Try, from this folder:

```bash
S=../../scripts/migration_checks.py
python3 $S map url-map.csv --new-crawl crawl-new.csv
python3 $S crawl-diff crawl-old.csv crawl-new.csv --map url-map.csv
python3 $S links links-export.csv --host store.example --old-host old-store.example --staging-host staging.store.example
python3 $S hreflang hreflang-export.csv --crawl crawl-new.csv
python3 $S performance gsc-before.csv gsc-after.csv --map url-map.csv
```

`redirects` needs live URLs, so it is not run on these reserved domains; the tests run it against a local server.
