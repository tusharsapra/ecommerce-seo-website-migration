"""Tests for migration_checks.py and the skill's files. The redirect tests run against a local HTTP server, so
no real site is contacted.

    python3 -m unittest discover -s tests -v
"""
import contextlib
import csv
import http.server
import io
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SKILL = os.path.join(REPO, "skills", "ecommerce-seo-website-migration")
EX = os.path.join(SKILL, "assets", "synthetic-examples")
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import migration_checks as mc  # noqa: E402


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = mc.main([str(a) for a in argv])
    return code, buf.getvalue()


def ex(name):
    return os.path.join(EX, name)


# ---------------------------------------------------------------- a local site to test redirects against

def page(lang="en", canonical="", robots=""):
    head = '<link rel="canonical" href="%s">' % canonical if canonical else ""
    if robots:
        head += '<meta name="robots" content="%s">' % robots
    return ('<!doctype html><html lang="%s"><head><title>T</title>%s</head><body>ok</body></html>' % (
        lang, head)).encode()


ROUTES = {
    "/old-a": (301, "/new-a", None, {}),
    "/new-a": (200, None, ("en", "SELF", ""), {}),
    "/new-a/": (200, None, ("en", "SELF", ""), {}),
    "/old-temp": (302, "/new-a", None, {}),
    "/old-chain": (301, "/mid", None, {}),
    "/mid": (301, "/new-a", None, {}),
    "/loop1": (301, "/loop2", None, {}),
    "/loop2": (301, "/loop1", None, {}),
    "/old-de": (301, "/de-page", None, {}),
    "/de-page": (200, None, ("de", "SELF", ""), {}),
    "/still-live": (200, None, ("en", "SELF", ""), {}),
    "/gone": (410, None, None, {}),
    "/old-noindex": (301, "/noindex", None, {}),
    "/noindex": (200, None, ("en", "SELF", "noindex"), {}),
    "/old-canon": (301, "/canon-other", None, {}),
    "/canon-other": (200, None, ("en", "/new-a", ""), {}),
    "/removed-home": (301, "/", None, {}),
    "/": (200, None, ("en", "SELF", ""), {}),
    "/retained": (200, None, ("en", "SELF", ""), {}),
    "/old-xr": (301, "/xr", None, {}),
    "/xr": (200, None, ("en", "SELF", ""), {"X-Robots-Tag": "noindex"}),
    "/old-slash": (301, "/new-a/", None, {}),
    "/old-500": (301, "/err", None, {}),
    "/err": (500, None, None, {}),
}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        route = ROUTES.get(self.path)
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        status, loc, html, headers = route
        self.send_response(status)
        if loc:
            self.send_header("Location", loc)
        for k, v in headers.items():
            self.send_header(k, v)
        body = b""
        if html:
            lang, canon, robots = html
            base = "http://%s:%d" % self.server.server_address
            canon = base + self.path if canon == "SELF" else (base + canon if canon else "")
            body = page(lang, canon, robots)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class Live(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def grade(self, path, disposition, dest=None, **extra):
        row = {"old_url": self.base + path, "disposition": disposition,
               "destination_url": (self.base + dest) if dest else "", "page_type": "product", "locale": "en"}
        row.update(extra)
        t = mc.trace(row["old_url"], timeout=5, max_hops=5)
        return mc.evaluate(row, t)

    def test_a_clean_permanent_redirect_passes(self):
        state, problems = self.grade("/old-a", "redirect", "/new-a")
        self.assertEqual(state, "passed", problems)

    def test_redirect_failures_are_named(self):
        cases = [
            ("/old-temp", "redirect", "/new-a", "temporary 302"),
            ("/old-chain", "redirect", "/new-a", "a chain of 2 redirects"),
            ("/loop1", "redirect", "/new-a", "redirect loop"),
            ("/still-live", "redirect", "/new-a", "a page still lives there"),
            ("/old-noindex", "redirect", "/noindex", "noindex"),
            ("/old-canon", "redirect", "/canon-other", "canonicalises to"),
            ("/old-xr", "redirect", "/xr", "noindex"),
            ("/old-slash", "redirect", "/new-a", "trailing slash"),
            ("/old-500", "redirect", "/err", "returns 500"),
        ]
        for path, disp, dest, want in cases:
            state, problems = self.grade(path, disp, dest)
            self.assertEqual(state, "failed", path)
            self.assertIn(want, " ".join(problems), path)

    def test_a_200_in_the_wrong_language_fails(self):
        state, problems = self.grade("/old-de", "redirect", "/de-page", destination_locale="en")
        self.assertEqual(state, "failed")
        self.assertIn("in de, expected en", " ".join(problems))

    def test_removals_and_retained_urls(self):
        self.assertEqual(self.grade("/gone", "remove")[0], "passed")
        state, problems = self.grade("/removed-home", "remove")
        self.assertEqual(state, "failed")
        self.assertIn("homepage", " ".join(problems))
        self.assertEqual(self.grade("/still-live", "remove")[0], "failed")
        self.assertEqual(self.grade("/retained", "retain")[0], "passed")
        self.assertEqual(self.grade("/old-a", "retain")[0], "failed")
        self.assertEqual(self.grade("/old-a", "investigate")[0], "not_tested")

    def test_network_failures_are_blocked_not_failed(self):
        row = {"old_url": "http://127.0.0.1:9/nothing-listens-here", "disposition": "redirect",
               "destination_url": self.base + "/new-a"}
        state, problems = mc.evaluate(row, mc.trace(row["old_url"], timeout=2, max_hops=3))
        self.assertEqual(state, "blocked")

    def test_the_redirects_command_writes_results_and_respects_the_limit(self):
        tmp = tempfile.mkdtemp(prefix="mig-test-")
        try:
            m = os.path.join(tmp, "map.csv")
            with open(m, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["old_url", "priority", "disposition", "destination_url", "page_type"])
                w.writerow([self.base + "/old-a", "critical", "redirect", self.base + "/new-a", "product"])
                w.writerow([self.base + "/old-temp", "high", "redirect", self.base + "/new-a", "product"])
                w.writerow([self.base + "/gone", "standard", "remove", "", "product"])
                w.writerow([self.base + "/x", "critical", "investigate", "", "product"])
            out = os.path.join(tmp, "results.csv")
            code, text = run("redirects", m, "--rate", 0, "--timeout", 5, "--out", out)
            self.assertEqual(code, 0, text)
            self.assertIn("passed 2", text)
            self.assertIn("failed 1", text)
            self.assertIn("not_tested 1", text)
            with open(out, encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual([r["evidence_state"] for r in rows], ["passed", "failed", "passed", "not_tested"])
            self.assertIn("[301]", rows[0]["hops_seen"])
            code, text = run("redirects", m, "--rate", 0, "--limit", 1, "--json")
            data = json.loads(text)
            self.assertEqual(data["tested"], 1)
            self.assertEqual(data["not_run_over_limit"], 3)
            code, text = run("redirects", m, "--rate", 0, "--priority", "critical", "--json")
            self.assertEqual(json.loads(text)["tested"], 2)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- offline checks on the synthetic examples

class MapCheck(unittest.TestCase):
    def test_the_example_map_finds_every_planted_problem(self):
        res = mc.check_map(mc.load_map(ex("url-map.csv")), mc.load_crawl(ex("crawl-new.csv")))
        checks = {f["check"] for f in res["findings"]}
        for want in ("loop", "chain", "conflicting decisions", "destination not 200", "homepage destination",
                     "unapproved fuzzy match", "missing disposition", "locale mismatch", "critical not approved",
                     "many-to-one without rationale", "open decision", "destination not indexable"):
            self.assertIn(want, checks)
        self.assertEqual(res["findings"][0]["severity"], "critical")
        # a chain's intermediate destination is reported once, as a chain, not also as 'not crawled'
        chain = [f for f in res["findings"] if "1003-trail-stove" in f["old_url"] and "v2" not in f["old_url"]]
        self.assertEqual([f["check"] for f in chain], ["chain"])

    def test_small_cases(self):
        rows = [{"old_url": "https://a.example/x", "disposition": "redirect", "destination_url": "https://a.example/x",
                 "_line": 2, "priority": ""},
                {"old_url": "https://a.example/y", "disposition": "remove", "destination_url": "https://a.example/z",
                 "_line": 3, "priority": ""},
                {"old_url": "https://a.example/w", "disposition": "moved", "destination_url": "", "_line": 4,
                 "priority": ""},
                {"old_url": "https://a.example/v", "disposition": "redirect", "destination_url": "", "_line": 5,
                 "priority": "critical"}]
        checks = {f["check"] for f in mc.check_map(rows)["findings"]}
        self.assertTrue({"self redirect", "remove with destination", "invalid disposition",
                         "missing destination"} <= checks)

    def test_a_hosting_move_with_unchanged_urls_raises_nothing(self):
        rows = [{"old_url": "https://a.example/p/%d" % i, "disposition": "retain",
                 "destination_url": "https://a.example/p/%d" % i, "_line": i + 2, "priority": "high"}
                for i in range(5)]
        self.assertEqual(mc.check_map(rows)["findings"], [])


class Links(unittest.TestCase):
    def test_the_example_links(self):
        f = mc.check_links(mc.read_rows(ex("links-export.csv")), "store.example", ["old-store.example"],
                           ["staging.store.example"])
        kinds = {x["kind"] for x in f}
        for want in ("duplicated host", "old host", "staging or preview host", "document-relative link",
                     "not crawlable", "insecure protocol", "broken link", "link to a redirect"):
            self.assertIn(want, kinds)
        dup = [x for x in f if x["kind"] == "duplicated host"][0]
        self.assertEqual(dup["location"], "product description")

    def test_ordinary_links_pass_and_previews_are_caught(self):
        rows = [{"source_url": "https://store.example/a", "link_url": u} for u in (
            "/products/x", "https://store.example/products/y", "//store.example/z", "mailto:hi@store.example",
            "tel:+10000000000", "#top")]
        self.assertEqual(mc.check_links(rows, "store.example"), [])
        rows = [{"source_url": "https://store.example/a", "link_url": "https://invented-store-0000.myshopify.com/x"},
                {"source_url": "https://store.example/a", "link_url": "/https://store.example/x"}]
        kinds = [x["kind"] for x in mc.check_links(rows, "store.example")]
        self.assertEqual(sorted(kinds), ["duplicated host", "staging or preview host"])


class Hreflang(unittest.TestCase):
    def test_the_example_annotations(self):
        res = mc.check_hreflang(mc.read_rows(ex("hreflang-export.csv")), mc.load_crawl(ex("crawl-new.csv")))
        checks = {f["check"] for f in res["findings"]}
        for want in ("missing return link", "invalid region", "relative alternate", "missing self-reference"):
            self.assertIn(want, checks)

    def test_a_valid_cluster_only_notes_x_default(self):
        rows = []
        for page in ("https://s.example/", "https://s.example/de/"):
            for code, alt in (("en", "https://s.example/"), ("de", "https://s.example/de/")):
                rows.append({"page_url": page, "hreflang": code, "alternate_url": alt})
        res = mc.check_hreflang(rows)
        self.assertEqual({f["severity"] for f in res["findings"]}, {"info"})
        rows.append({"page_url": "https://s.example/", "hreflang": "x-default", "alternate_url": "https://s.example/"})
        rows.append({"page_url": "https://s.example/de/", "hreflang": "x-default",
                     "alternate_url": "https://s.example/"})
        self.assertEqual(mc.check_hreflang(rows)["findings"], [])


class CrawlDiffAndPerformance(unittest.TestCase):
    def test_crawl_diff_labels_introduced_and_existing(self):
        res = mc.crawl_diff(mc.load_crawl(ex("crawl-old.csv")), mc.load_crawl(ex("crawl-new.csv")),
                            mc.load_map(ex("url-map.csv")))
        fields = {(f["field"], f["label"]) for f in res["findings"]}
        for want in (("canonical", "introduced"), ("status", "introduced"), ("indexability", "introduced"),
                     ("content", "introduced"), ("indexability", "existing")):
            self.assertIn(want, fields)
        self.assertEqual(res["chained_skipped"], 3)
        self.assertEqual(res["conflicting_sources"], ["https://old-store.example/p/1005-rain-shell"])
        staging = [f for f in res["findings"] if f["field"] == "canonical"][0]
        self.assertIn("staging", staging["detail"])

    def test_performance_groups_old_and_new_urls(self):
        res = mc.performance(mc.perf_rows(ex("gsc-before.csv")), mc.perf_rows(ex("gsc-after.csv")),
                             mc.load_map(ex("url-map.csv")))
        g = {r["group"]: r for r in res["groups"]}
        tent = g["https://store.example/products/alpine-tent-2p"]
        self.assertEqual(tent["after"]["clicks"], 800)        # the new URL plus the old URL still showing
        self.assertAlmostEqual(tent["clicks_change_pct"], -2.439, places=2)
        self.assertAlmostEqual(g["https://store.example/products/rain-shell"]["clicks_change_pct"], -76.83, places=1)
        self.assertIn("(unmapped after URLs)", g)
        # position is weighted by impressions: (6.4 x 20,500 + 7.0 x 1,300) / 21,800
        self.assertAlmostEqual(tent["after"]["position"], (6.4 * 20500 + 7.0 * 1300) / 21800, places=6)

    def test_cli_output(self):
        for args in (("map", ex("url-map.csv"), "--new-crawl", ex("crawl-new.csv")),
                     ("crawl-diff", ex("crawl-old.csv"), ex("crawl-new.csv"), "--map", ex("url-map.csv")),
                     ("links", ex("links-export.csv"), "--host", "store.example"),
                     ("hreflang", ex("hreflang-export.csv")),
                     ("performance", ex("gsc-before.csv"), ex("gsc-after.csv"), "--map", ex("url-map.csv"))):
            code, out = run(*args)
            self.assertEqual(code, 0, out)
            self.assertTrue(out.startswith("# "), args[0])
            code, out = run(*(args + ("--json",)))
            json.loads(out)
        code, out = run("map", ex("crawl-new.csv"))
        self.assertNotEqual(code, 0)
        self.assertIn("no old_url column", out)


class Helpers(unittest.TestCase):
    def test_url_comparison_is_strict_but_explains_near_misses(self):
        self.assertTrue(mc.same_url("https://S.example/a?b=1#x", "https://s.example/a?b=1"))
        self.assertFalse(mc.same_url("https://s.example/a/", "https://s.example/a"))
        self.assertFalse(mc.same_url("https://s.example/A", "https://s.example/a"))
        self.assertEqual(mc.near_miss("https://s.example/a/", "https://s.example/a"), "differs only by a trailing slash")
        self.assertEqual(mc.near_miss("https://s.example/A", "https://s.example/a"), "differs only by letter case")
        self.assertIn("different host", mc.near_miss("https://www.s.example/a", "https://s.example/a"))
        self.assertIn("different protocol", mc.near_miss("http://s.example/a", "https://s.example/a"))

    def test_rows_with_extra_cells_are_tolerated(self):
        tmp = tempfile.mkdtemp(prefix="mig-test-")
        try:
            p = os.path.join(tmp, "c.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("Address,Status Code,Meta Robots 1\nhttps://s.example/a,200,index,follow\n")
            rows = mc.read_rows(p)
            self.assertEqual(rows[0]["address"], "https://s.example/a")
            self.assertEqual(rows[0]["_extra"], "follow")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Files(unittest.TestCase):
    def test_skill_frontmatter_follows_the_agent_skills_spec(self):
        text = read(os.path.join(SKILL, "SKILL.md"))
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(m)
        keys, fields, cur = [], {}, None
        for line in m.group(1).splitlines():
            km = re.match(r"^([a-z][a-z-]*):\s*(.*)$", line)
            if km:
                cur = km.group(1)
                keys.append(cur)
                fields[cur] = km.group(2)
            elif cur:
                fields[cur] += " " + line.strip()
        self.assertTrue(set(keys) <= {"name", "description", "license", "compatibility", "metadata",
                                      "allowed-tools"}, keys)
        name = fields["name"].strip()
        self.assertEqual(name, os.path.basename(SKILL))
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        desc = fields["description"].replace(">-", "").strip()
        self.assertTrue(0 < len(desc) <= 1024, len(desc))
        self.assertLessEqual(len(fields.get("compatibility", "").strip()), 500)
        self.assertLess(len(text.splitlines()), 500)

    def test_every_file_skill_md_names_exists(self):
        text = read(os.path.join(SKILL, "SKILL.md"))
        for rel in sorted(set(re.findall(r"`((?:references|assets|scripts)/[A-Za-z0-9_./-]+)`", text))):
            self.assertTrue(os.path.exists(os.path.join(SKILL, rel)), rel)

    def test_every_cited_source_is_in_the_register(self):
        register = read(os.path.join(SKILL, "references", "sources.md"))
        listed = set(re.findall(r"^\| (S\d+) \|", register, re.M))
        self.assertEqual(listed, {"S%d" % i for i in range(1, 13)})
        for name in os.listdir(os.path.join(SKILL, "references")):
            for cited in re.findall(r"\[(S\d+)\]", read(os.path.join(SKILL, "references", name))):
                self.assertIn(cited, listed, (name, cited))

    def test_templates_and_examples_line_up(self):
        header = read(os.path.join(SKILL, "assets", "templates", "url-map.csv")).splitlines()[0].split(",")
        for col in ("old_url", "page_type", "locale", "stable_id", "priority", "disposition", "destination_url",
                    "rationale", "match_method", "approval_state", "evidence_state"):
            self.assertIn(col, header)
        self.assertEqual(read(ex("url-map.csv")).splitlines()[0].split(","), header)
        issues = read(os.path.join(SKILL, "assets", "templates", "issue-register.csv")).splitlines()[0].split(",")
        for col in ("affected_urls", "impact", "evidence", "proposed_fix", "owner", "dependency", "retest_condition",
                    "label"):
            self.assertIn(col, issues)
        qa = read(os.path.join(SKILL, "assets", "templates", "qa-evidence-register.csv"))
        self.assertIn("evidence_state", qa)

    def test_examples_use_only_reserved_domains(self):
        for name in os.listdir(EX):
            for host in re.findall(r"https?://([a-z0-9.-]+)", read(ex(name)).lower()):
                self.assertTrue(host.endswith(".example") or host == "example", (name, host))
        self.assertRegex(read(ex("README.md")).lower(), r"invented|synthetic|fictional")


if __name__ == "__main__":
    unittest.main()
