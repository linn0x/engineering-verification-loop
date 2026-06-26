# Benchmark Discipline

Do not optimize without a workload model and baseline.

Minimum benchmark record:

- command;
- git SHA and dirty status;
- machine/runtime metadata;
- dataset/input generator;
- input sizes;
- input distribution;
- warmup or iteration settings when the framework supports them;
- baseline result;
- candidate result;
- decision threshold.

Interpretation rules:

- Treat one-off timing from a shell command as a smoke signal, not proof.
- Prefer the language ecosystem's benchmark tooling: Go `testing.B`, Rust Criterion, JVM JMH, Python `pytest-benchmark` or a stable project-native harness.
- Compare the same binary/configuration class unless the task is explicitly about build/runtime configuration.
- Do not mix correctness failures with performance decisions. Correctness failures reject the candidate before benchmark interpretation.
- If results are noisy, reduce noise or report inconclusive; do not cherry-pick the best run.
- Report memory/allocation changes when the optimization could shift pressure from CPU to memory.
