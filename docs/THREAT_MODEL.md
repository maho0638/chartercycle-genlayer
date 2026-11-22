# CharterCycle — threat model and explicit limitations

## Protected by deterministic contract code

- Only a nonzero member address from the frozen genesis set can propose or vote.
- A ballot key is bound to one unique proposal and member; ballots are immutable.
- Two-thirds approval is computed from all genesis members, not votes cast.
- Voting closes at 24h; any approved charter is timelocked another 24h.
- Every proposal is bound to a charter version and immutable content digest.
- Enactment changes exactly one version; competing passed proposals cannot overwrite it.
- No privileged admin escape hatch, treasury or value transfer path.

## Dependent on honest validator majority / semantic classification

- AI may misjudge contradiction with immutable provisions. Its judgments are NOT a mathematical proof of charter meaning.
- All new charter text is untrusted data in the prompt. Prompt injection can be attempted, mitigated by an independent validator rerun, not eliminated.
- Classifier errors and validator disagreement are possible; conflict/uncertain statuses never authorize voting.

## Known trade-offs and boundaries

- Genesis members cannot be removed, rotated or recovered if a wallet is lost. This is intentionally excluded from v1 to prevent admin takeovers.
- No on-chain proof that separate genesis addresses are independently controlled. This is an opt-in member registry, not sybil resistance.
- No external funds, arbitrary execution or cross-contract state mutations.
- Blockchain time is transaction time, not external wall-clock time.
- There is no automated executor: someone must call `finalize` and `enact` after their respective deadlines.
- Contract source lint/GenVM deployment is required before a security or compatibility claim.
