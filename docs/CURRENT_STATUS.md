# CharterCycle — verified state (2026-11-24)

- Contract source: `contracts/charter_cycle.py`; SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`.
- Python compilation / GenVM lint PASS; local logic **36/36 PASS**; official Direct Mode **7/7 PASS**.
- Initial live contract `0x4cc15e0D4C89B57295D5B48eD027908581068C3c` deployed; AI comparison COMPATIBLE; 3 Agree / 2 Idle.
- Full 48-hour lifecycle contract `0x5506E19b990cD9839659855AEC2fcA7c761867e8` deployed; amendment `live_timelock_lifecycle_v1` received **2 YES / 0 NO** from three genesis voters.
- The proposal, both votes, and the **finalize** transaction are all **FINALIZED** on chain.
- **FINALIZED finalize TX:** `0x44c23f0f082d7fca73573cef21f706f42701f6abf909051ed4c1a357dfced9a9`.
- On-chain proposal state is `TIMELOCK`. [Live finalize workflow](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45272322767); [independent RPC FINALIZED audit](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45272816728).
- **Only remaining timed step:** `enact` after **2026-11-24 22:42:10 Europe/Istanbul** (Unix `1795549330`). The original 24-hour vote plus 24-hour timelock cannot be bypassed.
- Resume script: `proofs/chartercycle_enact_studio_js.mjs`; workflow: `.github/workflows/chartercycle-timelock-resume.yml`. Uses current Studio fees, Studio-aware official GenLayerJS SDK and chain-time checks; never redeploys.
- Full machine-readable proof: `docs/STUDIONET_PROOF.json`.
- Portal submission **NOT** authorized/executed. Both GitHub repositories remain Private; make both Public and check anonymous access before Portal.
- Full independent security audit and 500-point result not guaranteed.
