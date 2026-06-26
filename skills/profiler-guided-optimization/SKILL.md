---
name: profiler-guided-optimization
description: Profiler-guided performance optimization specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to optimize latency, throughput, CPU, memory, allocation, I/O, startup time, or hot-path runtime behavior only after identifying measured bottlenecks with profiler evidence and to verify before/after performance after editing.
---

# Profiler-Guided Optimization

## Operating Contract

Use this skill when performance is the target and the bottleneck is not already proven. Do not optimize from intuition. Do not claim an optimization helped unless a representative workload, profile artifact, and before/after measurement exist.

Profiling identifies where time, CPU, allocation, memory, lock contention, or I/O is spent. Benchmarking verifies whether a change actually improves the target metric.

## Workflow

1. Define the workload and performance target:
   - endpoint, batch job, algorithm, parser, query, UI interaction, or service path;
   - input distribution and scale;
   - latency, throughput, CPU, memory, allocation, startup, or I/O goal.
2. Establish correctness guardrails before editing:
   - existing tests;
   - `property-based-differential-testing` for behavior-preserving rewrites;
   - `dafny-verification` for critical local invariants.
3. Run the baseline workload and profiler with `scripts/run-profile.sh`.
4. Extract hotspots:
   - Python `cProfile`: `scripts/summarize-cprofile.py`;
   - other ecosystems: use project-native profilers and record commands/artifacts.
5. Select one bottleneck-backed change. Prefer the smallest change that attacks a measured hotspot.
6. Keep algorithm replacement decisions in `algorithm-selection-benchmarking` when the fix changes the data structure or asymptotic strategy.
7. Run tests after the change.
8. Run the same workload again and compare before/after metrics with `scripts/compare-optimization-metrics.py` or project-native benchmark output.
9. Reject the change if:
   - the hotspot was not measured;
   - the workload is not representative;
   - correctness guardrails fail;
   - performance gain is below the useful threshold;
   - another critical metric regresses.
10. Final output must include workload, profile command, artifact paths, top hotspots, change made, tests, before/after metrics, thresholds, and remaining bottlenecks.

## Profiler Choice

| Target | Preferred evidence |
| --- | --- |
| Python CPU | `cProfile`, `py-spy`, `scalene` |
| Node.js CPU | `node --prof`, Chrome DevTools CPU profile |
| Go CPU/memory | `go test -bench`, `pprof` |
| Rust CPU | `cargo bench`, `perf`, `samply`, `flamegraph` |
| JVM CPU/allocation | JFR, async-profiler |
| SQL/I/O | query plan, trace, request timing, DB metrics |
| Frontend runtime | browser performance trace, React profiler |

## Common Failure Modes

- Optimizing code that is not on the hot path.
- Measuring a toy input while claiming production impact.
- Changing several factors before rerunning the profile.
- Reporting faster wall time without correctness tests.
- Ignoring memory/allocation regressions after CPU wins.
- Treating profiler overhead as benchmark evidence.

## Resources

- `scripts/run-profile.sh`: record and run a project-native profiler command under `.profiles/`.
- `scripts/summarize-cprofile.py`: summarize Python `cProfile` `.prof` files.
- `scripts/compare-optimization-metrics.py`: compare before/after performance samples from CSV or JSON.
- `references/profiler-selection.md`: profiler selection by ecosystem.
- `references/bottleneck-triage.md`: how to interpret hotspot evidence.
- `references/optimization-loop.md`: disciplined before/after loop.
- `references/correctness-guardrails.md`: tests and formal checks before optimization.
- `assets/templates/`: profile plan, profile report, and metrics CSV templates.
