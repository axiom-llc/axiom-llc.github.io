"""Dependency-free checks for static assets and working navigation/contact paths."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
STYLES = (ROOT / 'styles.css').read_text()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Page()
        cls.page.feed((ROOT / 'index.html').read_text())

    def test_local_links_and_anchors_resolve(self):
        ids = [attrs['id'] for _, attrs in self.page.elements if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        for _, attrs in self.page.elements:
            for key in ('href', 'src'):
                if key not in attrs:
                    continue
                url = urlsplit(attrs[key])
                if url.scheme or url.netloc:
                    continue
                if url.path:
                    self.assertTrue((ROOT / url.path).is_file(), attrs[key])
                if url.fragment:
                    self.assertIn(url.fragment, ids)

    def test_contact_paths(self):
        links = [attrs.get('href') for tag, attrs in self.page.elements if tag == 'a']
        self.assertIn('mailto:axiom.co@proton.me', links)
        phones = [href for href in links if href and href.startswith('tel:')]
        self.assertEqual(phones, ['tel:+16094030646'])
        self.assertIn('(609) 403-0646', ''.join(self.page.text))
        for path in [ROOT / 'index.html', ROOT / 'README.md']:
            numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', path.read_text())
            self.assertEqual(numbers, ['(609) 403-0646'])

    def test_accessible_static_structure(self):
        self.assertEqual(sum(tag == 'h1' for tag, _ in self.page.elements), 1)
        self.assertEqual(sum(tag == 'main' for tag, _ in self.page.elements), 1)
        self.assertFalse(any(tag == 'script' for tag, _ in self.page.elements))
        for tag, attrs in self.page.elements:
            if tag == 'img':
                self.assertIn('alt', attrs)
            if tag == 'nav':
                self.assertIn('aria-label', attrs)
        self.assertIn(('meta', {'name': 'color-scheme', 'content': 'dark'}), self.page.elements)
        self.assertIn('a:focus-visible', STYLES)

    def test_system_cards_have_independent_borders(self):
        """Grid placement must never determine whether a card has an edge."""
        self.assertRegex(
            STYLES,
            r'\.systems\s*\{[^}]*grid-template-columns:[^;}]+;[^}]*gap:\s*12px;',
        )
        self.assertRegex(
            STYLES,
            r'\.system\s*\{[^}]*border:\s*1px solid var\(--line\);',
        )
        self.assertNotIn('.system + .system', STYLES)
        self.assertNotIn('.system:nth-child', STYLES)

    def test_system_card_headers_share_grid_tracks(self):
        """Metadata height must not set an individual card title's position."""
        self.assertIn('grid-template-rows: repeat(6, auto)', STYLES)
        self.assertIn('grid-row: span 6', STYLES)
        self.assertIn('grid-template-rows: subgrid', STYLES)
        for row in range(1, 5):
            self.assertIn(f'grid-row: {row}', STYLES)

    def test_engineering_stack_is_grouped_and_excludes_unverified_tools(self):
        text = ''.join(self.page.text)
        for label in ('Systems', 'AI & agents', 'Data', 'Interfaces', 'Infrastructure', 'Applied'):
            self.assertIn(label, text)
        for excluded in ('PostgreSQL', 'pgvector', 'Cloud Run', 'OpenCode', 'Podman'):
            self.assertNotIn(excluded, text)

    def test_static_assets_do_not_require_external_requests(self):
        resource_links = [
            attrs['href']
            for tag, attrs in self.page.elements
            if tag == 'link' and 'href' in attrs
        ]
        self.assertEqual(resource_links, ['favicon.svg', 'styles.css'])
        embedded_sources = [
            attrs['src']
            for tag, attrs in self.page.elements
            if tag in {'img', 'script', 'iframe', 'audio', 'video'} and 'src' in attrs
        ]
        self.assertEqual(embedded_sources, ['favicon.svg'])


if __name__ == '__main__':
    unittest.main()
