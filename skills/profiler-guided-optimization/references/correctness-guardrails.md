# Correctness Guardrails

- Run existing tests before and after optimization.
- Add differential tests when replacing an implementation with a faster equivalent.
- Add property-based tests for broad input spaces and edge cases.
- Use `dafny-verification` when preserving local invariants is correctness-critical.
- Do not trade correctness for speed unless the user explicitly changes the product requirement.
