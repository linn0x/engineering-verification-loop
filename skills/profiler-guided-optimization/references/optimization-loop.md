# Optimization Loop

1. Define workload and target metric.
2. Run baseline tests and profile.
3. Pick one measured bottleneck.
4. Make one scoped change.
5. Run correctness tests.
6. Re-profile if the hot path changed.
7. Run before/after benchmark or workload measurement.
8. Keep the change only if it clears the useful threshold without critical regressions.
