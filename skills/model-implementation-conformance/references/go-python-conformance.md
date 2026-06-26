# Go/Python Conformance

Go evidence:

- `go test ./...`
- `go test -race ./...` when concurrency matters
- fuzz/differential corpus for parser, validator, stateful, or algorithmic logic
- generated Go artifact when using Dafny's Go backend
- integer width, overflow, nil/slice mutation, pointer aliasing, and goroutine interleaving semantics when the model assumes mathematical values or sequential behavior

Python evidence:

- `pytest`
- Hypothesis or deterministic generated cases
- differential tests against fixtures/oracles
- JSONL fixture comparison for model-exported input/output cases
- trace comparison for stateful/TLA behavior
- integer domain, `None`, mutation, and exception policy semantics

For both languages, each formal property ID and each target entrypoint must map to at least one passed implementation evidence item.
