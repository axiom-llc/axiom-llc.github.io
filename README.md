# AXIOM LLC website

The dependency-free public site for AXIOM LLC, an AI systems engineering lab:
[axiom-llc.github.io](https://axiom-llc.github.io).

## Information architecture

- `/` — concise flagship identity, core architecture, selected evidence, and contact path.
- `/systems/` — ASON, APEX, and RAG relationships plus validated supporting systems.
- `/research/` — current research agenda, artifacts, and evidence boundaries.
- `/engineering/` — Adam Tacon's evidence-backed engineering profile, principles, validation posture, and the complete stack.
- `/contact/` — project brief guidance and contact details.
- `/engagements/` — evidence-backed engineering engagement capabilities and contact path.
- `/engagements/reliability-control-sprint/` — fixed-scope Agent Reliability & Control Sprint offer.

Each route is plain HTML. `styles.css` is the shared Graphite / Ivory / Ice visual
system, `favicon.svg` is the AXIOM mark, and `assets/technology/` contains locally
vendored technology marks. Inter Variable and IBM Plex Mono Variable are served
from `assets/fonts/` with their OFL licenses. Provenance is recorded in the
respective `SOURCES.md` files.

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. There is no build step, package installation,
JavaScript requirement, analytics, tracker, or external runtime asset request.
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
