# CharterCycle — Verified QA (2026-11-22)

- Contract: `contracts/charter_cycle.py`
- Contract SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`
- Source commit: `f61c547766dd73f13b6cb833fc49bbfd38a16787`
- GitHub Actions: **SUCCESS** — https://github.com/maho0638/chartercycle-genlayer/actions/runs/45056596343
- Job ID: `137313091589`
- Python compilation: PASS
- Supplemental static AST audit: PASS (not official lint)
- Fake SDK: **36/36 PASS** (simulation)
- Official GenVM lint: **PASS** (three checks and validation)
- Official Direct Mode: **7/7 PASS**, validator reruns with mocked LLM
- Studionet live deployment + finalized transactions: **NOT RUN**, pending separate gas/chain approval
- Portal submission: **NOT AUTHORIZED**
- Both GitHub repositories: **PRIVATE**; switch to Public before Portal submission and verify anonymous accessibility

Real Direct Mode checks are not equivalent to real on-chain consensus.

## Latest superseding release status (2026-11-22)

- **Studionet LIVE VERIFIED**, chain ID 61999, address `0x4cc15e0D4C89B57295D5B48eD027908581068C3c`.
- Real semantic decision `COMPATIBLE`, validator votes 3 Agree / 2 Idle; 2 write transactions FINALIZED.
- Canonical run: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057544161
- Independent status/votes audit: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057971178
- Portal submission not authorized; private repositories must be Public before Portal.
