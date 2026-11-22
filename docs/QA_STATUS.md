# QA verified — chartercycle-genlayer

Checked: 2026-11-22

- Contract: `contracts/charter_cycle.py`
- Contract SHA-256: `c5c218ec0e31e4b8edbf120efc3e26a99969126682b98ca062da19296d12b604`
- Python syntax: **PASS**, verified GitHub Actions
- Supplemental AST audit: **PASS**, custom only
- Fake-SDK local pytest: **30/30 PASS** (NOT chain proof)
- Official `genvm-lint check contracts/*.py`: **PASS** (3 checks + validation)
- Official GenLayer Direct Mode (`genlayer-test==0.29.2`): **5/5 PASS** including validator mismatch scenarios
- CI run for exact contract version: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45045343123
- CI job ID: `137278622623`; contract commit: `bfcd01878357c9fcb399a4fa3c3bf9e9ee2e8714`
- Studionet deploy, actual write/read, transaction finality and live validator consensus: **NOT RUN** (separate chain/gas authorization required)
- Portal submission: **NOT AUTHORIZED**

The CI pipeline copies the official `genvm-runners-all.tar.xz` bundle cached by `genvm-linter` into the legacy `gltest-direct` cache filename to fix the upstream missing `genvm-universal.tar.xz` release asset. It does NOT bypass GenVM testing.

**Before Portal submission:** change **BOTH** private GitHub repositories to Public; verify anonymous access. The successful CI is not evidence of on-chain deployment.
