# AXIOM LLC website

The dependency-free public site for AXIOM LLC's super intelligence systems engineering work:
[axiom-llc.github.io](https://axiom-llc.github.io).

## SI terminology

AXIOM uses **SI (super intelligence)** as its strategic research and engineering direction, not as a claim that any published implementation has achieved superhuman performance. Existing provider names, public API contracts, established research terminology, source filenames and historical evidence remain accurate and unchanged.

## Information architecture

- `/` — concise flagship identity, core architecture, selected evidence, and contact path.
- `/systems/` — ASON, APEX, and RAG relationships plus validated supporting systems.
- `/research/` — current research agenda, artifacts, and evidence boundaries.
- `/engineering/` — AXIOM LLC engineering practice, principles, validation posture, and the complete stack.
- `/contact/` — project brief guidance and contact details.
- `/case-studies/` — synthetic organizational simulations with explicit evidence limits.
- `/engagements/` — evidence-backed engineering engagement capabilities and contact path.
- `/engagements/reliability-control-sprint/` — fixed-scope Agent Reliability & Control Sprint offer.

Each route is plain HTML. `styles.css` is the shared approved light/dark AXIOM visual
system, `theme.js` provides progressive theme selection, `favicon.svg` and
`assets/brand/` contain deployment-only derivatives from the private canonical
AXIOM aura master (including density-aware 1x/2x web renders), and
`assets/technology/` contains locally vendored technology marks. Inter Variable and IBM Plex Mono Variable are served
from `assets/fonts/` with their OFL licenses. Provenance is recorded in the
respective `SOURCES.md` files.

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. There is no build step, package installation,
analytics, tracker, or external runtime asset request. JavaScript is used only for
explicit theme selection and mobile navigation; system-preference light/dark styling
remains available without JavaScript.
GitHub Pages publishes `main` using the repository's configured Pages deployment.

## Maintain

Keep the compact navigation and visible contact details consistent across pages.
The business number is **(609) 403-0646**, linked as `tel:+16094030646`. Email
remains `axiom.co@proton.me`.

Describe APEX as execution/runtime, ASON as caller-policy enforcement before
submission, and RAG as the canonical retrieval/storage HTTP service and library.
Do not imply deterministic model output, exactly-once external effects, general
runtime sandboxing, third-party assurance, or a production deployment without
new direct evidence.

Add system detail pages only when enough distinct public material exists to
justify a maintained page. Prefer direct repository links over thin summaries.

## Validate

```bash
python -m unittest discover -s tests -v
git diff --check
```

Preview desktop and narrow mobile layouts. Check keyboard navigation, focus
visibility, readability at 200% zoom, and every page with JavaScript disabled.
No content may depend on animation or hover. Recheck external repository links
and technology mark guidance when their public state changes.
