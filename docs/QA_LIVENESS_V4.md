# Chartercycle — liveness/security regression v4

Scope: contract code and tests only; no website, deploy or transactions.

- Removed the permanent global lifetime limit on historical objects.
- Added bounded live-operation controls and eventual capacity recovery.
- Kept prior stored IDs and records immutable; newly added public methods only.
- Expanded fake-SDK negative/invariant cases and official Direct Mode tests.
- Real chain finality remains NOT VERIFIED pending separate authorization.

CI status: pending current code push and GitHub Actions results.

Controls: 2 proposals per genesis founder per 7-day transaction-time window; `archive_obsolete()` permissionlessly settles stale timelocks.
