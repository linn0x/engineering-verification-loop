---
name: ci-regression-forensics
description: CI failure and regression forensics specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to parse structured CI failure footers, reproduce failing CI locally, classify build/test/lint/typecheck/performance failures, extract stable failure signatures, compare environments, isolate first-bad commits, or produce a minimal fix plan from logs/artifacts. Not for designing new tests, formal verification, API compatibility review, or performance optimization after the failing regression is isolated.
---

# CI Regression Forensics

## Operating Contract

Use this skill as the top-level entry point for CI failures and regressions. Do not edit code before classifying the failure, extracting the stable failure signature, and identifying the shortest credible reproduction command.

The goal is not to guess a fix from a red log. The goal is to turn noisy CI output into a classified failure, reproducible command, likely change range, and correct specialist handoff.

## Workflow

1. Gather CI logs, artifact paths, commit SHA, branch, job name, runner OS, dependency/cache state, and the command CI executed.
2. Prefer structured CI failure footers when available. Generate them with `scripts/emit-ci-failure-footer.py` from CI jobs or wrappers.
3. Validate structured CI failure footers with `scripts/validate-ci-failure-footer.py` when present.
   - generated signatures are preferred and validate without extra flags;
   - custom `--stable-signature` values require `--signature-provenance external`, `--signature-source`, and `--signature-reason`;
   - external signatures require `--allow-external-signature` plus source and reason metadata;
   - `artifact_path` must resolve to the classified log, not only share a basename.
4. Classify the failure using `scripts/classify-ci-log.py`:
   - first parse valid `ci_failure` JSON/NDJSON footers;
   - pass `--allow-external-signature` only when external signature provenance is trusted and includes source/reason metadata;
   - fall back to log-pattern classification when no valid footer exists;
   - treat low-confidence or ambiguous fallback results as requiring human review;
   - build/compile;
   - dependency resolution;
   - lint/format;
   - typecheck;
   - unit/integration/e2e test;
   - timeout;
   - OOM/resource exhaustion;
   - network/external service;
   - flaky suspicion;
   - benchmark/performance regression;
   - schema/API compatibility;
   - formal verification/model-checking.
5. Extract a stable signature using `scripts/extract-failure-signature.py` unless a trusted footer already provided one.
6. Build the smallest local reproduction command. Do not start with the whole CI pipeline if a targeted command is visible.
7. Collect local diagnostics with `scripts/collect-local-diagnostics.sh`.
8. Compare CI vs local environment with `scripts/compare-ci-env.py` when structured environment data exists.
9. If the culprit range is unclear and the repo history allows it, run `scripts/run-bisect.sh`.
10. Decide the handoff:
   - Dafny verification failure -> `dafny-verification`;
   - TLA model check failure -> `tla-distributed-model-checking`;
   - property-test seed failure -> `property-based-differential-testing`;
   - benchmark/performance regression -> `algorithm-selection-benchmarking` or `profiler-guided-optimization`;
   - API/schema compatibility failure -> `api-contract-compatibility`;
   - experiment drift -> `reproducible-experiment-analysis`.
11. Make the minimal fix only after the failure class and reproduction path are clear.
12. Report:
    - classification;
    - structured footer status and warnings;
    - stable signature;
    - repro command;
    - environment deltas;
    - first bad commit if found;
    - fix or specialist handoff;
    - prevention test/check.

## Boundaries

This skill owns CI triage, log classification, failure signatures, local reproduction, environment comparison, flaky suspicion, and bisect discipline.

This skill does not own broad test strategy, algorithm redesign, formal proof repair, API compatibility review, or profiling beyond detecting that a regression is performance-related.

## Resources

- `scripts/classify-ci-log.py`: classify logs into stable failure categories and emit JSON or text summary.
- `scripts/emit-ci-failure-footer.py`: emit stable `ci_failure` JSON footer for CI jobs or wrappers.
- `scripts/validate-ci-failure-footer.py`: validate footer enum, route, signature, exit code, and artifact consistency.
- `scripts/extract-failure-signature.py`: extract normalized failure signatures with stable hashes.
- `scripts/collect-local-diagnostics.sh`: collect local git, OS, toolchain, and environment metadata without secrets.
- `scripts/compare-ci-env.py`: compare two JSON environment snapshots.
- `scripts/run-bisect.sh`: guarded wrapper for `git bisect run`.
- `references/ci-forensics-playbook.md`: disciplined diagnosis workflow.
- `references/flakiness-classification.md`: flaky-vs-real heuristics.
- `references/bisect-discipline.md`: safe bisect rules.
- `references/handoff-routing.md`: specialist skill routing table.
- `assets/templates/`: forensics report, repro command, and signature JSON templates.
