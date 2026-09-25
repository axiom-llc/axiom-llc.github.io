from pathlib import Path
import unittest
from tests.test_site import parse, local_target, ROOT
class CaseStudyTests(unittest.TestCase):
    def setUp(self):
        self.path=Path('case-studies/index.html'); self.page=parse(self.path)
    def test_case_study_page_is_bounded_and_evidence_traceable(self):
        text=self.page.content
        for required in ('Five synthetic organizations','74 modeled steps','74 successful recorded effects','Synthetic demonstrations, not production deployments','not establish regulatory compliance','67 produced files'):
            self.assertIn(required.lower(),text.lower())
        hrefs=[attrs.get('href','') for attrs,_ in self.page.links]
        for required in ('simulations/portfolio-summary.json','simulations/cross-domain-findings.md','simulations/claims','axiom-demos/tree/main/organizational-simulations'):
            self.assertTrue(any(required in href for href in hrefs),required)
        case_hrefs={href for href in hrefs if '/simulations/case-studies/' in href}
        self.assertEqual(len(case_hrefs),5)

    def test_high_fidelity_cycles_are_bounded_and_traceable(self):
        text=self.page.content.lower()
        for required in ('accepted high-fidelity cycles','three days','six work items per domain','shared resources under contention','24/24 successful effects/events'):
            self.assertIn(required.lower(),text)
        hrefs=[attrs.get('href','') for attrs,_ in self.page.links]
        for required in ('simulations/operational-fidelity/portfolio-acceptance.json','simulations/operational-fidelity/gap-closure-findings.md','organizational-simulations/high-fidelity'):
            self.assertTrue(any(required in href for href in hrefs),required)
        self.assertTrue(any('software-development.md' in href for href in hrefs))
        self.assertTrue(any('logistics-supply-chain.md' in href for href in hrefs))

    def test_local_assets_and_links_resolve(self):
        for _,attrs in self.page.elements:
            for key in ('href','src'):
                if key not in attrs: continue
                target,_=local_target(self.path,attrs[key])
                if target is not None: self.assertTrue(target.is_file(),attrs[key])
    def test_research_page_links_case_studies(self):
        hrefs=[attrs.get('href') for attrs,_ in parse(Path('research/index.html')).links]
        self.assertIn('../case-studies/',hrefs)
if __name__=='__main__': unittest.main()
