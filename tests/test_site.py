"""Dependency-free checks for the complete static AXIOM site."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGE_PATHS = (
    Path("index.html"),
    Path("systems/index.html"),
    Path("research/index.html"),
    Path("engineering/index.html"),
    Path("contact/index.html"),
)
NAV_LABELS = ("Systems", "Research", "Engineering", "Contact")
REPOSITORIES = {
    "axiom-apex", "axiom-api", "axiom-ason", "axiom-blender", "axiom-demos",
    "axiom-infra", "axiom-ops", "axiom-rag", "axiom-research",
}
TECHNOLOGIES = {
    "Python", "Bash", "Linux", "Agent orchestration", "MCP", "RAG",
    "Gemini", "Ollama", "SQLite", "ChromaDB", "Pydantic", "Flask",
    "REST / HTTP", "Git", "GitHub Actions", "Docker / Compose", "Twilio",
    "Blender",
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.elements = []
        self.text = []
        self.links = []
        self.headings = []
        self._link = None
        self._heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "a":
            self._link = [attrs, []]
            self.links.append(self._link)
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = [int(tag[1]), []]
            self.headings.append(self._heading)

    def handle_endtag(self, tag):
        if tag == "a":
            self._link = None
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = None

    def handle_data(self, data):
        self.text.append(data)
        if self._link is not None:
            self._link[1].append(data)
        if self._heading is not None:
            self._heading[1].append(data)

    @property
    def content(self):
        return " ".join("".join(self.text).split())


def parse(path):
    page = Page(path)
    page.feed((ROOT / path).read_text())
    return page


def local_target(page_path, value):
    url = urlsplit(value)
    if url.scheme or url.netloc:
        return None, url.fragment
    raw_path = url.path or page_path.name
    target = (ROOT / page_path.parent / raw_path).resolve()
    if target.is_dir():
        target /= "index.html"
    return target, url.fragment


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {path: parse(path) for path in PAGE_PATHS}
        cls.styles = (ROOT / "styles.css").read_text()

    def test_required_pages_are_the_complete_public_architecture(self):
        self.assertEqual(set(self.pages), set(PAGE_PATHS))
        for path in PAGE_PATHS:
            self.assertTrue((ROOT / path).is_file())
        self.assertFalse((ROOT / "systems" / "apex").exists())

    def test_every_local_page_asset_and_anchor_resolves(self):
        for path, page in self.pages.items():
            ids = [attrs["id"] for _, attrs in page.elements if "id" in attrs]
            self.assertEqual(len(ids), len(set(ids)), path)
            for _, attrs in page.elements:
                for key in ("href", "src"):
                    if key not in attrs:
                        continue
                    target, fragment = local_target(path, attrs[key])
                    if target is None:
                        continue
                    self.assertTrue(target.is_file(), f"{path}: {attrs[key]}")
                    if fragment:
                        current = (ROOT / path).resolve()
                        target_page = page if target == current else parse(target.relative_to(ROOT))
                        target_ids = {a["id"] for _, a in target_page.elements if "id" in a}
                        self.assertIn(fragment, target_ids, f"{path}: {attrs[key]}")

    def test_shared_navigation_is_compact_and_coherent(self):
        for path, page in self.pages.items():
            navs = [attrs for tag, attrs in page.elements if tag == "nav"]
            self.assertEqual(navs, [{"aria-label": "Main navigation"}], path)
            nav_links = [(" ".join("".join(text).split()), attrs) for attrs, text in page.links if " ".join("".join(text).split()) in NAV_LABELS]
            self.assertEqual(tuple(label for label, _ in nav_links), NAV_LABELS, path)
            if path != Path("index.html"):
                current = [label for label, attrs in nav_links if attrs.get("aria-current") == "page"]
                self.assertEqual(current, [path.parts[0].title()], path)

    def test_semantic_and_accessible_structure(self):
        for path, page in self.pages.items():
            tags = [tag for tag, _ in page.elements]
            self.assertEqual(tags.count("h1"), 1, path)
            self.assertEqual(tags.count("main"), 1, path)
            self.assertGreaterEqual(tags.count("header"), 1, path)
            self.assertEqual(tags.count("footer"), 1, path)
            self.assertNotIn("script", tags, path)
            self.assertEqual(page.headings[0][0], 1, path)
            for previous, current in zip(page.headings, page.headings[1:]):
                self.assertLessEqual(current[0] - previous[0], 1, path)
            ids = {attrs["id"] for _, attrs in page.elements if "id" in attrs}
            for _, attrs in page.elements:
                if "aria-labelledby" in attrs:
                    self.assertIn(attrs["aria-labelledby"], ids, path)
            skip = [attrs.get("href") for attrs, text in page.links if "".join(text).strip() == "Skip to content"]
            self.assertEqual(skip, ["#main"], path)
            for tag, attrs in page.elements:
                if tag == "img":
                    self.assertIn("alt", attrs, f"{path}: {attrs}")
                    self.assertIn("width", attrs, f"{path}: {attrs}")
                    self.assertIn("height", attrs, f"{path}: {attrs}")
        self.assertIn("a:focus-visible", self.styles)

    def test_contact_paths_remain_valid_and_consistent(self):
        contact = self.pages[Path("contact/index.html")]
        hrefs = [attrs.get("href") for attrs, _ in contact.links]
        self.assertIn("mailto:axiom.co@proton.me", hrefs)
        self.assertEqual([href for href in hrefs if href and href.startswith("tel:")], ["tel:+16094030646"])
        self.assertIn("(609) 403-0646", contact.content)
        numbers = re.findall(r"\(\d{3}\) \d{3}-\d{4}", (ROOT / "README.md").read_text())
        self.assertEqual(numbers, ["(609) 403-0646"])

    def test_external_repository_links_are_expected(self):
        found = set()
        for page in self.pages.values():
            for attrs, _ in page.links:
                match = re.match(r"https://github\.com/axiom-llc/([^/#?]+)", attrs.get("href", ""))
                if match:
                    found.add(match.group(1))
        self.assertEqual(found, REPOSITORIES)
        all_html = "\n".join((ROOT / path).read_text() for path in PAGE_PATHS)
        self.assertNotIn("axiom-director", all_html)

    def test_complete_stack_lives_only_on_engineering(self):
        engineering = self.pages[Path("engineering/index.html")].content
        for name in TECHNOLOGIES:
            self.assertIn(name, engineering)
        for path, page in self.pages.items():
            if path != Path("engineering/index.html"):
                self.assertNotIn("Complete engineering technology stack", page.content)
        sources = [attrs["src"] for tag, attrs in self.pages[Path("engineering/index.html")].elements if tag == "img" and "technology/" in attrs.get("src", "")]
        self.assertEqual(len(sources), len(set(sources)))
        self.assertEqual(len(sources), 11)

    def test_static_runtime_has_no_external_or_active_assets(self):
        for path, page in self.pages.items():
            for tag, attrs in page.elements:
                if tag == "link" and "href" in attrs:
                    self.assertFalse(urlsplit(attrs["href"]).scheme, f"{path}: {attrs['href']}")
                if tag in {"img", "script", "iframe", "audio", "video", "source"} and "src" in attrs:
                    self.assertFalse(urlsplit(attrs["src"]).scheme, f"{path}: {attrs['src']}")
        self.assertNotRegex(self.styles, r"url\(['\"]?https?://")

    def test_local_variable_fonts_and_licenses(self):
        expected = {
            "InterVariable.woff2": "Inter",
            "IBMPlexMonoVariable.woff2": "IBM Plex Mono",
        }
        for filename, family in expected.items():
            path = ROOT / "assets/fonts" / filename
            self.assertTrue(path.is_file(), filename)
            self.assertEqual(path.read_bytes()[:4], b"wOF2", filename)
            self.assertIn(f'font-family: "{family}"', self.styles)
            self.assertIn(f'url("assets/fonts/{filename}")', self.styles)
        self.assertEqual(self.styles.count("font-display: swap"), 2)
        for filename in ("LICENSE-Inter.txt", "LICENSE-IBM-Plex.txt"):
            license_text = (ROOT / "assets/fonts" / filename).read_text()
            self.assertIn("SIL OPEN FONT LICENSE Version 1.1", license_text)
        provenance = (ROOT / "assets/fonts/SOURCES.md").read_text()
        for filename in (*expected, "LICENSE-Inter.txt", "LICENSE-IBM-Plex.txt"):
            self.assertIn(f"`{filename}`", provenance)
        for value in re.findall(r"url\([\"']?([^\"')]+)", self.styles):
            self.assertFalse(urlsplit(value).scheme, value)
            self.assertTrue((ROOT / value).is_file(), value)

    def test_svg_assets_are_valid_and_documented(self):
        sources = (ROOT / "assets/technology/SOURCES.md").read_text()
        for asset in sorted((ROOT / "assets/technology").glob("*")):
            if asset.suffix == ".svg":
                tree = ET.parse(asset)
                self.assertNotIn("<!DOCTYPE", asset.read_text())
                for element in tree.iter():
                    for name, value in element.attrib.items():
                        if name.endswith("href"):
                            self.assertFalse(urlsplit(value).scheme, f"{asset}: {value}")
            if asset.suffix in {".svg", ".png"}:
                self.assertIn(f"`{asset.name}`", sources)

    def test_visual_system_and_responsive_guards(self):
        for value in ("#0d0f12", "#14181c", "#191e23", "#f4f1e9", "#aab0b4", "#91c4d6", "#b9dce8", "#2a3036", "#20262c"):
            self.assertIn(value, self.styles)
        for unwanted in ("linear-gradient", "radial-gradient", "backdrop-filter", "box-shadow", "border-radius", "@keyframes"):
            self.assertNotIn(unwanted, self.styles)
        self.assertIn("@media (max-width: 900px)", self.styles)
        self.assertIn("@media (max-width: 640px)", self.styles)
        self.assertRegex(self.styles, r"@media \(max-width: 640px\)[\s\S]*?\.core-grid \{ grid-template-columns: 1fr;")
        self.assertRegex(self.styles, r"@media \(max-width: 640px\)[\s\S]*?\.stack \{ grid-template-columns: 1fr;")
        self.assertNotIn("-webkit-font-smoothing", self.styles)
        self.assertNotIn("text-shadow", self.styles)
        self.assertIn("font-synthesis: none", self.styles)

    def test_exact_homepage_hero_and_editorial_rejections(self):
        home = self.pages[Path("index.html")]
        hero = " ".join("".join(home.headings[0][1]).split())
        self.assertEqual(hero, "Intelligence, with structure.")
        source = (ROOT / "index.html").read_text()
        self.assertRegex(source, r'with <span class="hero-accent">structure</span>\.')
        all_content = " ".join(page.content for page in self.pages.values())
        for rejected in (
            "Bring the difficult system.",
            "Software decides what runs.",
            "What should the system do?",
            "Boundaries before capabilities.",
            "Reliability is a boundary discipline.",
            "Reproducibility over ceremony.",
            "Intelligence, given structure.",
        ):
            self.assertNotIn(rejected, all_content)

    def test_claim_boundaries_are_explicit(self):
        all_content = " ".join(page.content for page in self.pages.values()).lower()
        for required in ("does not establish exactly-once external effects", "not independent assurance", "not certification", "does not imply a production deployment"):
            self.assertIn(required, all_content)
        for unsupported in ("production-ready", "enterprise-grade", "fully secure", "independently verified", "guaranteed accuracy"):
            self.assertNotIn(unsupported, all_content)
        self.assertIn("model output is treated as a proposal", all_content)
        self.assertNotIn("deterministic model", all_content)

    def test_obsolete_single_page_navigation_is_removed(self):
        for page in self.pages.values():
            hrefs = [attrs.get("href", "") for attrs, _ in page.links]
            self.assertNotIn("#capabilities", hrefs)
            self.assertNotIn("#systems", hrefs)
            self.assertNotIn("#contact", hrefs)


if __name__ == "__main__":
    unittest.main()
