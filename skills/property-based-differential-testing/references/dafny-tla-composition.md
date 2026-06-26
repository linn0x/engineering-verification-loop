# Composition With Dafny And TLA+

Use `dafny-verification` for formal local contracts and invariants. Use this skill to check target-language implementation alignment against those contracts across generated cases.

Use `tla-distributed-model-checking` for global protocol traces and failure scenarios. Use this skill to replay counterexamples, test local handlers, and generate operation sequences derived from the model.

Use `algorithm-selection-benchmarking` when a candidate is faster. Use this skill before accepting the candidate to compare behavior against the old implementation or a simple oracle.

Do not claim property-based tests prove full correctness. They are falsification and regression tools.
