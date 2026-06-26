# Conformance Policy

Required distinction:

- Formal model proof: Dafny/TLA evidence only covers the model.
- Generated implementation: stronger linkage when target code is generated from verified Dafny.
- Handwritten implementation: requires test, fuzz, fixture, or oracle evidence.
- Fixture comparison: covers recorded cases only.
- Trace comparison: required for TLA, temporal, state-machine, retry, idempotency, ordering, or concurrency behavior.

Every conformance map must list `implementation_targets`. Each target language, artifact, and entrypoint needs passed evidence for every formal property. Evidence that covers an unknown property, duplicates a property ID, omits `evidence_type`, or omits a result artifact is invalid.

Expected trace files use `expected_state`. Implementation trace files must use `observed_state` or `actual_state`; `expected_state` is not accepted as implementation output.

When `observable_projection` is set, every projected key must exist in both expected and observed states. Missing projection keys are comparison failures; they are not treated as `null`.

When `allowed_stuttering` is true, implementation traces may contain extra actual steps only when the projected observed state is unchanged. A step with the same action and input as the next expected step must still satisfy that expected state.

Generated-code evidence must include generator identity, source model hash, and generated artifact hash. Handwritten Go/Python evidence must include a structured unsupported-claims boundary stating that the implementation is tested for conformance and is not machine-checked refinement.

Final reports must state unsupported claims. Do not say handwritten Go/Python is machine-verified unless a checked refinement or generation chain actually exists.
