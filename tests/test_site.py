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
    Path("director/index.html"),
    Path("research/index.html"),
    Path("engineering/index.html"),
    Path("contact/index.html"),
    Path("engagements/index.html"),
    Path("engagements/reliability-control-sprint/index.html"),
)
NAV_LABELS = ("Director", "Systems", "Research", "Engineering", "Contact")
REPOSITORIES = {
    "axiom-apex", "axiom-api", "axiom-ason", "axiom-blender", "axiom-demos",
    "axiom-infra", "axiom-rag", "axiom-research",
    "axiom-wiki-infinite",
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
            if path.parts[0] in {"director", "systems", "research", "engineering", "contact"}:
                current = [label for label, attrs in nav_links if attrs.get("aria-current") == "page"]
                self.assertEqual(current, [path.parts[0].title()], path)

    def test_semantic_and_accessible_structure(self):
        for path, page in self.pages.items():
            tags = [tag for tag, _ in page.elements]
            self.assertEqual(tags.count("h1"), 1, path)
            self.assertEqual(tags.count("main"), 1, path)
            self.assertGreaterEqual(tags.count("header"), 1, path)
            self.assertEqual(tags.count("footer"), 1, path)
            scripts = [attrs for tag, attrs in page.elements if tag == "script"]
            self.assertEqual(len(scripts), 2, path)
            self.assertNotIn("src", scripts[0], path)
            self.assertEqual(scripts[1].get("src"), ("../" * len(path.parent.parts)) + "theme.js", path)
            self.assertIn("defer", scripts[1], path)
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

    def test_reliability_sprint_offer_is_fixed_and_bounded(self):
        path = Path("engagements/reliability-control-sprint/index.html")
        page = self.pages[path]
        home = self.pages[Path("index.html")]
        hrefs = [attrs.get("href") for attrs, _ in page.links]
        home_hrefs = [attrs.get("href") for attrs, _ in home.links]
        self.assertIn("engagements/", home_hrefs)
        self.assertIn("mailto:axiom.co@proton.me?subject=Agent%20Reliability%20%26%20Control%20Sprint", hrefs)
        for required in ("5 business days", "$5,000", "up to five", "up to two", "one retrieval subsystem", "one prioritized control patch"):
            self.assertIn(required.lower(), page.content.lower())
        self.assertIn("Executable acceptance tests", page.content)
        self.assertIn("Defined scope", page.content)

    def test_engagement_surface_is_evidence_backed(self):
        page=self.pages[Path("engagements/index.html")].content
        for required in ("Agent reliability & execution control","RAG durability & retrieval engineering","Workflow & systems automation","Architecture, debugging & readiness","Acceptance criteria"):
            self.assertIn(required,page)

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


    def test_migrated_research_artifacts_link_to_current_owners(self):
        hrefs = {attrs.get("href") for attrs, _ in self.pages[Path("research/index.html")].links}
        relocated = {
            "apex-transactional-effects-research.md": "axiom-apex",
            "rag-crash-consistency-architecture.md": "axiom-rag",
            "rag-http-compatibility-contract.md": "axiom-rag",
            "write-file-compensation-readiness.md": "axiom-apex",
            "tacon2026-apex-deterministic-execution-contracts.md": "axiom-apex",
        }
        for filename, owner in relocated.items():
            expected = f"https://github.com/axiom-llc/{owner}/blob/main/research/{filename}"
            obsolete = f"https://github.com/axiom-llc/axiom-research/blob/main/{filename}"
            with self.subTest(filename=filename):
                self.assertIn(expected, hrefs)
                self.assertNotIn(obsolete, hrefs)

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
        for value in ("#edf7ff", "#03090e", "--surface", "--accent", "--muted", "--line"):
            self.assertIn(value, self.styles)
        for required in (':root[data-theme="dark"]', "@media (prefers-color-scheme: dark)", "radial-gradient", "linear-gradient", "@media (max-width: 760px)", ".theme-toggle", ".hero-geometry", ".evidence-panels", ".home-contact-visual"):
            self.assertIn(required, self.styles)
        self.assertIn("-webkit-font-smoothing: antialiased", self.styles)
        self.assertIn("-moz-osx-font-smoothing: grayscale", self.styles)
        self.assertIn("font-optical-sizing: auto", self.styles)
        self.assertIn("font-synthesis: none", self.styles)

    def test_theme_control_and_brand_derivatives_are_shared(self):
        for path, page in self.pages.items():
            buttons = [attrs for tag, attrs in page.elements if tag == "button" and "data-theme-toggle" in attrs]
            self.assertEqual(len(buttons), 1, path)
            links = [attrs for tag, attrs in page.elements if tag == "link"]
            hrefs = {attrs.get("href") for attrs in links}
            prefix = "../" * len(path.parent.parts)
            self.assertIn(prefix + "favicon.svg", hrefs, path)
            self.assertIn(prefix + "assets/brand/axiom-mark-32.png", hrefs, path)
            self.assertIn(prefix + "assets/brand/axiom-mark-180.png", hrefs, path)
            self.assertIn(prefix + "site.webmanifest", hrefs, path)
        for size in (16, 32, 64, 128, 180, 192, 512, 1024):
            self.assertTrue((ROOT / "assets" / "brand" / f"axiom-mark-{size}.png").is_file(), size)
        ET.parse(ROOT / "favicon.svg")
        self.assertTrue((ROOT / "favicon.ico").is_file())
        self.assertTrue((ROOT / "theme.js").is_file())
        theme = (ROOT / "theme.js").read_text()
        for required in ("prefers-color-scheme: dark", "localStorage", "system", "light", "dark"):
            self.assertIn(required, theme)
        for path in PAGE_PATHS:
            source=(ROOT/path).read_text()
            self.assertIn('localStorage.getItem("axiom-theme")',source)
            self.assertLess(source.index('localStorage.getItem("axiom-theme")'),source.index('rel="stylesheet"'))
            for icon in ("system", "light", "dark"):
                self.assertIn(f'class="theme-icon theme-icon-{icon}"', source, path)
                self.assertIn(f'.theme-toggle[data-mode="{icon}"] .theme-icon-{icon}', self.styles)
            self.assertIn('<span data-theme-label>System</span>', source, path)
            self.assertIn('data-theme-toggle data-mode="system"', source, path)
            self.assertNotIn('data-theme-label aria-hidden="true"', source, path)
        self.assertIn('filter: invert(1); mix-blend-mode: multiply;', self.styles)
        self.assertIn(':root[data-theme="light"] .brand img', self.styles)
        self.assertIn(':root:not([data-theme]) .brand img', self.styles)
        self.assertIn('button.dataset.mode = mode', theme)
        self.assertIn('button.setAttribute("aria-label"', theme)
        self.assertIn('mode[0].toUpperCase() + mode.slice(1)', theme)
        self.assertNotIn('label.textContent = mode === "light"', theme)

    def test_editorial_images_are_not_cropped(self):
        """Maintain the source aspect ratio and show the complete illustrated subject."""
        self.assertIn("aspect-ratio: 1672 / 941", self.styles)
        self.assertIn(".evidence-visual img { width: 100%; height: 100%; object-fit: contain; }", self.styles)
        self.assertNotIn("aspect-ratio: 16/7", self.styles)

    def test_asus_dark_mode_and_closing_contact_paths(self):
        source = (ROOT / "index.html").read_text()
        selector = 'img[src$="/asus.svg"] { filter: invert(1); }'
        self.assertEqual(self.styles.count(selector), 2)
        self.assertIn(':root[data-theme="dark"] .ecosystem-logo ' + selector, self.styles)
        self.assertIn(':root:not([data-theme]) .ecosystem-logo ' + selector, self.styles)
        self.assertIn('class="home-contact-main"', source)
        self.assertIn('class="home-contact-visual"', source)
        self.assertIn('class="button" href="contact/"', source)
        self.assertIn('class="quiet-link" href="engagements/"', source)
        self.assertIn('href="mailto:axiom.co@proton.me"', source)

    def test_technology_ecosystem_groups_and_logos(self):
        source = (ROOT / "index.html").read_text()
        home = self.pages[Path("index.html")].content
        expected = {
            "ASUS": "asus.svg",
            "LG Electronics": "lg.svg",
            "Advanced Micro Devices, Inc. (AMD)": "amd.svg",
            "Arch Linux": "arch-linux.svg",
            "Android": "android.svg",
        }
        for name, asset in expected.items():
            self.assertIn(name, home)
            self.assertIn(f"assets/technology/ecosystem/{asset}", source)
            self.assertTrue((ROOT / "assets/technology/ecosystem" / asset).is_file())
        self.assertEqual(source.count('class="ecosystem-card"'), 5)
        self.assertIn("Core hardware and software in the AXIOM engineering environment.", home)
        self.assertIn("Android is a trademark of Google LLC", home)
        self.assertIn("Creative Commons 3.0 Attribution License", home)

    def test_exact_homepage_hero_and_editorial_rejections(self):
        home = self.pages[Path("index.html")]
        hero = " ".join("".join(home.headings[0][1]).split())
        self.assertEqual(hero, "Super intelligence with structure.")
        source = (ROOT / "index.html").read_text()
        self.assertNotIn('class="hero-mark"', source)
        self.assertIn('class="hero-geometry"', source)
        self.assertIn('assets/visual/hero-axiom.png', source)
        for asset in ("hero-axiom.png","systems-earth.png","research-wave.png","engineering-hall.png","closing-valley.png"):
            path = ROOT / "assets" / "visual" / asset
            self.assertTrue(path.is_file(), asset)
            self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", asset)
        self.assertNotIn('assets/brand/axiom-mark-512.png', source)
        self.assertNotIn('assets/brand/axiom-mark-512.png', (ROOT / "site.webmanifest").read_text())
        self.assertNotIn('hero-mark', self.styles)
        all_content = " ".join(page.content for page in self.pages.values())
        for rejected in ("Bring the difficult system.", "Software decides what runs.", "What should the system do?", "Boundaries before capabilities.", "Reliability is a boundary discipline.", "Reproducibility over ceremony.", "Intelligence, given structure."):
            self.assertNotIn(rejected, all_content)

    def test_advanced_positioning_has_no_generic_disclaimer_boilerplate(self):
        all_content = " ".join(page.content for page in self.pages.values()).lower()
        for rejected in ("not independent assurance", "not certification", "does not imply a production deployment", "does not establish exactly-once external effects", "engineering evidence, not certification", "does not provide independent certification"):
            self.assertNotIn(rejected, all_content)
        self.assertIn("advanced si systems", all_content)
        self.assertIn("advanced si systems for policy enforcement", all_content)
        self.assertIn("model output is a proposal", all_content)

    def test_si_public_positioning_preserves_technical_integrity(self):
        home = self.pages[Path("index.html")].content
        self.assertIn("super intelligence", home.lower())
        for path, page in self.pages.items():
            self.assertIn("Super intelligence systems engineering", page.content)
        readme = (ROOT / "README.md").read_text()
        self.assertNotIn("not as a claim", readme)
        self.assertIn("Advanced SI", readme)
        self.assertIn("public API contracts", readme)

    def test_director_has_prominent_public_presentation_without_private_links(self):
        home = self.pages[Path("index.html")]
        systems = self.pages[Path("systems/index.html")]
        director = self.pages[Path("director/index.html")]
        for page in (home, systems, director):
            self.assertIn("AXIOM Director", page.content)
            for attrs, _ in page.links:
                self.assertNotIn("github.com/axiom-llc/axiom-director", attrs.get("href", ""))
        home_source = (ROOT / "index.html").read_text()
        self.assertLess(home_source.index('id="director-title"'), home_source.index('id="apex-demo-title"'))
        self.assertLess(home_source.index('id="director-title"'), home_source.index('id="core-title"'))
        self.assertIn('href="director/"', home_source)
        self.assertIn('href="../director/"', (ROOT / "systems/index.html").read_text())
        self.assertIn("Fictional task and evidence", director.content)
        for capability in ("Strategic control", "Capability-based routing", "Governed autonomy", "Durable continuity"):
            self.assertIn(capability, director.content)

    def test_business_identity_is_axiom_llc_only(self):
        all_sources = "\n".join((ROOT / path).read_text() for path in PAGE_PATHS)
        forbidden = "".join(chr(x) for x in (65,100,97,109,32,84,97,99,111,110))
        self.assertNotIn(forbidden, all_sources)
        home=self.pages[Path("index.html")].content
        engineering=self.pages[Path("engineering/index.html")].content
        self.assertIn("AXIOM LLC", home)
        self.assertIn("AXIOM LLC", engineering)
        self.assertIn("Systems breadth", engineering)
        self.assertIn("Failure-mode engineering", engineering)
        self.assertNotIn("Virtuoso-level", engineering)
        self.assertNotIn("Hyper-capable", engineering)

    def test_core_stack_reference_is_public_and_bounded(self):
        systems=self.pages[Path("systems/index.html")].content
        source=(ROOT/"systems/index.html").read_text()
        self.assertIn("durably binding the ASON authorization identity", systems)
        self.assertIn("axiom-demos/tree/main/core-stack", source)

    def test_obsolete_single_page_navigation_is_removed(self):
        for page in self.pages.values():
            hrefs = [attrs.get("href", "") for attrs, _ in page.links]
            self.assertNotIn("#capabilities", hrefs)
            self.assertNotIn("#systems", hrefs)
            self.assertNotIn("#contact", hrefs)


if __name__ == "__main__":
    unittest.main()
