# Enterprise package positioning — November 5, 2026

## Decision and scope

Owner-approved commercial strategy (November 5, 2026): focus AXIOM LLC's
commercial offers on **production AI-agent reliability and execution control**.
Primary buyers are engineering leads at AI-native B2B SaaS firms; initial
distribution favors existing AI implementation agencies and qualified
partnerships to reduce acquisition cost. The next business goal is one paying
customer and one customer-consented, independently supportable commercial case
study. These are strategic goals, not achieved outcomes.

Retain the existing $5,000 Agent Reliability & Control Sprint as the flagship.
Add a $1,500 paid diagnostic, a provisionally priced $12,500 hardening tier, and
a custom enterprise tier starting at a provisional $25,000. The higher-tier
prices are test proposals, not validated willingness-to-pay or guaranteed
contracts. Commercial-strategy approval alone did not authorize outbound outreach or
publication. On November 5, 2026 the Owner explicitly authorized removal of
the website publication hold, merging PR #13 and deploying the updated site.
Outreach, spending and external commitments remain separately gated.

Preserve PR #13's mobile navigation, typography, theme,
model-selection explanation, CTA wording, and established URL. Keep retrieval,
workflow integration and architecture/debugging as supporting capabilities;
do not sell them as competing primary package ladders. Preserve the
dependency-free HTML/CSS stack, existing palette, source evidence and
restored GitHub Pages deployment workflow on main.

## Research before pricing

Observed November 5, 2026; published offers are positioning references, not
evidence of sales volume, equal scope, delivery economics or AXIOM conversion.

| Primary source | Observed offer | Implication |
| --- | --- | --- |
| [FAULTLINE pricing](https://www.faultline-labs.com/pricing/) | $500 rapid diagnostic; $7,500 production reliability and pre-production audits | Differentiate AXIOM's bounded $5,000 sprint by including a control patch and reproducible handoff, rather than matching a larger trace-analysis scope. |
| [Rewired Ops Sprint](https://www.rewired.co/ai-ops-sprint) | $5,000 two-week assessment; execution separate | Historical $2,500 architecture-assessment proposal was superseded by the approved $1,500 agent-failure diagnostic; the implementation packages distinguish shipped changes from advisory work. |
| [McKinsey 2025 survey](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-2025) | Many respondents remain in pilot stages; workflow redesign and scaling are recurring themes | Inference: scoped integration, acceptance evidence and operational control are credible buyer problems to address. This does not establish demand for AXIOM specifically. |
| [IBM 2025 CEO study](https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/2025-ceo) | Survey of 2,000 CEOs across 33 geographies and 24 industries examines business outcomes, infrastructure and agent adoption | Lead with measurable workflow outcomes and keep model/infrastructure selection under customer control. |

## Approved commercial direction and proposed offers

| Package | Public starting/fixed USD fee | Delivery window after scope/access readiness | Boundary |
| --- | ---: | --- | --- |
| Agent Failure Triage | $1,500 fixed | 2 business days | One existing agent workflow, one failure class, diagnosis, evidence map and plan; **no production patch**. |
| Agent Reliability & Control Sprint | $5,000 fixed (retained) | 5 business days | Existing scope unchanged: one repository/service, up to five effect types, two provider profiles, at most one retrieval subsystem; one prioritized patch and acceptance tests. |
| Production Hardening | $12,500 fixed (test price) | 10 business days | Up to two agreed existing agent workflows, staging validation, bounded control changes and regression evidence. |
| Execution Assurance | From $25,000 (custom quote, test floor) | Typically 4+ weeks | Multi-system engineering assessment and prioritized controls; exact price, schedule and delivery boundaries require written scope. No independent certification or SLA. |

Observed competitors include [Code and Proof's $2,500 five-day diagnostic](https://codeandproof.com/services/ai-reliability-audit),
[Durgesh Rathod's $4,000–$6,000 audit](https://durgeshrathod.com/work-with-me),
and [nyk's $4,000–$7,000 production reliability audit](https://www.nyk.dev/consulting).
Published prices and scope are reference points, not evidence of AXIOM sales,
conversion, gross margin, or buyer budget. Direct acquisition and delivery costs
must be measured on actual engagements. Preliminary economics favor low-volume,
high-context referrals or agency partnerships over paid advertising.

Public proof is AXIOM-controlled tests, code and synthetic simulations; there
are no substantiated customer outcome metrics or independent certifications.
Keep customer-selected LLM support scoped to verified provider adapters.
The November 5 Owner instruction specifically authorizes this website merge
and deployment. Other publication, outreach preparation/sending, and spending
remain separately authorization-gated.

## Implementation plan and acceptance

- [x] Preserve the existing static stack; introduce no runtime dependencies or trackers.
- [x] Add model-agnostic positioning to Home, Systems, Director and packages, with adapter/capability validation explained.
- [x] Keep the hero link order; emphasize Meet Director through the shared button style and restrained accent.
- [x] Raise tiny labels to at least 12px equivalent and body copy slightly; preserve display hierarchy.
- [x] Replace AMD display text and suspended workflow's matching assertion.
- [x] Apply the exact two-sentence CTA on Home, Contact and packages.
- [x] Align visible offer names/prices, package anchors and structured OfferCatalog data to the approved strategy.
- [x] Keep mobile navigation available without JavaScript; close the enhanced menu with Escape and restore focus.
- [x] Run source, metadata and offer-contract checks.
- [x] Run complete original-asset checks and desktop/mobile browser verification in isolated GitHub Actions CI.
- [ ] Merge and deploy through restored main-only Pages workflow per Owner's November 5 authorization; verify the resulting production run and live pages before marking complete in the PR/release receipt.

## Verified recovery and results

[Prior isolated PR verification run 42100248157](https://github.com/axiom-llc/axiom-llc.github.io/actions/runs/42100248157)
passed on earlier implementation revision `ec1f2660a217ddfc3f117fe03253467871f281f0`. The updated commercial positioning requires independent rerun on the new PR head; this historical receipt does not validate subsequent edits.
The test workflow is scoped to the named PR branch, has read-only repository
permissions, and performs no deployment. The existing check/Pages holds remain.

- Full Python suite: **39/39 passed** in a complete GitHub checkout.
- Existing Chromium suite: passed at 320, 390, 768 and 1440px in light/dark
  modes, including image loading, keyboard focus and theme persistence across
  all nine routes and reloads.
- Conversion suite: **90 route/width/theme cases passed** (nine routes × five
  widths: 320, 390, 768, 1024, 1440 × two themes). Checks cover page/section/card
  overflow, navigation visibility, menu Escape/focus restoration, touch-target
  dimensions, four package destinations, and FAQ interaction.
- Reflow emulation: all nine routes at a 720 CSS-pixel viewport and device scale
  2, equivalent to a 1440px display at 200% layout zoom; this is not a separate
  manual browser-zoom measurement.
- JavaScript-disabled navigation: all nine routes at 320 and 1440px passed.
- JavaScript syntax and whitespace checks passed. No field performance claim.

The original temporary snapshot failure was caused by GitHub's contents
interface returning empty base64 content for artwork over 1 MB. The complete
CI checkout includes the originals and avoids that interface limitation. The
workflow retains the original-artwork archive and browser evidence for seven
days. The authenticated artifact download interface recovered all seven large
artwork files into the temporary snapshot; each Git blob hash matched the
canonical repository tree, and the full local suite subsequently passed39/39.
No original image bytes were changed in the PR.

The in-session browser automation service still cannot load its requirements;
native desktop input also failed provider initialization. Browser validation is
therefore performed by the repository's reproducible Chromium runner rather
than treating that session-specific integration as a website defect. Both
original verification blockers are resolved for this change; no browser-service
repair or production deployment is claimed.
