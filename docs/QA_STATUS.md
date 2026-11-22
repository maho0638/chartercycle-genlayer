# QA v3 — chartercycle-genlayer

Checked: 2026-11-22

- Contract SHA-256: `9385a0192864e8314546d16aa77278303c576404ecbba391164ea60270778231`
- `python -m compileall -q contracts tests`: **PASS**
- `python scripts/static_contract_audit.py`: **PASS** (custom, NOT official GenVM lint)
- `PYTHONPATH=tests/local python -m pytest tests/local -q`: **30/30 PASS** (fake SDK, NOT GenVM)
- Official `genvm-lint check`: **NOT RUN** — runtime tooling unavailable; package network blocked
- Official Direct Mode with `genlayer-test`: **NOT RUN** — dependencies unavailable
- Studionet deployment, transactions, finality and validator consensus: **NOT RUN** — needs separate gas/chain authorization
- GitHub CI: **PENDING** — CI will execute after approved push

Local tests include parameter loops; loop iterations are not separately counted as pytest cases.

**Pre-submission reminder:** Both GitHub repositories currently Private; make both Public and verify anonymous access before Portal submission.
