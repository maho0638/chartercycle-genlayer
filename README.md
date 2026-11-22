# CharterCycle — Consensus-Governed Constitutional DAO (GenLayer)

**Contract only — no frontend. Development draft; not deployed or audited.**

## What is actually implemented

- `contracts/charter_cycle.py`: one standalone `gl.Contract`, version-pinned.
- 3–15 deployer-specified genesis members; deployer must belong to genesis set.
- Frozen one-member-one-vote and 2/3-of-**all**-members threshold; abstentions are never positive votes.
- AI conflict classification against immutable governance invariants using a fresh leader response and **independent validator re-execution**.
- Three decision classes: `COMPATIBLE`, `CONFLICT`, `UNDETERMINED`. Only `COMPATIBLE` may open voting.
- Fixed 24-hour vote + additional 24-hour timelock before charter replacement.
- Immutable proposal IDs/candidate hashes; explicit version check; stale proposals cannot overwrite later versions.
- No value transfers, treasury, proxy, contract owner override, or public membership expansion.

## Code surface

- `CharterCycle(constitution: str, founders_json: str)`
- `propose(proposal_id, replacement, rationale)`
- `vote(proposal_id, support)`
- `finalize(proposal_id)`
- `enact(proposal_id)`
- `get_charter()`, `get_proposal(id)`, `get_proposal_count()`, `get_proposal_id(i)`, `is_member(address)`

## Verification matrix

| Stage | Status |
|---|---|
| Python compile | PASS (locally) |
| Supplementary AST audit (NOT official lint) | PASS (locally) |
| Pure-Python contract-logic simulation | PASS (30 tests, fake SDK and fake LLM) |
| Official GenLayer Direct Mode tests | **5/5 PASS** (GitHub Actions; actual SDK fixture, not Studionet) |
| `genvm-lint check` | **PASS** (GitHub Actions, official linter) |
| Studionet deploy / on-chain finality | **NOT RUN** — requires separate chain/gas approval |
| Reviewer/portal submission | Not submitted |

`PYTHONPATH=tests/local python -m pytest tests/local -q` runs the isolated fake-SDK logic tests. The repository includes a non-deploying GitHub Actions workflow, verified successful.

With GenLayer tooling installed, run:

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/charter_cycle.py
pytest tests/direct/ -v
```

GitHub Actions verified these commands against the actual SDK and official linter: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45045343123. See `docs/THREAT_MODEL.md` and `docs/RELEASE_GATE.md`.

## Release control

Before Portal submission, **REMIND OWNER TO CHANGE BOTH PRIVATE GITHUB REPOSITORIES TO PUBLIC** and verify access while logged out. GitHub source push was separately authorized and completed. Chain deploy, gas spending and Portal submission require separate explicit user permission.

Official Direct Mode tests passed in GitHub Actions, with mocked LLMs and validator reruns; these are NOT finalized on-chain consensus or Studionet transactions.

## QA v3 update (2026-11-22)

- Supplemental negative tests now reject Unicode bidi/zero-width display spoofing in signed charter/move text.
- Canonicalizes wallet address case before constructing SDK Address.
- QuestForge rejects boolean turn nonce before type conversion.
- CharterCycle covers quorum acceptance/rejection for all configured member counts 3..15.
- QuestForge runs 100 reproducible seeded game traces with bounds assertions.
- Official GenVM lint and Direct Mode passed in GitHub Actions (5/5 Direct Mode); live Studionet proof has NOT been claimed.
- Verified exact source SHA-256: `c5c218ec0e31e4b8edbf120efc3e26a99969126682b98ca062da19296d12b604`; canonical CI: https://github.com/maho0638/chartercycle-genlayer/actions/runs/45045343123.
