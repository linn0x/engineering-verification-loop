# Algorithm Selection Checklist

Ask these before changing an implementation:

- What is the actual input scale now and in the expected growth case?
- What distribution matters: random, sorted, adversarial, skewed, sparse, dense, bursty, or repeated?
- Is the operation batch, streaming, online, incremental, interactive, or background?
- Is the bottleneck CPU, memory, allocation, I/O, lock contention, cache locality, or algorithmic complexity?
- Which observable behavior cannot change: ordering, tie-breaking, rounding, overflow, errors, concurrency semantics, or side effects?
- Can a simple slow oracle be used for differential testing?
- Is the candidate sensitive to data skew, hash collision behavior, numeric precision, or pathological inputs?
- Does the target need p50, p95, p99, throughput, memory, allocation count, or asymptotic improvement?
- Is the target environment stable enough for benchmarks to be meaningful?
- What benchmark threshold will decide whether the candidate is accepted?
