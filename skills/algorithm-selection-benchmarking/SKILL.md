---
name: algorithm-selection-benchmarking
description: Algorithm and data-structure selection specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to choose, replace, or evaluate algorithms or data structures under latency, throughput, memory, asymptotic-complexity, or benchmark-regression constraints, especially when a Dafny-backed correctness model exists but the target Go/Python implementation must be efficient. Not for formal proof, distributed protocol semantics, network partitions, clocks, consensus, broad infrastructure tuning, or generic refactoring.
---

# Algorithm Selection & Benchmarking

## Operating Contract

Use this skill to choose and validate faster algorithms or data structures without weakening correctness. Do not claim a change is faster unless benchmark evidence was produced. Do not claim a change is correct merely because it is faster.

Use `dafny-verification` for correctness-critical functional equivalence, invariants, parsers, validators, authorization logic, and local state transitions. This skill owns workload modeling, complexity tradeoffs, benchmark evidence, profiling discipline, and performance regression gates.

## Workflow

1. Read the existing implementation, tests, requirements, and any Dafny model before editing.
2. Extract the functional contract that must not change.
3. Define the performance target:
   - input size range;
   - input distribution;
   - latency, throughput, memory, allocation, or complexity target;
   - mutation/read ratio;
   - concurrency assumptions;
   - target runtime and deployment environment.
4. Establish a baseline:
   - run existing tests;
   - run or create a benchmark for the current implementation;
   - record command, git revision, runtime metadata, and machine metadata when practical.
5. Build a candidate matrix:
   - current algorithm/data structure;
   - candidate alternatives;
   - asymptotic time and space;
   - constant-factor concerns;
   - edge cases;
   - implementation risk;
   - correctness obligations.
6. If the logic is correctness-critical, compose with `dafny-verification` before or during implementation:
   - prove the abstract contract;
   - prove equivalence of candidate logic when practical;
   - otherwise document the manual alignment boundary.
7. Implement the smallest candidate that plausibly satisfies the target.
8. Add property or differential tests comparing old vs new behavior, implementation vs simple oracle, or implementation vs Dafny-modeled behavior.
9. Run tests and benchmarks.
10. Profile only after a benchmark identifies a bottleneck. Profiling does not replace a workload model.
11. Keep the simplest candidate that satisfies the target.
12. Add a regression benchmark command or metric threshold.
13. In the final answer, report performance target, baseline result, candidate result, benchmark command, correctness tests, Dafny verification status if used, assumptions, and non-goals.

## Boundaries

This skill is appropriate for local algorithm and data-structure choices: sorting, searching, indexing, deduplication, aggregation, caching policy, interval operations, matching, batching, memory layout, and hot-path local computation.

Do not use this skill as the primary tool for:

- Dafny proof repair;
- distributed protocol semantics;
- network partitions, clocks, leader election, quorum behavior, or consensus;
- broad database/index/infrastructure tuning;
- speculative micro-optimization without a benchmark;
- generic refactoring with no measurable performance constraint.

## Resources

- `scripts/run-benchmarks.sh`: run a user-supplied benchmark command and save metadata-rich logs under `.benchmarks/`.
- `scripts/compare-metrics.py`: compare baseline and candidate metrics from CSV and fail on configured regression thresholds.
- `references/algorithm-selection-checklist.md`: questions for workload, distribution, complexity, and correctness risk.
- `references/benchmark-discipline.md`: rules for reliable benchmark interpretation.
- `references/property-test-patterns.md`: differential/property test patterns for optimized algorithms.
- `references/dafny-composition.md`: how to compose this skill with `dafny-verification`.
- `assets/templates/`: benchmark plan, decision record, and metrics CSV templates.

Prefer project-native benchmark tooling, but require explicit commands and recorded outputs.
