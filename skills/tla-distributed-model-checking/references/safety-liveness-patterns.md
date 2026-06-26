# Safety And Liveness Patterns

Safety properties state that bad things never happen:

- agreement: two correct nodes do not decide different values;
- integrity: a node decides at most once per instance;
- monotonicity: term, epoch, version, or sequence number never decreases;
- no double-commit;
- no split brain;
- no stale read beyond the stated consistency model;
- durable-state invariant survives crash/recovery.

Liveness properties state that good things eventually happen. Only add them with explicit fairness and environment assumptions:

- network eventually delivers some class of messages;
- partitions eventually heal;
- retries eventually occur;
- non-crashed nodes continue taking steps;
- timeouts are eventually observed.

Do not turn a safety problem into a liveness assumption. If the model needs fairness to avoid an impossible scheduler, state it. If it needs fairness to hide a protocol bug, fix the protocol or narrow the claim.
