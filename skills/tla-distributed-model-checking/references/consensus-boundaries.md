# Consensus Boundary Rules

Model consensus only when the task actually needs consensus-like guarantees.

Minimum safety properties:

- agreement: two correct nodes do not decide different values;
- validity: a decided value was proposed or otherwise allowed by the protocol;
- integrity: a node decides at most once per instance;
- monotonic term or epoch behavior where applicable;
- quorum intersection assumptions explicit in constants/config.

Do not claim production consensus correctness from:

- a single small TLC config;
- a model without crash/recovery when production persists state;
- a model assuming reliable FIFO networking when production does not;
- a model omitting clock/timeout assumptions used by the implementation;
- a local Dafny proof of a handler without the global protocol model.
