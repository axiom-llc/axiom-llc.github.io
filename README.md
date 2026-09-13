# AXIOM LLC website

The public site for AXIOM LLC's AI and automation systems:
[axiom-llc.github.io](https://axiom-llc.github.io).

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. There is no build step, package installation,
JavaScript requirement, analytics, or external font request. GitHub Pages publishes
`main` using the repository's configured Pages deployment.

## Maintain

- `index.html`: business information, capabilities, system boundaries, and contact links.
- `styles.css`: dark-only responsive layout, typography, and keyboard focus states.
- `favicon.svg`: AXIOM brand mark.

Keep visible contact details and URI targets consistent. The business number is
**(609) 403-0646**, linked as `tel:+16094030646`. Email remains
`axiom.co@proton.me`.

Describe APEX as the execution/runtime, ASON as pre-execution policy enforcement,
and RAG as the canonical retrieval/storage HTTP service and library. Do not imply
that model outputs are deterministic, audits are complete security boundaries, or
every runtime tool is sandboxed. Architecture is presented as responsive HTML
rather than a separate diagram with duplicated implementation details.

## Validate

```bash
python -m unittest discover -s tests -v
git diff --check
```

Preview desktop and narrow mobile layouts. Check navigation, keyboard focus,
contact links, readability at 200% zoom, and the page with JavaScript disabled.
No content should depend on animation or hover. Review external repository links
when project visibility changes.
