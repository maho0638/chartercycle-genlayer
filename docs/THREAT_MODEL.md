# CharterCycle — threat model and explicit limitations

## Protected by deterministic contract code

- Only a nonzero member address from the frozen genesis set can propose or vote.
- A ballot key is bound to one unique proposal and member; ballots are immutable.
- Two-thirds approval is computed from all genesis members, not votes cast.
- Voting closes at 24h; any approved charter is timelocked another 24h.
- Every proposal is bound to a charter version and immutable content digest.
- Enactment changes exactly one version; competing passed proposals cannot overwrite it.
- No privileged admin escape hatch, treasury or value transfer path.
- A per-founder, per-7-day proposal quota replaces the old global lifetime cap; historical proposal IDs remain immutable.
- Anyone can mark competing proposals from an obsolete charter version as STALE, including previously approved timelocks.

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
- The proposal index remains bounded by the largest u32 count and is not economically protected against many distinct funded wallets; founders are trusted participants.
- The 7-day proposal quota uses transaction timestamps and resets by integer time period, so a boundary can allow proposals close together.
- A successful Direct Mode test is not live Studionet settlement. Actual deployment and validator finality still require separate consent.
