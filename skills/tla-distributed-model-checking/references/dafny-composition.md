# Composition With dafny-verification

TLA+ owns:

- global state-space behavior;
- nondeterministic scheduling;
- message ordering/loss/duplication;
- partitions;
- clock abstractions;
- quorum/protocol invariants.

Dafny owns:

- local deterministic transition functions;
- message validators;
- parser/serializer invariants;
- storage-record invariants;
- idempotency checks;
- authorization/tenant isolation inside nodes;
- data-structure invariants.

Recommended handoff:

| TLA+ action | Dafny function/method | Implementation file | Tests | Assumptions |
|---|---|---|---|---|

Never claim that Dafny verified the distributed protocol merely because it verified a local handler.
Never claim that TLC verified the implementation merely because the implementation was inspired by the model.
