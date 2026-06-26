# Property And Differential Test Patterns

Use these when replacing a correct but slow implementation:

- **Differential oracle**: compare the optimized implementation against the old implementation or a simple specification implementation over generated inputs.
- **Metamorphic property**: transform input in a way that preserves known output properties, then compare results.
- **Boundary sweep**: test empty, one item, duplicates, sorted, reverse-sorted, high skew, maximum/minimum values, and adversarial shapes.
- **Ordering contract**: assert whether output order is stable, sorted, unspecified, or insertion-preserving.
- **Idempotence**: verify repeated application when the operation should be idempotent, such as deduplication or normalization.
- **Set/sequence relation**: verify no missing elements, no extra elements, and multiplicity rules.
- **Failure behavior**: compare errors, panics/exceptions, and invalid input handling.

For correctness-critical logic, use `dafny-verification` for the formal contract and keep these tests as implementation-alignment checks.
