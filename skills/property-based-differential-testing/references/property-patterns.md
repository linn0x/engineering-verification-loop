# Property Test Patterns

- Differential oracle: compare optimized implementation against a simple implementation, old implementation, or reference library.
- Metamorphic relation: transform input while preserving a known output relation, such as sorting after permutation or parsing after whitespace normalization.
- Stateful model: generate operation sequences and compare concrete state to an abstract model.
- Boundary sweep: generate empty, singleton, duplicate-heavy, sorted, reverse-sorted, skewed, min/max, malformed, and adversarial cases.
- Error equivalence: compare not only outputs but also failure modes, error codes, panics/exceptions, and validation messages when observable.
- Seed replay: every failure must include a deterministic replay command or seed.
- Regression capture: turn every meaningful generated failure into a fixed unit/regression test.
