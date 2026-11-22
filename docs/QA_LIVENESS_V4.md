# CharterCycle — Security/liveness changes (v4)

Exact contract source SHA-256: `626761675678707b17dde12c2c1b21c0630cd1c5bf1d44cd162a7f853d3322f6`.

- Two proposals per founder per 7-day time window, preventing permanent historical-index exhaustion
- Permissionless STALE archiving of old competing proposals, including approved timelocks

- Official CI: **SUCCESS**, local 36/36 PASS, Direct Mode 7/7 PASS, GenVM lint PASS.
- Run: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45056596343
- No live transaction; Studionet requires explicit permission.
