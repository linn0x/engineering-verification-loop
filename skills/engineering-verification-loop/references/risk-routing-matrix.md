# Risk Routing Matrix

| Trigger | First gate | Follow-up gate |
| --- | --- | --- |
| Correctness-critical behavior | `dafny-verification` | `property-based-differential-testing` for target implementation alignment |
| Algorithm replacement | `algorithm-selection-benchmarking` | `property-based-differential-testing`, then `reproducible-experiment-analysis` if claiming improvement |
| Hot-path performance issue | `profiler-guided-optimization` | `algorithm-selection-benchmarking` if the fix changes algorithm/data structure |
| Public API/schema change | `api-contract-compatibility` | `ci-regression-forensics` if surfaced as CI failure |
| Red CI job | `ci-regression-forensics` | Route by classification |
| Benchmark/experiment claim | `reproducible-experiment-analysis` | `profiler-guided-optimization` if bottleneck explanation is needed |
| Distributed protocol behavior | `tla-distributed-model-checking` | `dafny-verification` for local deterministic handlers |

Gate order is not chronological ceremony; it prevents invalid claims. A failed earlier gate invalidates later acceptance claims until resolved.
