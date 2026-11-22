# Hard release gate — action requires user approval

- [x] Official `genvm-lint check` PASS on exact source hash, evidence captured.
- [x] Official GenLayer Direct Mode tests PASS, including validator disagreements.
- [ ] Studionet deployments and real write/read finalization PASS; record addresses and TX hashes.
- [ ] Source SHA-256 equals deployed proof manifest; preserve validator/leader results.
- [ ] Security review: auth, replay, duplicate IDs, ranges, time windows and terminal states.
- [ ] Review external duplicate projects / reviewer criteria one last time.
- [x] **Explicit user permission for GitHub push** before creating commits on the remote.
- [ ] **REMIND USER: make BOTH GitHub repositories Public before Portal submission**, then verify unauthenticated read access.
- [ ] **Explicit user permission for chain deploy / gas and Portal submission.**

Source code, tests, mock simulation and successful CI are distinct from real finalized GenLayer transactions.

## Verified CI evidence (not deployment)

- Source SHA-256: `c5c218ec0e31e4b8edbf120efc3e26a99969126682b98ca062da19296d12b604`
- 30/30 mock-only local tests, 5/5 official Direct Mode and GenVM lint PASS.
- https://github.com/maho0638/chartercycle-genlayer/actions/runs/45045343123
- Studionet live verification remains blocked without separate chain/gas permission.
