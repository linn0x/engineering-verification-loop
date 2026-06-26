# Reproducibility Threats

- Code revision changed without recording the diff.
- Dependency lockfile changed between runs.
- Dataset snapshot was regenerated or filtered differently.
- Random seed was omitted or reused inconsistently.
- Warm cache was compared to cold cache.
- Hardware, runtime, or feature flags differed.
- Metrics were selected after inspecting many outputs.
- Failed or timed-out runs were silently excluded.
