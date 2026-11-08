# Website native RSI — non-deploying readiness record

Status: `PREPARED_ONLY / OWNER_ACTIONS_HOLD`  
Source: `axiom-llc/axiom-llc.github.io@949293462a1b9eab491d6826720b53f7130241a3`  
Scope: read-only generator proposal for `theme.js`; **no candidate generated or applied**.

## Authoritative constraints

- `.github/workflows/check.yml` has no enabled job and explicitly requires Owner confirmation of usable GitHub Actions quota before restoration.
- `.github/workflows/pages.yml` deploys every `main` push; **do not merge any website code without separate release authorization**.
- `.github/workflows/verify-website-pr.yml` triggers only on pushes to `website-enterprise-packages-2026-11-05`; this independent preparation branch must not use that name, dispatch Actions or open a deploy-enabled release PR.
- Director's prior `axiom-native-rsi/v1` federation accepts Python targets only. The separate Director PR #206 proposes a fail-closed **website-only `theme.js`** exception; do not assume it merged or that browser acceptance is complete.
- Preserve current accessibility, theme-mode metadata, mobile navigation, no-JavaScript behavior, exact assets and existing public routes. No network, telemetry, secrets or asset modifications.

## Source-grounded candidate hypothesis (not an optimization claim)

At source revision above, `theme.js` performs `button.querySelector("[data-theme-label]")` inside `apply()`, and `apply()` runs on theme click and applicable system-preference events. A potential read-only generator can propose caching that stable label element outside `apply()`, avoiding repeated selection. **Do not apply it until** runtime tests establish DOM lifetime/semantics and measured benefit. If dynamic label replacement is a supported behavior, reject the cache transformation. Restrict its source anchor and target path to the exact verified source; reject duplicate anchors, stale SHAs, unapproved paths and unsafe patches.

## Integration acceptance sequence (after separate approvals)

1. Confirm billable Actions capacity and explicit approval for a bounded, non-deploying validation run. Keep the production Pages trigger unchanged until a separately approved release plan.
2. Provide a source-bound `rsi/generators.json`, pure read-only `rsi/native.py`, and Python 3.11/3.12 paired benchmark and regressions. The generator must emit deterministic candidate/patch/source SHA-256 and `mutation_authority=false`; no source-write or deployment primitive.
3. Validate strict website `theme.js` schema in Director, static `node --check`, existing unit tests, and browser behavior across mobile/desktop widths, keyboard navigation, theme states and reduced functionality when JavaScript is disabled. Check artifact identity against exact source SHA and unchanged unrelated source files.
4. Benchmark representative theme-toggle and system-preference interaction workloads against baseline in the same browser/configuration with paired repetitions, overhead accounting and negative holdouts. Treat synthetic fixture timing as preliminary; do not infer user-time or commercial ROI.
5. Prepare a reviewable implementation PR **only** after independent acceptance, prior source/head verification, explicit release authorization and successful head-bound CI. A PR must not merge to `main` or deploy on the strength of candidate metadata alone. Preserve exact Git reverse rollback.

## Publication and permission boundaries

Source-to-Director `repository_dispatch` requires a repository-scoped credential with Contents **write** on the Director repository. Director-to-source `workflow_dispatch` requires Actions **write** on the selected source repository. Those grants are **not verified**; no token, secret, external event or CI dispatch is created. A per-run `GITHUB_TOKEN` with only the site's current repository rights does not establish cross-repository authorization. Revalidate the grant and event payload against live GitHub identity before enabling any relay.

## Current acceptance

- Safe preparation: branch-only review artifact, no user-visible website change.
- Runtime validation: `BLOCKED_OWNER_ACTIONS_HOLD`.
- Production promotion: `NOT_ELIGIBLE`; no representative benchmarks or approved deployment.
