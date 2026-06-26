---
name: reproducible-experiment-analysis
description: Reproducible experiment and benchmark analysis specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to audit experiment results, benchmark reports, ablations, model metrics, algorithm comparisons, rollout measurements, or research claims that need reproducible commands, fixed inputs, captured environments, seeds, repeated runs, statistical uncertainty, workload-validity evidence, or falsifiable conclusions.
---

# Reproducible Experiment Analysis

## Operating Contract

Use this skill to turn an experiment claim into an auditable artifact. Do not accept a conclusion unless the input snapshot, command, environment, metric definition, repetitions, and uncertainty are recorded.

Fail closed when the evidence cannot distinguish a real effect from missing provenance, one-off noise, changed data, changed code, or post-hoc metric selection.

## Workflow

1. Identify the claim:
   - improvement, regression, no-regression, ablation effect, model-quality delta, cost reduction, or latency/throughput change.
2. Identify immutable inputs:
   - dataset or fixture snapshot;
   - git revision and diff state;
   - config and feature flags;
   - random seeds;
   - dependency lockfiles;
   - hardware/runtime where relevant.
3. Capture context with `scripts/capture-experiment-context.sh` before rerunning.
4. Require a manifest and audit it with `scripts/audit-experiment-manifest.py`.
5. Reproduce the command from a clean checkout or clean environment when practical.
6. Require repeated runs unless the measurement is deterministic by construction.
7. Compare metric samples with `scripts/compare-metric-runs.py`; report confidence intervals, sample counts, and noise.
8. Separate exploratory analysis from confirmatory claims. A post-hoc discovery needs a fresh confirmation run.
9. Compose with other skills:
   - `algorithm-selection-benchmarking` for algorithm choices and benchmark harnesses;
   - `profiler-guided-optimization` for bottleneck evidence after an experiment exposes a performance problem;
   - `property-based-differential-testing` for behavioral equivalence;
   - `ci-regression-forensics` when CI produces conflicting experiment results.
10. Final output must include claim, exact commands, immutable inputs, context artifact path, metric definition, sample count, uncertainty, reproduced result, and unsupported claims.

## Evidence Bar

| Claim | Minimum evidence |
| --- | --- |
| No regression | Baseline/candidate samples, direction, threshold, no likely regression, captured context |
| Improvement | Same as no-regression plus confidence interval supporting minimum useful effect |
| Ablation effect | Only one intended factor changed, same dataset/config, repeated samples |
| Model-quality result | Frozen eval set, metric definition, seed handling, confidence or bootstrap interval |
| Cost/latency result | Workload distribution, warmup policy, hardware/runtime, repeated measurements |

## Common Failure Modes

- One run is treated as evidence.
- Dataset, traffic slice, or random seed changed between baseline and candidate.
- The metric was chosen after inspecting results.
- Mean is reported without distribution, variance, or outliers.
- A benchmark result is mixed with unrelated code/config changes.
- Dependency or hardware changes are not captured.

## Resources

- `scripts/capture-experiment-context.sh`: write a machine/git/runtime context JSON file.
- `scripts/audit-experiment-manifest.py`: fail closed on missing manifest fields.
- `scripts/compare-metric-runs.py`: compare repeated metric samples from CSV/JSON with bootstrap confidence intervals.
- `references/experiment-design-checklist.md`: required design questions.
- `references/statistical-interpretation.md`: interpreting repeated metrics and uncertainty.
- `references/reproducibility-threats.md`: common threats to validity.
- `references/reporting-policy.md`: final-report requirements.
- `assets/templates/`: manifest, metrics CSV, and report templates.
