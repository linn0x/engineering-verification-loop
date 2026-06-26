---
name: dafny-verification
description: Dafny formal model verification specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to create, modify, debug, or review Dafny `.dfy` models, prove properties before implementation, repair Dafny verifier failures, or work on authorization/access control, tenant isolation, state machines, parsers, validators, algorithmic correctness, invariants, security-sensitive branching, or target-language code that should be backed by machine-checked Dafny specifications.
---

# Dafny Verification

## Operating Contract

Use Dafny 4+ as the source of truth for correctness-critical behavior. Do not implement target-language code first unless the user explicitly asks only for exploratory review of existing code. When implementation is required, write or update the Dafny model first, verify and audit it, then keep target-language code structurally aligned with the verified logic.

Do not claim that a property is verified unless `scripts/verify-dafny.sh` passed on the relevant Dafny files in this workspace.

Do not claim that hand-written target-language code is machine-verified merely because it mirrors a verified Dafny model. Unless the target code is generated from Dafny or connected by a checked refinement/equivalence proof, claim only that the target implementation is manually aligned with the verified model and tested against mirrored properties.

## Composition Boundaries

Dafny verifies functional correctness properties of modeled code. It is not a runtime performance optimizer and does not choose algorithms or data structures. If the task asks Codex to improve latency, throughput, memory use, asymptotic complexity, or algorithm/data-structure choice, use `algorithm-selection-benchmarking` for workload modeling and benchmark evidence, and use this skill only for correctness-critical functional equivalence, invariants, and boundary cases.

Dafny is also not the primary tool for full distributed-system protocol behavior involving network partitions, clock skew, crash/recovery, consensus, quorum behavior, or asynchronous message ordering. If those concerns are central, use `tla-distributed-model-checking` for the protocol model. Use this skill afterward for local deterministic handlers, message validators, storage transitions, parsers, authorization checks, and implementation-level invariants derived from the protocol model.

Never claim that:

- Dafny proves runtime performance unless an explicit resource-bound model was actually verified;
- Dafny alone proves distributed protocol correctness under network/failure semantics;
- a TLA+ model-checking result proves target-language implementation correctness;
- benchmark results prove functional correctness.

## Workflow

1. Read the requirement and existing code/tests before editing.
2. Extract safety properties, boundary conditions, and negative cases.
3. Create or update Dafny files under the existing formal directory, preferring `formal/` when no convention exists.
4. Model domain concepts explicitly with `datatype`, `predicate`, `function`, `set`, `seq`, or `map`.
5. Write specifications before implementation:
   - use `requires` for real preconditions;
   - use `ensures` for postconditions;
   - use `invariant` for loops;
   - use `decreases` for recursive definitions and termination arguments;
   - use `lemma` for named proof obligations.
6. Run `scripts/scan-forbidden.sh <path>` before trusting a proof.
7. Run `scripts/verify-dafny.sh <path>` until Dafny verification and `dafny audit` both pass.
8. Generate or modify target-language code only after Dafny verification passes.
9. Add target-language tests that mirror verified positive and negative properties.
10. In the final answer, report Dafny files changed, target files changed, verified properties, commands run, and assumptions not covered by Dafny.

## Proof Discipline

For authorization, access control, tenant isolation, and workflow logic, prove both allowed and denied cases. A useful model normally includes properties such as:

- admin or privileged actor is allowed;
- owner or same-tenant actor is allowed when the requirement permits it;
- public resource access is allowed when applicable;
- private non-owner non-admin access is denied;
- cross-tenant access is denied;
- invalid state transitions are impossible;
- terminal states cannot move to illegal successor states;
- parser/validator rejects malformed input, not only accepts valid input.

Never make a verifier error disappear by weakening the property that the user actually asked to guarantee. If the requirement is ambiguous, state the ambiguity and choose the stricter interpretation for safety-sensitive code.

## Forbidden Bypasses

Do not use or introduce:

- `assume`;
- `expect` in formal proof files;
- `{:verify false}`;
- `{:axiom}`;
- `{:extern}` in scanned formal proof files;
- `{:only}`;
- `decreases *`;
- bodyless declarations with specifications;
- bodyless loops or bodyless `forall` statements;
- vacuous specifications such as `ensures true`;
- `--no-verify`, `/dafnyVerify:0`, `--allow-axioms`, `/allowAxioms`, or other options that turn proofs into assumptions;
- deleting negative properties;
- strengthening `requires`, weakening `ensures`, weakening invariants, deleting lemmas/properties, or narrowing the modeled input space merely to pass verification.

If a proof needs an environmental fact, model it as an explicit precondition only when the caller can actually establish that fact. Otherwise encode it as state or prove a lemma.

## Verification Failure Handling

Classify every verifier failure before changing code:

- syntax or type error;
- implementation bug;
- missing loop invariant;
- missing lemma or reveal;
- insufficient precondition;
- over-strong postcondition;
- underspecified model;
- termination issue;
- verifier timeout or resource issue.

Repair in this order:

1. Fix the implementation or model if it contradicts the intended property.
2. Add the smallest valid invariant.
3. Add a narrow lemma for the missing proof fact.
4. Strengthen the model with missing definitions.
5. Strengthen preconditions only if the original requirement truly requires them.
6. Change the specification only when it is inconsistent with the user's stated requirement.

## Resources

- `scripts/verify-dafny.sh`: verify and audit one or more Dafny files/directories after forbidden-bypass scanning.
- `scripts/scan-forbidden.sh`: reject common proof bypasses and vacuous specs in `.dfy` files.
- `references/dafny-patterns.md`: load when examples are needed for authorization models, state machines, loop invariants, parser/validator specs, or proof repair patterns.

Run `verify-dafny.sh` as the authority for Dafny proof claims. Project-native Dafny commands may be run additionally, not instead, unless they are audited to be at least as strict: they must scan forbidden bypasses, verify included files, and run `dafny audit`.
