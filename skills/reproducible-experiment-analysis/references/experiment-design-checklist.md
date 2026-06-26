# Experiment Design Checklist

- State the hypothesis before reading the result.
- Identify baseline and candidate revisions/configs.
- Freeze dataset, traffic slice, fixtures, or input generator seed.
- Define each metric name, unit, direction, and minimum useful effect.
- Record warmup, cache state, concurrency, batch size, and timeout policy.
- Use repeated runs unless the measurement is deterministic by construction.
- Keep exploratory analysis separate from confirmation runs.
- Change one intended factor at a time for ablations.
