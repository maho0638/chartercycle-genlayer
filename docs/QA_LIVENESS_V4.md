# CharterCycle — Security/liveness changes (v4)

Exact contract source SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`.

- Two proposals per founder per 7-day time window, preventing permanent historical-index exhaustion
- Permissionless STALE archiving of old competing proposals, including approved timelocks

- Official CI: **SUCCESS**, local 36/36 PASS, Direct Mode 7/7 PASS, GenVM lint PASS.
- Run: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45056596343
- No live transaction; Studionet requires explicit permission.

## Live verification update
- Live contract: `0x4cc15e0D4C89B57295D5B48eD027908581068C3c`; all recorded writes FINALIZED.
- https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057544161
- Legacy note: preceding 'no live transaction' statement referred to the pre-deployment phase only.
