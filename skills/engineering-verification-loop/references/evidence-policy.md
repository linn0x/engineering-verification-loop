# Evidence Policy

Minimum evidence by claim:

- Correctness claim: passed formal verification when modeled, plus target-language tests or differential tests.
- Go/Python implementation alignment claim: `conformance` risk with passed `model-implementation-conformance` evidence, plus declared `implementation_languages`, Go/Python `targets`, target-language checks, and a formal coverage map showing each model property has passed implementation evidence for every declared language.
- Performance claim: workload manifest, baseline/candidate metrics, threshold, and reproducibility record.
- Optimization/profile claim: measured hotspot before edit and before/after metrics after edit.
- API safety claim: baseline/candidate compatibility check and migration note for intentional breaks.
- CI fix claim: failure classification, stable signature, smallest reproduction command, structured CI footer when possible, and prevention check.
- Experiment claim: manifest, context snapshot, repeated samples, uncertainty, structured workload manifest, and structured limitations.

Evidence entries must reference artifact IDs from the bundle artifact manifest. A passed gate cannot rely only on source files; it needs a result artifact such as a test log, audit result, metrics file, profile, CI log, schema report, fixture, or coverage report. Artifact paths and string `formal_coverage_map` paths must resolve under the repository root used to run the auditor; absolute paths outside that root are invalid.

Risk labels are closed. Unknown or duplicate labels are audit failures, not warnings.

Claims are first-class. Each readiness claim should identify its `kind`, `scope`, supporting `evidence_refs`, and `workload_id` when workload-backed.

Each `claim.evidence_refs` entry must reference an artifact in the manifest and that artifact must be linked from passed specialist evidence. A claim kind with required specialists must have at least one referenced artifact attached to passed evidence from each required specialist. `implementation_conformance` claims must list non-empty `property_ids`, and each ID must exist in the formal coverage map. Coverage is per declared implementation language; Go covering `p1` and Python covering `p2` is not enough for a Go/Python conformance claim over `p1` and `p2`.

Final reports must distinguish:

- machine-checked proof;
- tested implementation alignment;
- benchmark evidence;
- profile evidence;
- compatibility evidence;
- workload validity;
- structured CI failure semantics;
- inference or unresolved assumption.

Do not let `synthetic_only` workload evidence support production impact. State it as local evidence unless replay, shadow, canary, or production data is present, and record that boundary as a structured `unsupported_claims` item scoped to `production`.
