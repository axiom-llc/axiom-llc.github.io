"""Validate public search metadata, entity identity and discovery boundaries."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://axiom-llc.github.io"
PAGES = {
    "index.html": "/",
    "director/index.html": "/director/",
    "systems/index.html": "/systems/",
    "research/index.html": "/research/",
    "engineering/index.html": "/engineering/",
    "contact/index.html": "/contact/",
    "engagements/index.html": "/engagements/",
    "engagements/reliability-control-sprint/index.html": "/engagements/reliability-control-sprint/",
    "case-studies/index.html": "/case-studies/",
}

class Head(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta = {}
        self.canonicals = []
        self.graphs = []
        self.ld = None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name", ""))] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.ld = []
    def handle_data(self, data):
        if self.ld is not None:
            self.ld.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.ld is not None:
            self.graphs.append(json.loads("".join(self.ld)))
            self.ld = None

class SearchTests(unittest.TestCase):
    def test_each_public_route_has_one_matching_canonical_and_share_url(self):
        for path, route in PAGES.items():
            with self.subTest(path=path):
                head = Head((ROOT / path).read_text())
                self.assertEqual(head.canonicals, [BASE + route])
                self.assertEqual(head.meta.get("og:url"), BASE + route)
                self.assertTrue(head.meta.get("og:title"))
                self.assertEqual(head.meta.get("og:description"), head.meta.get("description"))
                self.assertEqual(head.meta.get("twitter:card"), "summary_large_image")
                image = head.meta.get("og:image", "")
                self.assertEqual(urlsplit(image).netloc, "axiom-llc.github.io")
                self.assertTrue(head.meta.get("og:image:alt"))
    def test_json_ld_links_each_page_to_the_same_public_publisher(self):
        for path, route in PAGES.items():
            with self.subTest(path=path):
                head = Head((ROOT / path).read_text())
                self.assertEqual(len(head.graphs), 1)
                data = head.graphs[0]
                self.assertEqual(data["@context"], "https://schema.org")
                nodes = data["@graph"]
                ids = [node["@id"] for node in nodes]
                self.assertEqual(len(ids), len(set(ids)))
                page = next(n for n in nodes if n.get("@type") == "WebPage")
                self.assertEqual(page["url"], BASE + route)
                self.assertEqual(page["publisher"]["@id"], BASE + "/#organization")
                self.assertEqual(page["isPartOf"]["@id"], BASE + "/#website")
                if route != "/":
                    crumbs = next(n for n in nodes if n.get("@type") == "BreadcrumbList")
                    items = crumbs["itemListElement"]
                    self.assertEqual(items[0]["item"], BASE + "/")
                    self.assertEqual(items[-1]["item"], BASE + route)
                    self.assertEqual([n["position"] for n in items], list(range(1, len(items) + 1)))
    def test_publisher_uses_public_business_identity_without_private_records(self):
        head = Head((ROOT / "index.html").read_text())
        self.assertTrue(head.graphs)
        org = next(n for n in head.graphs[0]["@graph"] if n.get("@type") == "Organization")
        self.assertEqual(org["name"], "AXIOM LLC")
        self.assertEqual(org["sameAs"], ["https://github.com/axiom-llc"])
        self.assertEqual(org["email"], "axiom.co@proton.me")
        self.assertNotIn("address", org)
        for path in PAGES:
            head = Head((ROOT / path).read_text())
            self.assertNotRegex(json.dumps(head.graphs), r"axiom-(?:director|health-ops|narcissism|housing|ocbss)(?:/|\u0022)")
    def test_sitemap_covers_real_public_pages_without_private_or_duplicate_urls(self):
        path = ROOT / "sitemap.xml"
        self.assertTrue(path.is_file())
        tree = ET.parse(path)
        urls = [n.text for n in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertCountEqual(urls, [BASE + route for route in PAGES.values()])
        self.assertEqual(len(urls), len(set(urls)))
    def test_robots_allows_public_discovery_and_points_to_sitemap(self):
        path = ROOT / "robots.txt"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertIn("User-agent: *", text)
        self.assertIn("Allow: /", text)
        self.assertIn("Sitemap: https://axiom-llc.github.io/sitemap.xml", text)
        self.assertNotIn("Disallow: /", text)
    def test_evidence_intros_keep_the_three_column_layout_contract(self):
        for path in ("director/index.html", "case-studies/index.html"):
            text = (ROOT / path).read_text()
            for body in re.findall(r'<div class="section-intro">([\\s\\S]*?)</div>', text):
                children = re.findall(r'<(?:p|h2)(?:\\s|>)', body)
                self.assertLessEqual(len(children), 3, path)
                self.assertTrue(body.lstrip().startswith('<p class="eyebrow">'), path)

    def test_service_schema_describes_the_visible_sprint_without_invented_ratings(self):
        head = Head((ROOT / "engagements/reliability-control-sprint/index.html").read_text())
        self.assertTrue(head.graphs)
        service = next(n for n in head.graphs[0]["@graph"] if n.get("@type") == "Service")
        self.assertEqual(service["provider"]["@id"], BASE + "/#organization")
        self.assertIn("Reliability", service["name"])
        self.assertNotIn("aggregateRating", service)
        self.assertNotIn("review", service)

if __name__ == "__main__":
    unittest.main()
