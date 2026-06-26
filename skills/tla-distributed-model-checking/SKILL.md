---
name: tla-distributed-model-checking
description: TLA+/PlusCal distributed model-checking specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to model or check safety/liveness under asynchronous message ordering, retries, duplication, loss, network partitions, quorum behavior, leader election, replication, clock skew, crash-stop, crash-recovery, or consensus-style nondeterminism. Not for local Dafny proof repair, ordinary single-process state machines, algorithm performance optimization, production chaos testing, or generic distributed-systems advice.
---

# TLA+ Distributed Model Checking

## Operating Contract

Use this skill for protocol-level behavior under nondeterminism and failure semantics. Model checking a finite TLA+ configuration is not the same as proving the production implementation correct. Always report the checked model, constants, bounds, fairness assumptions, invariants, liveness properties, state counts, and unmodeled environment assumptions.

Use `dafny-verification` for local deterministic handlers, message validators, storage-record transitions, parsers, authorization checks, and implementation-level invariants derived from the protocol model.

## Workflow

1. Read the protocol requirement, existing implementation, tests, docs, and any Dafny model.
2. Decide whether this is truly distributed-protocol work. Use this skill for partitions, clocks, async ordering, quorum, leader election, replication, retries, crash/recovery, or consensus-style nondeterminism. Use `dafny-verification` alone for deterministic business state machines.
3. Extract the protocol model:
   - node identities;
   - persistent state;
   - volatile state;
   - message types;
   - network state;
   - environment actions;
   - failure/recovery actions;
   - clock/timeout abstractions.
4. Define the failure model explicitly: reliable network, lossy network, duplicate messages, reordering, partition/heal, crash-stop, crash-recovery, bounded clock skew, and whether Byzantine faults are out of scope.
5. Define safety properties first: agreement, validity, integrity, monotonicity, no double-commit, no stale read beyond the stated consistency model, no split brain, and durable-state invariants.
6. Define liveness/progress properties only with explicit fairness and environment assumptions.
7. Create or update files under `formal/tla/`:
   - `<Protocol>.tla`;
   - `<Protocol>.cfg`;
   - optional alternate configs for different bounds or failure modes.
8. Keep the model finite and inspectable: small node counts, bounded message sets, bounded terms/epochs, bounded clocks/timeouts, and explicit constants in `.cfg`.
9. Run `scripts/check-tla.sh formal/tla/<Protocol>.tla`.
10. If model checking fails, classify the issue as real protocol bug, model bug, missing type invariant, overly strong invariant, unjustified environment constraint, state-space explosion, or liveness/fairness issue.
11. Preserve useful counterexamples. Do not silence failures by constraining the scheduler/network beyond the real system.
12. Extract implementation obligations: local transition pre/postconditions, message validation, persistence ordering, idempotency, timeout assumptions, retry behavior, and clock assumptions.
13. Compose with `dafny-verification` for local deterministic obligations.
14. Add target-language tests where possible: trace replay from counterexamples, property tests for handlers, and deterministic simulations for failure scenarios.
15. In the final answer, report TLA+ files changed, configs checked, constants/bounds, safety properties, liveness/fairness assumptions, command summary, counterexamples, Dafny handoff obligations, and assumptions not covered.

## Boundaries

This skill owns protocol-level models, asynchronous scheduling, message ordering/loss/duplication, partitions, crash/recovery assumptions, clocks/timeouts, quorum behavior, leader election, replication consistency, finite-state model-checking configurations, and counterexample analysis.

This skill does not own target-language implementation correctness, local Dafny proof repair, algorithm benchmarking, production observability, chaos testing execution, or full unbounded theorem proving unless explicitly requested and supported by a separate proof workflow.

## Resources

- `scripts/check-tla.sh`: run TLC for `.tla` files with matching `.cfg` files, optionally run Apalache when `APALACHE=1`.
- `scripts/summarize-tlc.py`: extract state counts, depth, failures, deadlock status, and runtime hints from TLC logs.
- `references/tla-patterns.md`: compact modeling patterns.
- `references/distributed-failure-models.md`: failure model matrix.
- `references/safety-liveness-patterns.md`: property patterns and liveness cautions.
- `references/consensus-boundaries.md`: consensus-specific scope rules.
- `references/dafny-composition.md`: handoff from global protocol model to local Dafny obligations.
- `references/examples/`: small TLC-oriented examples.
- `assets/templates/`: protocol model plan, failure model, report, and Dafny handoff templates.

Prefer TLC as the default checker. Use Apalache as an optional additional checker for bounded symbolic checks or inductiveness workflows, not as an unexamined replacement for TLC.
