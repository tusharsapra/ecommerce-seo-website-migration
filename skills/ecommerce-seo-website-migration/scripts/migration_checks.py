#!/usr/bin/env python3
"""migration_checks.py: deterministic checks for an e-commerce website migration.

    python3 migration_checks.py map URL_MAP.csv [--new-crawl CRAWL.csv]
    python3 migration_checks.py redirects URL_MAP.csv [--priority critical,high] [--limit 200] [--rate 2]
                                         [--timeout 10] [--max-hops 10] [--out results.csv]
    python3 migration_checks.py links LINKS.csv --host store.example [--old-host old.example] [--staging-host s.example]
    python3 migration_checks.py hreflang ANNOTATIONS.csv [--crawl CRAWL.csv]
    python3 migration_checks.py crawl-diff OLD_CRAWL.csv NEW_CRAWL.csv --map URL_MAP.csv
    python3 migration_checks.py performance BEFORE.csv AFTER.csv --map URL_MAP.csv

Every check ends in one evidence state: passed | failed | not_tested | not_applicable | blocked. Network
failures are blocked, never failed and never passed. Inputs are read, never modified; the only file written is
the one named with --out. Every command takes --json.

`redirects` makes live HTTP requests: run it only against sites you own or are authorised to test. It is
bounded (--limit), rate-limited (--rate requests per second), times out (--timeout) and never follows more than
--max-hops redirects.

Python 3.8+, standard library only.
"""
import argparse
import csv
import html.parser
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

STATES = ("passed", "failed", "not_tested", "not_applicable", "blocked")
DISPOSITIONS = ("retain", "redirect", "consolidate", "remove", "investigate")
FUZZY_METHODS = ("slug", "name", "fuzzy", "similarity", "string", "title")
PERMANENT = (301, 308)
TEMPORARY = (302, 303, 307)
USER_AGENT = "migration-checks/1.0 (+bounded SEO migration QA; contact the site owner)"


class CheckError(Exception):
    pass


# ---------------------------------------------------------------- reading inputs

def read_rows(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        sample = fh.read(8192)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(fh, dialect=dialect)
        rows = []
        for r in reader:
            row = {}
            for k, v in r.items():
                if k is None:  # more cells than headers: an unquoted comma; keep them, flagged
                    row["_extra"] = ",".join(x for x in (v or []) if x)
                    continue
                row[re.sub(r"\s+", " ", k.strip().lower())] = v.strip() if isinstance(v, str) else ""
            rows.append(row)
    return rows


def pick(row, *names):
    for n in names:
        if n in row and row[n] != "":
            return row[n]
    return ""


URL_COLS = ("old_url", "address", "url", "page", "landing page", "top pages", "source url")


def load_map(path):
    rows = read_rows(path)
    if not rows:
        raise CheckError("%s has no rows" % path)
    if "old_url" not in rows[0]:
        raise CheckError("%s has no old_url column; use assets/templates/url-map.csv" % path)
    for i, r in enumerate(rows, start=2):
        r["_line"] = i
        r["disposition"] = r.get("disposition", "").lower()
        r["priority"] = r.get("priority", "").lower()
    return rows


def load_crawl(path):
    """{url: {status, indexable, canonical, title, h1, words, robots}} from a crawler export."""
    out = {}
    for r in read_rows(path):
        url = pick(r, "address", "url", "page", "final_url", "new_url")
        if not url:
            continue
        status = pick(r, "status code", "status_code", "status", "http status")
        robots = pick(r, "meta robots 1", "meta robots", "robots", "x-robots-tag 1", "x-robots-tag")
        indexable = pick(r, "indexability", "indexable")
        if indexable:
            idx = indexable.lower() in ("indexable", "true", "yes", "1")
        elif robots:
            idx = "noindex" not in robots.lower()
        else:
            idx = None
        out[url] = {"status": status, "indexable": idx, "robots": robots,
                    "canonical": pick(r, "canonical link element 1", "canonical", "canonical url", "canonical_url"),
                    "title": pick(r, "title 1", "title", "page title"),
                    "h1": pick(r, "h1-1", "h1", "h1 1"),
                    "words": pick(r, "word count", "words", "word_count"),
                    "structured_data": pick(r, "structured data", "schema", "structured_data")}
    return out


# ---------------------------------------------------------------- url helpers

def split(url):
    p = urllib.parse.urlsplit(url)
    return p.scheme.lower(), p.netloc.lower(), p.path, p.query


def same_url(a, b):
    """Same URL, ignoring only scheme and host case and the fragment. Paths, trailing slashes, case and
    queries are compared exactly: they are meaningful until shown otherwise."""
    if not a or not b:
        return False
    return split(a) == split(b)


def near_miss(a, b):
    """Why two URLs differ when they almost match, or ''."""
    sa, sb = split(a), split(b)
    if sa == sb:
        return ""
    if sa[1] != sb[1] and sa[2:] == sb[2:]:
        return "different host (%s vs %s)" % (sa[1], sb[1])
    if sa[0] != sb[0] and sa[1:] == sb[1:]:
        return "different protocol (%s vs %s)" % (sa[0], sb[0])
    if sa[:2] == sb[:2] and sa[3] == sb[3] and sa[2].rstrip("/") == sb[2].rstrip("/"):
        return "differs only by a trailing slash"
    if sa[:2] == sb[:2] and sa[3] == sb[3] and sa[2].lower() == sb[2].lower():
        return "differs only by letter case"
    if sa[:3] == sb[:3] and sa[3] != sb[3]:
        return "different query string"
    return ""


def is_home(url):
    return split(url)[2] in ("", "/") and not split(url)[3]


def locale_of_path(url):
    m = re.match(r"^/([a-z]{2}(?:-[a-zA-Z]{2})?)(?:/|$)", split(url)[2])
    return m.group(1).lower() if m else ""


# ---------------------------------------------------------------- map

def check_map(rows, crawl=None):
    findings = []

    def add(sev, row, code, text):
        findings.append({"severity": sev, "line": row["_line"] if row else None,
                         "old_url": row.get("old_url", "") if row else "", "check": code, "detail": text})
    by_source = {}
    for r in rows:
        by_source.setdefault(r["old_url"], []).append(r)
    for src, rs in by_source.items():
        if len(rs) > 1:
            decisions = {(x["disposition"], x.get("destination_url", "")) for x in rs}
            if len(decisions) > 1:
                add("critical", rs[0], "conflicting decisions", "%d rows give %s different decisions: %s" % (
                    len(rs), len(decisions), "; ".join("%s -> %s" % (d or "?", u or "-") for d, u in sorted(decisions))))
            else:
                add("standard", rs[0], "duplicate row", "%d identical rows for this source" % len(rs))
    sources = {r["old_url"]: r for r in rows}
    dest_count = {}
    for r in rows:
        d, dest = r["disposition"], r.get("destination_url", "")
        if not r["old_url"]:
            add("high", r, "missing source", "row has no old_url")
            continue
        if not d:
            add("high", r, "missing disposition", "no decision recorded")
            continue
        if d not in DISPOSITIONS:
            add("high", r, "invalid disposition", "'%s' is not one of %s" % (d, ", ".join(DISPOSITIONS)))
            continue
        if d in ("redirect", "consolidate"):
            if not dest:
                add("critical" if r["priority"] == "critical" else "high", r, "missing destination",
                    "%s with no destination_url" % d)
                continue
            if same_url(dest, r["old_url"]):
                add("high", r, "self redirect", "destination is the source itself")
            dest_count.setdefault(dest, []).append(r)
            if is_home(dest) and r.get("page_type", "").lower() not in ("home", "homepage"):
                add("high", r, "homepage destination", "a %s page sent to the homepage; check a relevant "
                    "destination exists, or record a removal" % (r.get("page_type") or "non-home"))
            nxt = sources.get(dest)
            if nxt and nxt["disposition"] in ("redirect", "consolidate") and nxt.get("destination_url"):
                seen, cur, hops = {r["old_url"]}, dest, 1
                while cur in sources and sources[cur]["disposition"] in ("redirect", "consolidate") and \
                        sources[cur].get("destination_url") and hops < 50:
                    if cur in seen:
                        break
                    seen.add(cur)
                    cur = sources[cur]["destination_url"]
                    hops += 1
                if cur in seen or cur == r["old_url"]:
                    add("critical", r, "loop", "the map sends this URL round in a loop")
                else:
                    add("high", r, "chain", "the destination is itself redirected: %d hops to %s. Point the "
                        "source straight at the final URL" % (hops, cur))
            dl, sl = r.get("destination_locale", "").lower(), r.get("locale", "").lower()
            dpath = locale_of_path(dest)
            if sl and dl and sl.split("-")[0] != dl.split("-")[0]:
                add("high", r, "locale mismatch", "source locale %s, destination locale %s" % (sl, dl))
            elif sl and not dl and dpath and dpath.split("-")[0] != sl.split("-")[0]:
                add("high", r, "locale mismatch", "source locale %s, destination path looks like /%s/" % (sl, dpath))
            if crawl is not None and not (nxt and nxt["disposition"] in ("redirect", "consolidate")):
                c = crawl.get(dest)
                if c is None:
                    add("high", r, "destination not crawled", "the destination is not in the new crawl")
                else:
                    if c["status"] and not c["status"].startswith("2"):
                        add("critical" if r["priority"] in ("critical", "high") else "high", r,
                            "destination not 200", "the destination returns %s in the new crawl" % c["status"])
                    if c["indexable"] is False:
                        add("high", r, "destination not indexable", "the destination is not indexable (%s)" % (
                            c["robots"] or "per the crawl"))
        elif d == "remove" and dest:
            add("standard", r, "remove with destination", "marked remove but has a destination; is it a redirect?")
        elif d == "retain" and dest and not same_url(dest, r["old_url"]):
            add("standard", r, "retain with other destination", "marked retain but points somewhere else")
        method = r.get("match_method", "").lower()
        approval = r.get("approval_state", "").lower()
        if any(m in method for m in FUZZY_METHODS) and approval not in ("approved", "yes", "true"):
            add("high", r, "unapproved fuzzy match", "matched by %s and not approved: a similar name can be a "
                "different variant, language or intent" % method)
        if r["priority"] == "critical" and d in ("redirect", "consolidate", "remove") and \
                approval not in ("approved", "yes", "true"):
            add("high", r, "critical not approved", "a critical URL's decision is not approved yet")
        if d == "investigate":
            add("standard", r, "open decision", "still to investigate")
    for dest, rs in dest_count.items():
        if len(rs) > 1:
            missing = [x for x in rs if not x.get("rationale")]
            if missing:
                add("standard", missing[0], "many-to-one without rationale", "%d sources consolidate into %s and "
                    "%d have no rationale; check the destination serves each one's intent" % (
                        len(rs), dest, len(missing)))
    counts = {}
    for r in rows:
        counts[r["disposition"] or "(none)"] = counts.get(r["disposition"] or "(none)", 0) + 1
    rank = {"critical": 0, "high": 1, "standard": 2}
    findings.sort(key=lambda f: (rank[f["severity"]], f["line"] or 0))
    return {"rows": len(rows), "sources": len(by_source), "dispositions": counts, "findings": findings,
            "many_to_one": {d: len(rs) for d, rs in dest_count.items() if len(rs) > 1}}


# ---------------------------------------------------------------- redirects (live)

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _Head(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = ""
        self.robots = ""
        self.lang = ""
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split() and not self.canonical:
            self.canonical = a.get("href", "")
        elif tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot"):
            self.robots = (self.robots + "," + a.get("content", "")).strip(",")
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and len(self.title) < 300:
            self.title += data


def fetch(url, timeout):
    """One request, no redirect following. Returns (status, headers, body_head) or raises."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        resp = opener.open(req, timeout=timeout)
        body = resp.read(512 * 1024)
        return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as e:
        try:
            body = e.read(64 * 1024)
        except Exception:  # some servers close early
            body = b""
        return e.code, dict(e.headers or {}), body


def trace(url, timeout=10, max_hops=10, pause=0.0):
    """Follow redirects by hand. Returns {hops: [(url, status, location)], final_url, final_status, headers,
    head, error, loop}."""
    hops, seen, cur = [], set(), url
    out = {"hops": hops, "final_url": "", "final_status": None, "headers": {}, "head": None, "error": "",
           "loop": False}
    for _ in range(max_hops + 1):
        if cur in seen:
            out["loop"] = True
            out["final_url"] = cur
            return out
        seen.add(cur)
        try:
            status, headers, body = fetch(cur, timeout)
        except Exception as e:  # network, DNS, TLS, timeout: not a website defect we can confirm
            out["error"] = "%s: %s" % (type(e).__name__, e)
            out["final_url"] = cur
            return out
        loc = {k.lower(): v for k, v in headers.items()}.get("location", "")
        hops.append((cur, status, loc))
        if pause:
            time.sleep(pause)
        if 300 <= status < 400 and loc:
            cur = urllib.parse.urljoin(cur, loc)
            continue
        out["final_url"], out["final_status"], out["headers"] = cur, status, headers
        h = _Head()
        try:
            h.feed(body.decode("utf-8", errors="replace"))
        except Exception:
            pass
        out["head"] = {"canonical": urllib.parse.urljoin(cur, h.canonical) if h.canonical else "",
                       "robots": h.robots, "lang": h.lang, "title": h.title.strip()}
        return out
    out["error"] = "more than %d redirects" % max_hops
    out["final_url"] = cur
    return out


def evaluate(row, t):
    """(state, problems) for one map row against its trace."""
    d = row["disposition"]
    dest = row.get("destination_url", "")
    if d == "investigate" or not d:
        return "not_tested", ["no decision to test"]
    if d not in ("redirect", "consolidate", "retain", "remove"):
        return "not_tested", ["unrecognised disposition: %s" % d]
    if t["error"] and not t["hops"]:
        return "blocked", ["could not reach the source: %s" % t["error"]]
    problems = []
    if t["loop"]:
        return "failed", ["redirect loop: %s" % " -> ".join(h[0] for h in t["hops"])]
    if t["error"]:
        return "blocked", ["stopped after %d hop(s): %s" % (len(t["hops"]), t["error"])]
    first = t["hops"][0][1] if t["hops"] else None
    n_redirects = sum(1 for h in t["hops"] if 300 <= h[1] < 400)
    head = t["head"] or {}
    hdrs = {k.lower(): v for k, v in (t["headers"] or {}).items()}
    robots = ",".join(x for x in (head.get("robots", ""), hdrs.get("x-robots-tag", "")) if x).lower()
    if d in ("redirect", "consolidate"):
        if first in TEMPORARY:
            problems.append("first hop is a temporary %d, not a permanent redirect" % first)
        elif first not in PERMANENT:
            problems.append("the source answered %s instead of redirecting%s" % (
                first, " (a page still lives there)" if first and 200 <= first < 300 else ""))
        if n_redirects > 1:
            problems.append("a chain of %d redirects; point the source straight at the final URL" % n_redirects)
        if t["final_status"] != 200:
            problems.append("the final URL returns %s" % t["final_status"])
        if dest and not same_url(t["final_url"], dest):
            why = near_miss(t["final_url"], dest)
            problems.append("ends at %s, expected %s%s" % (t["final_url"], dest, (" (%s)" % why) if why else ""))
        if "noindex" in robots:
            problems.append("the destination is noindex (%s)" % robots)
        canon = head.get("canonical", "")
        if canon and not same_url(canon, t["final_url"]):
            problems.append("the destination canonicalises to %s" % canon)
        want = (row.get("destination_locale") or row.get("locale") or "").lower()
        lang = (head.get("lang") or "").lower()
        if want and lang and want.split("-")[0] != lang.split("-")[0]:
            problems.append("the destination is in %s, expected %s" % (lang, want))
        if is_home(t["final_url"]) and row.get("page_type", "").lower() not in ("home", "homepage"):
            problems.append("ends on the homepage")
    elif d == "retain":
        if n_redirects:
            problems.append("a retained URL redirects (%d hop(s)) to %s" % (n_redirects, t["final_url"]))
        if t["final_status"] != 200:
            problems.append("returns %s" % t["final_status"])
        if "noindex" in robots:
            problems.append("noindex (%s)" % robots)
        canon = head.get("canonical", "")
        if canon and not same_url(canon, t["final_url"]):
            problems.append("canonicalises to %s" % canon)
    elif d == "remove":
        if first in (404, 410):
            pass
        elif first and 200 <= first < 300:
            problems.append("a removed URL still returns %d" % first)
        elif n_redirects and is_home(t["final_url"]):
            problems.append("a removed URL redirects to the homepage; return 404 or 410, or record a relevant "
                            "redirect instead")
        elif n_redirects:
            problems.append("marked remove but redirects to %s; update the map if that is intended" % t["final_url"])
        else:
            problems.append("returns %s" % first)
    return ("failed" if problems else "passed"), problems


def cmd_redirects(args):
    rows = load_map(args.map)
    pri = {p.strip().lower() for p in (args.priority or "").split(",") if p.strip()}
    todo = [r for r in rows if r["old_url"] and (not pri or r["priority"] in pri)]
    skipped = max(0, len(todo) - args.limit)
    todo = todo[:args.limit]
    pause = 1.0 / args.rate if args.rate > 0 else 0.0
    results = []
    for r in todo:
        if r["disposition"] in ("", "investigate"):
            results.append(dict(r, evidence_state="not_tested", problems="no decision to test", hops_seen="",
                                actual_final_url="", final_status=""))
            continue
        t = trace(r["old_url"], args.timeout, args.max_hops, pause)
        state, problems = evaluate(r, t)
        results.append(dict(r, evidence_state=state, problems="; ".join(problems),
                            hops_seen=" -> ".join("%s [%s]" % (h[0], h[1]) for h in t["hops"]),
                            actual_final_url=t["final_url"], final_status=t["final_status"] or "",
                            tested_at=time.strftime("%Y-%m-%d %H:%M:%S")))
    counts = {s: sum(1 for x in results if x["evidence_state"] == s) for s in STATES}
    if args.out:
        cols = [c for c in (rows[0].keys()) if not c.startswith("_")]
        extra = ["evidence_state", "problems", "hops_seen", "actual_final_url", "final_status", "tested_at"]
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols + [c for c in extra if c not in cols], extrasaction="ignore")
            w.writeheader()
            for x in results:
                w.writerow({k: x.get(k, "") for k in cols + extra})
    if args.json:
        print(json.dumps({"tested": len(results), "not_run_over_limit": skipped, "counts": counts,
                          "results": [{k: v for k, v in x.items() if not k.startswith("_")} for x in results]},
                         indent=1, default=str))
        return 0
    print("# Redirect check")
    print("")
    print("%d URL(s) checked%s, at most %s request(s) a second, timeout %ss, max %d hops." % (
        len(results), (" (%d more over --limit, not run)" % skipped) if skipped else "", args.rate, args.timeout,
        args.max_hops))
    print("")
    print(" | ".join("%s %d" % (s, counts[s]) for s in STATES))
    print("")
    for state in ("failed", "blocked", "not_tested"):
        sel = [x for x in results if x["evidence_state"] == state]
        if not sel:
            continue
        print("## %s" % state)
        for x in sel:
            print("- %s [%s, %s]: %s" % (x["old_url"], x.get("priority") or "-", x["disposition"] or "-",
                                         x["problems"]))
            if x.get("hops_seen"):
                print("  hops: %s" % x["hops_seen"])
        print("")
    print("Blocked means the check could not run (network, DNS, TLS, timeout): it is neither a pass nor a "
          "confirmed defect. Retest with a clean client: browsers cache redirects.")
    if args.out:
        print("Results written to %s" % args.out)
    return 0


# ---------------------------------------------------------------- links

def check_links(rows, host, old_hosts=(), staging_hosts=()):
    host = host.lower()
    findings = []
    for r in rows:
        src = pick(r, "source_url", "source", "from", "page", "address")
        raw = pick(r, "link_url", "link", "href", "destination", "to", "target")
        where = pick(r, "location", "link position", "field", "context", "element")
        status = pick(r, "status_code", "status code", "status")
        if not raw:
            continue

        def add(kind, sev, detail):
            findings.append({"source_url": src, "link": raw, "location": where, "kind": kind, "severity": sev,
                             "detail": detail})
        low = raw.lower().strip()
        if low.startswith(("javascript:", "#")) or low in ("", "about:blank"):
            if low.startswith("javascript:"):
                add("not crawlable", "high", "a javascript: link is not a crawlable link")
            continue
        if low.startswith(("mailto:", "tel:", "sms:")):
            continue
        if re.search(r"https?:/{1,2}[^/\s]+/+https?:/", low) or re.search(r"^/+https?:/", low) or \
                re.search(r"https?://[^/]+/[^\s]*%s/" % re.escape(host), low):
            add("duplicated host", "high", "a hostname was prepended to an already absolute URL")
            continue
        if " " in raw.strip() or "\t" in raw:
            add("unencoded whitespace", "standard", "the link contains whitespace")
        resolved = urllib.parse.urljoin(src or ("https://%s/" % host), raw.strip())
        p = urllib.parse.urlsplit(resolved)
        h = p.netloc.lower()
        if any(h == o or h.endswith("." + o) for o in old_hosts if o):
            add("old host", "high", "links to the old host %s; link the new canonical URL directly" % h)
        elif any(h == s or h.endswith("." + s) for s in staging_hosts if s) or "staging" in h or \
                h.startswith(("dev.", "test.")) or h.endswith(".myshopify.com") or h in ("localhost",) or \
                h.startswith("127."):
            add("staging or preview host", "high", "links to %s" % h)
        elif h == host and p.scheme == "http":
            add("insecure protocol", "standard", "http link on the site's own host")
        if not re.match(r"^[a-z][a-z0-9+.-]*:|^/|^//", raw.strip(), re.I) and src:
            add("document-relative link", "standard", "resolves under the source's directory to %s; check that "
                "is intended" % resolved)
        if status:
            if status.startswith(("4", "5")):
                add("broken link", "high", "the link returns %s" % status)
            elif status.startswith("3"):
                add("link to a redirect", "standard", "the link returns %s; link the final URL directly" % status)
    rank = {"high": 0, "standard": 1}
    findings.sort(key=lambda f: (rank[f["severity"]], f["kind"], f["source_url"]))
    return findings


# ---------------------------------------------------------------- hreflang

HREFLANG_RE = re.compile(r"^(x-default|[a-z]{2,3}(-[a-z]{4})?(-([a-z]{2}|\d{3}))?)$", re.I)


def check_hreflang(rows, crawl=None):
    ann = {}
    findings = []

    def add(sev, page, code, detail):
        findings.append({"severity": sev, "page_url": page, "check": code, "detail": detail})
    for r in rows:
        page = pick(r, "page_url", "url", "address", "source_url")
        code = pick(r, "hreflang", "language", "lang", "code")
        alt = pick(r, "alternate_url", "href", "alternate", "target_url")
        if not page or not code:
            continue
        ann.setdefault(page, {}).setdefault(code.lower(), set()).add(alt)
    for page, codes in ann.items():
        for code, alts in codes.items():
            if not HREFLANG_RE.match(code):
                add("high", page, "invalid code", "'%s' is not a valid language or language-region code" % code)
            elif code.endswith("-uk"):
                add("high", page, "invalid region", "'%s': UK is not a region code; the United Kingdom is GB, "
                    "e.g. en-GB" % code)
            elif code == "uk" or code.startswith("uk-"):
                add("standard", page, "check code", "'%s' means Ukrainian; if the United Kingdom was meant, use "
                    "en-GB" % code)
            if len(alts) > 1:
                add("high", page, "conflicting alternates", "%s points to %d URLs: %s" % (
                    code, len(alts), ", ".join(sorted(alts))))
            for a in alts:
                if not re.match(r"^https?://", a or "", re.I):
                    add("high", page, "relative alternate", "%s -> '%s' is not an absolute URL" % (code, a))
        all_alts = {a for alts in codes.values() for a in alts}
        if not any(same_url(a, page) for a in all_alts):
            add("high", page, "missing self-reference", "the page does not list itself")
        for code, alts in codes.items():
            for a in alts:
                if same_url(a, page) or not a:
                    continue
                back = ann.get(a)
                if back is None:
                    tgt = None
                    for k in ann:
                        if same_url(k, a):
                            tgt = ann[k]
                    back = tgt
                if back is None:
                    add("high", page, "alternate not annotated", "%s (%s) has no hreflang annotations of its own "
                        "in the export" % (a, code))
                elif not any(same_url(x, page) for xs in back.values() for x in xs):
                    add("high", page, "missing return link", "%s (%s) does not link back" % (a, code))
                if crawl is not None:
                    c = crawl.get(a)
                    if c is None:
                        add("standard", page, "alternate not crawled", "%s is not in the crawl" % a)
                    elif c["status"] and not c["status"].startswith("2"):
                        add("high", page, "alternate not 200", "%s returns %s" % (a, c["status"]))
                    elif c["canonical"] and not same_url(c["canonical"], a):
                        add("high", page, "alternate canonicalises elsewhere", "%s canonicalises to %s" % (
                            a, c["canonical"]))
        if "x-default" not in codes:
            add("info", page, "no x-default", "no x-default in this cluster (optional)")
    rank = {"high": 0, "standard": 1, "info": 2}
    findings.sort(key=lambda f: (rank[f["severity"]], f["check"], f["page_url"]))
    return {"pages": len(ann), "findings": findings}


# ---------------------------------------------------------------- crawl diff

def decisive_rows(rows):
    """One row per source: the approved one if any, else the first. Returns (rows, sources with conflicts)."""
    first, conflicts = {}, set()
    for r in rows:
        src = r["old_url"]
        if src not in first:
            first[src] = r
            continue
        if (r["disposition"], r.get("destination_url")) != (first[src]["disposition"],
                                                             first[src].get("destination_url")):
            conflicts.add(src)
        approved = lambda x: x.get("approval_state", "").lower() in ("approved", "yes", "true")
        if approved(r) and not approved(first[src]):
            first[src] = r
    return [first[k] for k in first], sorted(conflicts)


def crawl_diff(old, new, rows):
    rows, conflicts = decisive_rows(rows)
    redirected = {r["old_url"] for r in rows if r["disposition"] in ("redirect", "consolidate")}
    pairs, findings, chained = [], [], 0
    for r in rows:
        d = r["disposition"]
        if r.get("destination_url") in redirected:
            chained += 1
            continue
        if d in ("redirect", "consolidate") and r.get("destination_url"):
            pairs.append((r, r["old_url"], r["destination_url"]))
        elif d == "retain":
            pairs.append((r, r["old_url"], r.get("destination_url") or r["old_url"]))
    by_type = {}
    for r, o, n in pairs:
        pt = r.get("page_type") or "unknown"
        bt = by_type.setdefault(pt, {"pairs": 0, "missing_old": 0, "missing_new": 0, "changed": {}})
        bt["pairs"] += 1
        a, b = old.get(o), new.get(n)
        if a is None:
            bt["missing_old"] += 1
        if b is None:
            bt["missing_new"] += 1
            findings.append({"severity": "high", "old_url": o, "new_url": n, "field": "crawl",
                             "detail": "the new URL is not in the new crawl", "label": "unknown"})
            continue
        if a is None:
            continue

        def changed(field, sev, detail):
            bt["changed"][field] = bt["changed"].get(field, 0) + 1
            findings.append({"severity": sev, "old_url": o, "new_url": n, "field": field, "detail": detail,
                             "label": "introduced"})
        if b["status"] and not b["status"].startswith("2"):
            changed("status", "critical" if r["priority"] in ("critical", "high") else "high",
                    "old %s, new %s" % (a["status"] or "?", b["status"]))
        if a["indexable"] is not False and b["indexable"] is False:
            changed("indexability", "critical" if r["priority"] in ("critical", "high") else "high",
                    "indexable before, not indexable now (%s)" % (b["robots"] or "per the crawl"))
        if a["indexable"] is False and b["indexable"] is False:
            findings.append({"severity": "standard", "old_url": o, "new_url": n, "field": "indexability",
                             "detail": "not indexable before or after", "label": "existing"})
        if b["canonical"] and not same_url(b["canonical"], n):
            changed("canonical", "high", "the new page canonicalises to %s" % b["canonical"])
        if a["title"] and not b["title"]:
            changed("title", "high", "title missing on the new page")
        elif a["title"] and b["title"] and a["title"].strip().lower() != b["title"].strip().lower():
            changed("title", "standard", "'%s' -> '%s'" % (a["title"][:70], b["title"][:70]))
        if a["h1"] and not b["h1"]:
            changed("h1", "high", "H1 missing on the new page")
        try:
            wa = float((a["words"] or "nan").replace(",", ""))
            wb = float((b["words"] or "nan").replace(",", ""))
            if wa > 0 and wb == wb and wb < wa * 0.6:
                changed("content", "high", "word count fell from %d to %d" % (wa, wb))
        except ValueError:
            pass
        if a["structured_data"] and not b["structured_data"]:
            changed("structured data", "high", "structured data found before, not now")
    rank = {"critical": 0, "high": 1, "standard": 2}
    findings.sort(key=lambda f: (rank[f["severity"]], f["field"], f["old_url"]))
    return {"pairs": len(pairs), "by_page_type": by_type, "findings": findings, "chained_skipped": chained,
            "conflicting_sources": conflicts}


# ---------------------------------------------------------------- performance

def perf_rows(path):
    out = {}
    for r in read_rows(path):
        url = pick(r, "page", "top pages", "landing page", "url", "address", "landing page + query string")
        if not url:
            continue
        rec = out.setdefault(url, {"clicks": 0.0, "impressions": 0.0, "pos_x_impr": 0.0, "has_pos": False,
                                   "sessions": 0.0, "conversions": 0.0, "revenue": 0.0})
        for key, names in (("clicks", ("clicks", "url clicks")), ("impressions", ("impressions",)),
                           ("sessions", ("sessions", "visits", "users")),
                           ("conversions", ("conversions", "key events", "transactions", "orders", "purchases")),
                           ("revenue", ("revenue", "purchase revenue", "total revenue"))):
            v = pick(r, *names)
            try:
                rec[key] += float(v.replace(",", "")) if v else 0.0
            except ValueError:
                pass
        pos = pick(r, "position", "average position")
        try:
            if pos:
                imp = float(pick(r, "impressions").replace(",", "") or 0)
                rec["pos_x_impr"] += float(pos) * imp
                rec["has_pos"] = True
        except ValueError:
            pass
    return out


def performance(before, after, rows):
    rows, conflicts = decisive_rows(rows)
    group_of, page_type = {}, {}
    for r in rows:
        d = r["disposition"]
        key = r.get("destination_url") if d in ("redirect", "consolidate") and r.get("destination_url") \
            else r["old_url"]
        group_of[r["old_url"]] = key
        group_of.setdefault(key, key)
        page_type[key] = r.get("page_type") or page_type.get(key) or "unknown"
    groups = {}

    for period, data in (("before", before), ("after", after)):
        for url, rec in data.items():
            g = group_of.get(url) or "(unmapped %s URLs)" % period
            gg = groups.setdefault(g, {"before": None, "after": None, "urls": set(),
                                       "page_type": page_type.get(g, "unmapped")})
            gg["urls"].add(url)
            cur = gg[period] or {"clicks": 0.0, "impressions": 0.0, "pos_x_impr": 0.0, "pos_impr": 0.0,
                                 "sessions": 0.0, "conversions": 0.0, "revenue": 0.0}
            for k in ("clicks", "impressions", "sessions", "conversions", "revenue"):
                cur[k] += rec[k]
            if rec["has_pos"]:
                cur["pos_x_impr"] += rec["pos_x_impr"]
                cur["pos_impr"] += rec["impressions"]
            gg[period] = cur
    out = []
    for g, v in groups.items():
        row = {"group": g, "page_type": v["page_type"], "urls": len(v["urls"])}
        for period in ("before", "after"):
            p = v[period]
            row[period] = None if p is None else {
                "clicks": p["clicks"], "impressions": p["impressions"], "sessions": p["sessions"],
                "conversions": p["conversions"], "revenue": p["revenue"],
                "ctr": (100.0 * p["clicks"] / p["impressions"]) if p["impressions"] else None,
                "position": (p["pos_x_impr"] / p["pos_impr"]) if p["pos_impr"] else None}
        b = (row["before"] or {}).get("clicks")
        a = (row["after"] or {}).get("clicks")
        row["clicks_change_pct"] = (100.0 * (a - b) / b) if b and a is not None else None
        out.append(row)
    out.sort(key=lambda r: -((r["before"] or {}).get("clicks") or 0))
    by_type = {}
    for r in out:
        t = by_type.setdefault(r["page_type"], {"before": 0.0, "after": 0.0, "groups": 0})
        t["groups"] += 1
        t["before"] += (r["before"] or {}).get("clicks") or 0
        t["after"] += (r["after"] or {}).get("clicks") or 0
    return {"groups": out, "by_page_type": by_type, "conflicting_sources": conflicts}


# ---------------------------------------------------------------- command wrappers and output

def _print_findings(title, findings, keys):
    print("## %s" % title)
    if not findings:
        print("- none")
    for f in findings:
        print("- [%s] %s" % (f["severity"], " | ".join(str(f.get(k, "")) for k in keys if f.get(k, "") != "")))
    print("")


def cmd_map(args):
    rows = load_map(args.map)
    crawl = load_crawl(args.new_crawl) if args.new_crawl else None
    res = check_map(rows, crawl)
    if args.json:
        print(json.dumps(res, indent=1))
        return 0
    print("# URL map check")
    print("")
    print("%d rows, %d distinct sources. Decisions: %s." % (res["rows"], res["sources"], ", ".join(
        "%s %d" % (k, v) for k, v in sorted(res["dispositions"].items()))))
    if res["many_to_one"]:
        print("Many-to-one destinations: %d (each needs a rationale that covers every source's intent)." %
              len(res["many_to_one"]))
    if crawl is None:
        print("No --new-crawl given: destinations were not checked against the new site (not_tested).")
    print("")
    _print_findings("Findings", res["findings"], ("line", "old_url", "check", "detail"))
    print("This checks the decisions in the map. It does not prove the live site does what the map says: run "
          "`redirects` for that.")
    return 0


def cmd_links(args):
    findings = check_links(read_rows(args.links), args.host, [h.lower() for h in args.old_host or []],
                           [h.lower() for h in args.staging_host or []])
    if args.json:
        print(json.dumps(findings, indent=1))
        return 0
    kinds = {}
    for f in findings:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    print("# Link check")
    print("")
    print("%d finding(s): %s." % (len(findings), ", ".join("%s %d" % kv for kv in sorted(kinds.items())) or "none"))
    print("")
    _print_findings("Findings", findings, ("source_url", "location", "link", "kind", "detail"))
    print("Findings come from parsing the exported links. Where the export has no status column, broken-link and "
          "redirect checks are not_tested. Stored content and app components may hold links a crawl did not see.")
    return 0


def cmd_hreflang(args):
    res = check_hreflang(read_rows(args.annotations), load_crawl(args.crawl) if args.crawl else None)
    if args.json:
        print(json.dumps(res, indent=1))
        return 0
    print("# Hreflang check")
    print("")
    print("%d annotated page(s)." % res["pages"])
    print("")
    _print_findings("Findings", res["findings"], ("page_url", "check", "detail"))
    print("This checks the annotations, not whether the content is a genuine translation for that market.")
    return 0


def cmd_crawl_diff(args):
    res = crawl_diff(load_crawl(args.old), load_crawl(args.new), load_map(args.map))
    if args.json:
        print(json.dumps(res, indent=1))
        return 0
    print("# Old and new crawl, by mapped pair")
    print("")
    print("%d mapped pair(s).%s%s" % (res["pairs"], (" %d pair(s) whose destination is itself redirected were "
                                                       "skipped: fix the chain first (see `map`)." %
                                                       res["chained_skipped"]) if res["chained_skipped"] else "",
                                      (" %d source(s) have conflicting rows; the approved row (else the first) was "
                                       "used." % len(res["conflicting_sources"])) if res["conflicting_sources"]
                                      else ""))
    print("")
    print("| page type | pairs | old missing | new missing | changes |")
    print("|---|---|---|---|---|")
    for t, v in sorted(res["by_page_type"].items()):
        print("| %s | %d | %d | %d | %s |" % (t, v["pairs"], v["missing_old"], v["missing_new"],
                                              ", ".join("%s %d" % kv for kv in sorted(v["changed"].items())) or "-"))
    print("")
    _print_findings("Findings", res["findings"], ("old_url", "new_url", "field", "detail", "label"))
    print("'existing' issues were already there before the migration; 'introduced' ones appeared with it. Pairs "
          "missing from the old crawl cannot be labelled.")
    return 0


def _f(x, nd=0):
    return "n/a" if x is None else ("{:,.%df}" % nd).format(x)


def cmd_performance(args):
    res = performance(perf_rows(args.before), perf_rows(args.after), load_map(args.map))
    if args.json:
        print(json.dumps(res, indent=1, default=list))
        return 0
    print("# Performance by mapped page group")
    print("")
    print("Each group is a new URL together with every old URL that maps to it. Compare periods of equal length "
          "with the same filters; before-and-after alone does not prove the cause.")
    if res["conflicting_sources"]:
        print("%d source(s) have conflicting rows in the map; the approved row (else the first) was used: %s" % (
            len(res["conflicting_sources"]), ", ".join(res["conflicting_sources"][:5])))
    print("")
    print("| page type | clicks before | clicks after | change |")
    print("|---|---|---|---|")
    for t, v in sorted(res["by_page_type"].items(), key=lambda kv: -kv[1]["before"]):
        ch = (100.0 * (v["after"] - v["before"]) / v["before"]) if v["before"] else None
        print("| %s | %s | %s | %s |" % (t, _f(v["before"]), _f(v["after"]), (_f(ch, 1) + "%") if ch is not None
                                         else "n/a"))
    print("")
    print("| group | type | URLs | clicks before | clicks after | change | impr before | impr after | "
          "position before | position after |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in res["groups"][:args.top]:
        b, a = r["before"] or {}, r["after"] or {}
        print("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (
            r["group"], r["page_type"], r["urls"], _f(b.get("clicks")), _f(a.get("clicks")),
            (_f(r["clicks_change_pct"], 1) + "%") if r["clicks_change_pct"] is not None else "n/a",
            _f(b.get("impressions")), _f(a.get("impressions")), _f(b.get("position"), 1), _f(a.get("position"), 1)))
    print("")
    print("Position is impression-weighted, never a plain average. Unmapped URLs are grouped separately: if that "
          "group is large, the map is missing pages.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="migration_checks.py", description="Deterministic SEO migration checks.")
    sub = p.add_subparsers(dest="command")
    s = sub.add_parser("map", help="validate a URL decision map")
    s.add_argument("map")
    s.add_argument("--new-crawl", help="a crawl export of the new site, to check destinations")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_map)
    s = sub.add_parser("redirects", help="test the map's redirects live (bounded, rate-limited)")
    s.add_argument("map")
    s.add_argument("--priority", help="only these priorities, e.g. critical,high")
    s.add_argument("--limit", type=int, default=200, help="at most this many URLs (default 200)")
    s.add_argument("--rate", type=float, default=2.0, help="requests per second (default 2)")
    s.add_argument("--timeout", type=float, default=10.0)
    s.add_argument("--max-hops", type=int, default=10)
    s.add_argument("--out", help="write the results as CSV here")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_redirects)
    s = sub.add_parser("links", help="malformed links and stale hosts in a link export")
    s.add_argument("links")
    s.add_argument("--host", required=True, help="the site's production host, e.g. store.example")
    s.add_argument("--old-host", action="append", help="an old host (repeatable)")
    s.add_argument("--staging-host", action="append", help="a staging or preview host (repeatable)")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_links)
    s = sub.add_parser("hreflang", help="hreflang relationships from an annotation export")
    s.add_argument("annotations")
    s.add_argument("--crawl", help="a crawl export, to check that alternates return 200 and self-canonicalise")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_hreflang)
    s = sub.add_parser("crawl-diff", help="compare old and new crawl exports by mapped pair")
    s.add_argument("old")
    s.add_argument("new")
    s.add_argument("--map", required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_crawl_diff)
    s = sub.add_parser("performance", help="compare performance by mapped page group")
    s.add_argument("before")
    s.add_argument("after")
    s.add_argument("--map", required=True)
    s.add_argument("--top", type=int, default=50)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_performance)
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 2
    try:
        return args.func(args)
    except (CheckError, OSError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
