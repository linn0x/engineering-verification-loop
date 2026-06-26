# Profiler Selection

- Use CPU profilers for hot loops, serialization, parsing, routing, and algorithmic work.
- Use allocation/memory profilers for GC pressure, peak RSS, object churn, and leaks.
- Use tracing for I/O waits, RPC fanout, lock contention, scheduler gaps, and frontend interactions.
- Prefer production-like profilers for production-only bottlenecks; synthetic profilers are acceptable for local hot paths.
- Record profiler overhead separately from benchmark measurements.
