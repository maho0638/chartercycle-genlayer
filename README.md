# CharterCycle — Consensus-Governed Constitutional DAO (GenLayer)

**Python GenLayer Intelligent Contract only — no website. Live-verified on Studionet (chain ID 61999).**

## Implemented contract

Source: `contracts/charter_cycle.py`. One standalone `gl.Contract` with persistent GenLayer storage.

- Immutable genesis founder membership (3–15 wallets) and one vote per proposal
- A 2/3-of-all-founders quorum, 24-hour voting, 24-hour timelock, and one-version-only enactment
- AI judges rule compatibility; validators independently rerun the decisive comparison
- Two proposals per founder per 7-day time window, preventing permanent historical-index exhaustion
- Permissionless STALE archiving of old competing proposals, including approved timelocks
- No transfers, treasury, arbitrary execution, or website

## Independent verification (2026-11-22)

- **36/36** local logic tests PASS (fake SDK, not chain).
- **7/7** official GenLayer Direct Mode tests PASS (SDK storage, mock LLM, validator reruns).
- **GenVM lint PASS**, including official validation checks.
- Python compilation and supplemental AST audit PASS.
- [Canonical successful GitHub Actions run](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45056596343)
- Verified source SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`
- Verified source commit: `f61c547766dd73f13b6cb833fc49bbfd38a16787`
- **Studionet live deployment SUCCESS:** `0x4cc15e0D4C89B57295D5B48eD027908581068C3c`; finalized writes and real validator result **3 Agree / 2 Idle**. See `docs/STUDIONET_PROOF.json`.

For reproducibility:

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/charter_cycle.py
PYTHONPATH=tests/local python -m pytest tests/local -q
pytest tests/direct -v
```

Full security limitations: `docs/THREAT_MODEL.md`. Latest exact test evidence: `docs/QA_STATUS.md` and `docs/LOCAL_PROOF_MANIFEST.json`.

## Publication gate

**BEFORE PORTAL SUBMISSION: Change both GitHub repositories from PRIVATE to PUBLIC and verify logged-out access.**
Chain deployment/gas, Portal submission, and any other external action need separate explicit user authorization.

## Canonical Studionet evidence (2026-11-22)

- Contract: `0x4cc15e0D4C89B57295D5B48eD027908581068C3c`
- Network: Studionet, chain 61999; contract source SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`
- 2 on-chain contract write transactions **FINALIZED**; outcome COMPATIBLE
- Real validator vote tally for decisive AI call: **3 Agree, 2 Idle**, one consensus round.
- [Deployment and write/read test](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057544161) and [independent status/vote audit](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057971178).
- Full transaction hashes and exact status in `docs/STUDIONET_PROOF.json`.

Portal submission remains **not authorized**, and both private repositories must be made **Public** before submission.
