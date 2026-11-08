# Website production-release gate — November 8, 2026

The site publishes **only** through `.github/workflows/pages.yml` with a
manually requested `workflow_dispatch`. There are no `push` or
`pull_request` production triggers. The deployment job requires both
`github.ref == 'refs/heads/main'` and `github.actor == 'axiom-llc'`.

**Every new production release requires a distinct explicit Owner action**
naming that release's exact reviewed `main` commit in the mandatory
`expected_sha` input. The workflow fails closed if that SHA differs from
the event commit, checkout HEAD, or latest remote `main` before deployment.
A previous approval, successful validation, merged PR, synthetic benchmark,
or generator proposal cannot authorize a later release.

The existing local site tests and post-deployment browser/route/asset
checks remain in place. The general `.github/workflows/check.yml` hold
remains unchanged. Independent source review and head-bound PR validation
are required before merge; a merge does not deploy.

No release is authorized by this policy update; the new approval for a
specific future `expected_sha` must be obtained separately.
The website's read-only `rsi/native.py` generator remains unmodified.
Candidate implementation additionally requires representative acceptance
evidence, independent validation, and explicit implementation review;
synthetic-only measurements cannot authorize patch application.
