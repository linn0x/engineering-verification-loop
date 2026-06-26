# Handoff Routing

| Failure type | Handoff |
|---|---|
| Dafny verification/audit failure | `dafny-verification` |
| TLA/TLC invariant or model failure | `tla-distributed-model-checking` |
| Generated seed/counterexample failure | `property-based-differential-testing` |
| Benchmark or performance regression | `algorithm-selection-benchmarking` |
| Hotspot/profile diagnosis after regression isolation | `profiler-guided-optimization` |
| OpenAPI/JSON Schema/Protobuf contract break | `api-contract-compatibility` |
| Experiment result drift | `reproducible-experiment-analysis` |
| Ordinary unit failure | fix locally after reproduction and signature extraction |
| External service/network failure | isolate dependency or add retry/mock/pin as appropriate |
