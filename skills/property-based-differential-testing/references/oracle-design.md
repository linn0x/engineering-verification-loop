# Oracle Design

A good oracle is simpler, more trusted, or independently implemented.

Good oracle sources:

- slow but obvious implementation;
- previous stable implementation;
- well-tested standard library behavior;
- generated fixtures from Dafny or TLA obligations;
- independently maintained reference implementation;
- hand-curated golden cases for tricky boundary behavior.

Avoid weak oracles:

- the same implementation with renamed variables;
- a mocked expected value that repeats the candidate logic;
- an oracle that ignores error behavior when errors are part of the contract;
- generated data that never reaches negative or malformed cases;
- exact floating-point equality unless the contract actually requires it.

When exact equality is not appropriate, document the comparator and why it is sound for the contract.
