# Website RSI: executable read-only generator and validation

Source: website `main` revision `fa18cd863d6699710f1c6158d23a28cdac498f41`.
The `rsi/generators.json` registration targets only `theme.js`, within
Director's existing website-specific `axiom-native-rsi/v1` allowance.

## Generator and tests

`python -m rsi.native --output candidate.json` generates a deterministic
source-revision-bound unified diff that moves the static theme-label query
outside `apply()`. It produces candidate/source/patch SHA-256 digests and
`mutation_authority=false`; it **does not apply** any patch or edit a
production file. Missing, duplicated, stale, dirty or unauthorized source
references fail closed. Regression tests independently verify ordinary
`git apply` and exact reverse against a temporary test fixture.

## Browser evidence

`native-rsi.yml` runs Python 3.11 and 3.12, the site's existing source
checks and paired, real Chromium DOM-interaction tests. The acceptance
fixture alternates baseline/candidate measurement order over 11 pairs,
with 900 theme activations per variant in each pair; it covers actual
Home, Director and packages routes, 390/1440px layouts, light/dark browser
preferences, system preference changes, meta tags, persistent mode,
visible label and accessibility text. Independent PR browser checks
retain nine-route responsive, keyboard and no-JavaScript coverage.

Local browser execution is representative **UI interaction** evidence,
but its workload is synthetic: not live traffic, field latency, real-user
time saving, business ROI, or production-scale performance. A measurement
may be valid within this limited machine-performance scope even if small,
negative, or inconclusive.

## Strict promotion and release gates

No automatic candidate implementation or Pages publication is installed.
Any future application requires an exact-head proposal with independently
verified event-run and artifact ZIP identities; successful behavioral
equivalence and matched representative browser measurements; independent
source/code and rollback review; and **explicit Owner-reviewed candidate
implementation** in a separately validated PR. Synthetic gains alone do
not satisfy these gates. Even after a reviewed code merge, production
publication independently requires Owner authorization for a specific
new `main` SHA and manual `pages.yml` dispatch with `expected_sha`.

`.github/workflows/pages.yml` remains manual and SHA-pinned. The disabled
`.github/workflows/check.yml` hold, existing source, assets and public
content remain unchanged. No OAuth grant, external dispatch, site
deployment, scheduler, customer-facing action or candidate patch application
is authorized by this generator or its CI artifacts.
