# Release gate — explicit authorization required

- [x] Source committed to GitHub under user-authorized development task
- [x] Local fake-SDK regression 36/36
- [x] Python compilation and supplemental static checks
- [x] Official `genvm-lint check` PASS
- [x] Official GenLayer Direct Mode 7/7 PASS, including validator mismatch
- [x] Security audit: wallet permissions, replay, boundary times, retained ID history, terminal-state accounting
- [x] Studionet deployment and independent real-chain read/write/finality
- [x] Record real on-chain contract address, transaction hashes, leader/validator results; gas figures unavailable, not invented
- [x] Verify on-chain source correspondence using CI-pinned SHA-256 and finality from the RPC
- [ ] Review latest Portal criteria and distinctness against live competing contributions
- [ ] **Reminder: Both private repositories must be made Public before Portal submission; verify logged-out access**
- [x] User authorized the already performed Studionet development deployment and test writes
- [ ] User's separate explicit authorization for Portal submission

Evidence of code-level checks: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45056596343

No on-chain claim should be made before verified finalized transactions.

## Live proof finalized

- `docs/STUDIONET_PROOF.json` — full chain address, writes, real validator vote tally, finality results.
- https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057544161

## 2026-11-24 — verified new milestone

- [x] 24-hour vote finalized with 2 YES / 0 NO: `0x44c23f0f082d7fca73573cef21f706f42701f6abf909051ed4c1a357dfced9a9`, FINALIZED.
- [x] Proposal in TIMELOCK, source unchanged.
- [ ] Live enactment after 24 Nov 22:42:10 Türkiye; require separate FINALIZED receipt and charter version 2/hash.
- [x] Existing automation updated to invoke fee-aware, fail-closed GenLayerJS enactment workflow.
- [ ] Portal review, repository Public conversion, Portal submission — do not run without explicit separate approval.

Evidence: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45272816728
