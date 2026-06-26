# Composition With dafny-verification

Use `dafny-verification` for:

- functional equivalence;
- invariants;
- boundary conditions;
- parser/validator behavior;
- authorization/security-sensitive branches;
- local state transitions.

Use `algorithm-selection-benchmarking` for:

- workload assumptions;
- candidate algorithm/data-structure comparison;
- asymptotic tradeoffs;
- empirical benchmark evidence;
- regression performance gates.

Never claim Dafny proves runtime performance unless a specific resource-bound model has actually been encoded and verified. In normal use, Dafny proves behavior; benchmarks measure performance.

Never claim benchmark results prove correctness. A faster wrong implementation is rejected.
