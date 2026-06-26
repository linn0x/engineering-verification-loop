---
name: engineering-verification-loop
description: Top-level engineering verification orchestration skill and distributable skill-pack entry point. Use when Codex must plan, execute, or review a Go/Python-heavy engineering change that spans correctness, model-to-implementation conformance, algorithm selection, performance, API/schema compatibility, CI failures, profiling, distributed behavior, or experiment claims and needs routing through specialist verification skills with an auditable evidence bundle.
---

# Engineering Verification Loop

## Operating Contract

Use this skill as a thin orchestration layer. Classify the change, route each risk to the right specialist skill, enforce entry/exit gates, and produce one evidence bundle. Do not duplicate specialist procedures; load the specialist skill when that gate is active.

Do not claim a change is ready when any active risk lacks passed evidence. Unsupported claims are structured limitations; they do not make a readiness claim true.

For Go/Python implementation work, require explicit model-to-implementation conformance evidence. Dafny/TLA proof is model evidence; handwritten Go/Python needs fixtures, fuzz, differential tests, or generated-code linkage before implementation alignment can be claimed.

## Risk Routing

| Risk or symptom | Required specialist |
| --- | --- |
| Functional invariant, parser/validator, auth, state transition | `dafny-verification` |
| Optimized implementation must match oracle/model | `property-based-differential-testing` |
| Algorithm/data-structure choice, benchmarked candidate | `algorithm-selection-benchmarking` |
| OpenAPI, JSON Schema, Protobuf, GraphQL, SDK surface | `api-contract-compatibility` |
| CI failure, noisy log, regression reproduction | `ci-regression-forensics` |
| Experiment/benchmark claim needs reproducibility | `reproducible-experiment-analysis` |
| Hot path, CPU/memory/allocation/I/O optimization | `profiler-guided-optimization` |
| Dafny/TLA model must be mapped to Go/Python implementation evidence | `model-implementation-conformance` |
| Distributed protocol semantics | `tla-distributed-model-checking` |

## Workflow

1. Classify the change:
   - correctness-critical;
   - algorithmic/performance-sensitive;
   - API/schema/public contract;
   - experiment or benchmark claim;
   - CI failure/regression;
   - distributed protocol behavior.
2. Build a verification plan with active risk labels, specialist skills, commands/artifacts expected, and stop conditions.
3. Run gates in dependency order:
   - correctness spec/proof before implementation when applicable;
   - algorithm choice before profiling when the algorithm is unknown;
   - differential/property tests before accepting optimized behavior;
   - API compatibility before claiming contract safety;
   - reproducibility audit before trusting experiment conclusions;
   - profiling after a representative workload exposes a bottleneck;
   - CI forensics first when the entry point is a failing job.
   - model-to-implementation conformance before claiming handwritten Go/Python matches a verified model.
4. Stop and reroute when a gate fails. Do not continue to later claims as if earlier evidence passed.
5. Assemble an evidence bundle using `assets/templates/evidence-bundle.json`.
6. Audit the bundle with `scripts/audit-evidence-bundle.py`.
7. Final answer must include active risks, specialist skills used, commands, artifact paths, pass/fail status, unsupported claims, and next gate if blocked.

## Decision Rules

- If correctness and performance both matter, prove/model critical properties and add differential tests before interpreting speedups.
- If an API check fails in CI, use `ci-regression-forensics` to classify and reproduce, then hand the compatibility issue to `api-contract-compatibility`.
- If benchmark results support a product/research claim, route through `reproducible-experiment-analysis`; raw benchmark output alone is insufficient.
- If the bottleneck is not measured, do not optimize; use `profiler-guided-optimization`.
- If a change modifies distributed semantics, use `tla-distributed-model-checking`; Dafny may still verify local deterministic handlers.
- If Go/Python code is handwritten against a Dafny/TLA model, include `conformance` risk and route through `model-implementation-conformance`.
- If an `implementation_conformance` claim exists, declare `implementation_languages`, Go/Python `targets`, and language checks; do not let the claim stand without target-language gates.
- If a benchmark uses synthetic inputs, do not claim production impact unless replay, canary, shadow, or production evidence also exists.
- If CI is an active risk, require a structured CI failure footer or a structured `unsupported_claims` limitation scoped to `ci-observability`.

## Evidence Bundle Schema

The bundle is JSON:

- `change_summary`: short description.
- `risks`: active risk labels: `correctness`, `conformance`, `algorithm`, `performance`, `api`, `ci`, `experiment`, `profile`, `distributed`.
- `targets`: Go/Python changed implementation targets and entrypoints.
- `implementation_languages`: `go`, `python`, or both when target code is in those languages.
- `formal_coverage_map`: model properties mapped to Go/Python evidence, or a repo-root-contained path to that JSON. Each declared implementation language must cover each claimed property.
- `workloads`: structured workload manifests with `synthetic_only`, `replay`, `shadow`, `canary`, or `production` level.
- `claims`: structured readiness/performance/conformance claims linked to evidence and workloads.
- `ci_structured_footer`: whether CI emitted a machine-readable failure footer.
- `artifacts`: manifest of result artifacts with `id`, `path`, `kind`, `sha256`, `producer_command`, and `exit_code`.
- `evidence`: object keyed by risk label. Each item needs `skill`, `command`, `status`, `artifact_refs`, and `summary`.
- `unsupported_claims`: structured limitations with `scope`, `disposition`, and related fields.

Use `scripts/audit-evidence-bundle.py <bundle.json>` as the final gate.
Use `--repo-root <path>` when running outside the repository root; otherwise the auditor derives the git root and resolves artifact paths against it.

## Boundaries

This skill coordinates. It does not repair Dafny proofs, design generators, interpret flamegraphs in depth, fix CI, write OpenAPI compatibility policy, or prove experiments. Those tasks belong to the named specialist skills.

## Resources

- `scripts/audit-evidence-bundle.py`: fail closed when active risks lack passed specialist evidence.
- `scripts/infer-go-python-targets.py`: infer Go/Python targets from changed file lists.
- `references/risk-routing-matrix.md`: expanded routing and gate order.
- `references/evidence-policy.md`: required evidence by claim type.
- `references/go-python-policy.md`: Go/Python-specific proof, conformance, benchmark, and profile policy.
- `assets/templates/evidence-bundle.json`: machine-readable evidence bundle template.
- `assets/templates/formal-coverage-map.json`: model-to-implementation mapping template.
- `assets/templates/workload-validity.json`: structured workload and claims template.
- `assets/templates/go-language-checks.json`: Go minimum gate examples.
- `assets/templates/python-language-checks.json`: Python minimum gate examples.
- `assets/templates/verification-plan.md`: concise plan template.
- `assets/templates/final-report.md`: final report template.
