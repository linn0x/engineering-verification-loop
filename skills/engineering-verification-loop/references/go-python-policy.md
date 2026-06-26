# Go/Python Policy

## Boundaries

- Dafny proof is model proof.
- Go generated from Dafny has stronger implementation linkage than handwritten Go.
- Handwritten Go/Python needs conformance evidence; it is not machine-checked refinement.
- Python is conformance-tested against fixtures, oracle traces, or differential properties.

## Go Default Evidence

- `go test ./...`
- `go test -race ./...` when concurrency matters
- fuzz or differential corpus for stateful, parser, validator, or algorithm logic
- `go test -bench=. -benchmem` for performance claims
- `pprof` CPU/memory artifact for profile claims
- target semantics for model links: integer width, overflow policy, nil/slice mutation policy, and goroutine interleaving assumptions when relevant

## Python Default Evidence

- `pytest`
- `hypothesis` or deterministic generated cases
- differential tests against oracle/model fixtures
- `pytest-benchmark` or a stable project benchmark for performance claims
- `cProfile`, `py-spy`, or `scalene` artifact for profile claims
- target semantics for model links: integer domain, `None` policy, mutation policy, and exception policy

## Formal Coverage Map

For each model property, record implementation evidence with:

- property ID, formal artifact, formal symbol, property kind, preconditions, model semantics, and implementation obligations;
- language;
- implementation artifact and public entrypoint;
- evidence type;
- test command;
- result artifact path;
- status;
- covered property IDs;
- case count, seed, oracle artifact, and known gaps when applicable.

Unknown property coverage, duplicate property IDs, and missing target-language evidence are audit failures.
