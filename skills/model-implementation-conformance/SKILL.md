---
name: model-implementation-conformance
description: Model-to-implementation conformance specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to map Dafny or TLA model properties to Go/Python implementation evidence, audit model-to-code conformance, compare model-exported fixtures or oracle traces against implementation output, or distinguish formal model proof from handwritten implementation alignment.
---

# Model Implementation Conformance

## Operating Contract

Use this skill after a Dafny/TLA model has verified or model-checked properties and Go/Python implementation evidence must show alignment. Do not claim handwritten Go/Python is machine-verified by Dafny/TLA unless it is generated from the model or has an explicit checked refinement.

This skill owns conformance evidence. It does not repair proofs, design the original model, choose algorithms, or profile performance.

## Workflow

1. Identify formal artifacts:
   - Dafny files and verified lemmas/predicates;
   - TLA specs, invariants, traces, or model-checking outputs.
2. List formal properties with stable IDs.
3. List every Go/Python implementation target, artifact, and public entrypoint.
4. For each Go/Python implementation, map every property to evidence:
   - generated code artifact;
   - fixture or oracle trace;
   - differential test;
   - fuzz or property test corpus;
   - golden case or regression test.
5. Audit the map with `scripts/audit-conformance-map.py`.
6. When fixtures exist, compare expected model output and implementation output with `scripts/compare-fixture-results.py`.
7. For TLA, temporal, state-machine, retry, idempotency, or ordering behavior, compare traces with `scripts/compare-trace-results.py`.
8. Report the exact boundary:
   - model proof;
   - generated implementation linkage;
   - tested handwritten conformance;
   - unsupported claims.

## Go/Python Defaults

Go evidence normally includes `go test ./...`; use `go test -race ./...` when concurrency matters, fuzz/differential corpus for parsers/stateful/algorithm logic, `go test -bench=. -benchmem` for performance claims, and `pprof` artifacts for profile claims.

Python evidence normally includes `pytest`; use Hypothesis or deterministic generated cases, differential tests against model fixtures/oracles, `pytest-benchmark` or stable benchmark harness for performance claims, and `cProfile`, `py-spy`, or `scalene` artifacts for profile claims.

## Evidence Boundary

- Dafny proof = model proof.
- Go generated from Dafny = stronger implementation linkage.
- Handwritten Go/Python = conformance-tested, not machine-checked refinement.
- Fixture equality = evidence over covered cases, not exhaustive proof.
- Trace equality = evidence over projected observable states, not complete distributed-system proof.

## Resources

- `scripts/audit-conformance-map.py`: verify every formal property has passed Go/Python implementation evidence.
- `scripts/compare-fixture-results.py`: compare model-exported expected JSONL with implementation actual JSONL.
- `scripts/compare-trace-results.py`: compare model traces with implementation observed traces.
- `references/conformance-policy.md`: evidence levels and reporting rules.
- `references/go-python-conformance.md`: Go/Python-specific guidance.
- `assets/templates/conformance-map.json`: conformance map template.
- `assets/templates/model-fixtures.jsonl`: JSONL fixture template.
- `assets/templates/model-traces.jsonl`: trace fixture template.
- `assets/templates/implementation-traces.jsonl`: observed implementation trace template.
- `assets/templates/conformance-report.md`: report template.
