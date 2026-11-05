"""Conversion contracts: visible offers, contact destinations and metadata agree."""
from pathlib import Path
import json
import re
import unittest
from html import unescape
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class ConversionTests(unittest.TestCase):
    def test_four_offers_have_matching_visible_prices_and_schema(self):
        source = (ROOT / 'engagements/reliability-control-sprint/index.html').read_text()
        graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1])['@graph']
        offers = next(item for item in graph if item['@type'] == 'Service')['hasOfferCatalog']['itemListElement']
        self.assertEqual(len(offers), 4)
        self.assertEqual([(offer['name'], int(offer['price'])) for offer in offers], [
            ('Agent Failure Triage', 1500),
            ('Agent Reliability & Control Sprint', 5000),
            ('Production Hardening', 12500),
            ('Execution Assurance', 25000),
        ])
        self.assertIn('Starting at $25,000', offers[3]['description'])
        self.assertIn('From $25,000', source)
        self.assertIn('No production patch included.', source)
        self.assertIn('No independent audit certification or uptime SLA.', source)
        for offer in offers:
            self.assertEqual(offer['priceCurrency'], 'USD')
            self.assertIn(offer['name'], unescape(source))
            self.assertIn('$' + format(int(offer['price']), ','), source)
            self.assertIn('id="' + offer['url'].split('#')[1] + '"', source)
        contacts = re.findall(r'href="(mailto:[^"]+)"', source)
        self.assertGreaterEqual(len(contacts), 4)
        for contact in contacts:
            self.assertEqual(urlsplit(unescape(contact)).path, 'axiom.co@proton.me')
            self.assertTrue(parse_qs(urlsplit(unescape(contact)).query).get('subject'))

    def test_production_agent_positioning_and_retained_secondary_capabilities(self):
        home = (ROOT / 'index.html').read_text()
        engagements = (ROOT / 'engagements/index.html').read_text()
        packages = (ROOT / 'engagements/reliability-control-sprint/index.html').read_text()
        self.assertIn('Control what AI agents can change.', home)
        self.assertIn('Production reliability engineering', engagements)
        self.assertIn('Control what your AI agents can change.', packages)
        self.assertIn('RAG durability &amp; retrieval engineering', engagements)
        self.assertNotIn('Architecture &amp; Readiness Assessment', packages)
        self.assertNotIn('Retrieval Quality &amp; Durability Sprint', packages)
        self.assertNotIn('Workflow Integration Sprint', packages)

    def test_exact_cta_and_model_choice_are_on_primary_decision_pages(self):
        for path in ['index.html', 'contact/index.html', 'engagements/reliability-control-sprint/index.html']:
            source = (ROOT / path).read_text()
            self.assertIn('Send the system, objective, constraint, and acceptance target.<br>Let AXIOM handle the rest.', source, path)
        for path in ['index.html', 'systems/index.html', 'director/index.html', 'engagements/reliability-control-sprint/index.html']:
            source = (ROOT / path).read_text().lower()
            self.assertIn('model-agnostic', source, path)
            self.assertIn('llm', source, path)

    def test_mobile_navigation_has_progressive_enhancement_and_escape(self):
        source = (ROOT / 'theme.js').read_text()
        self.assertIn('nav-ready', source)
        self.assertIn('Escape', source)
        self.assertIn('navButton.focus()', source)
        styles = (ROOT / 'styles.css').read_text()
        self.assertIn('.site-header.nav-ready nav', styles)
        self.assertIn('.site-header:not(.nav-ready) nav', styles)

if __name__ == '__main__':
    unittest.main()
