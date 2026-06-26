# TLA+ Patterns

Use small finite models first. Increase bounds only after the model shape and invariants are clear.

Common shapes:

- Model the network as a set or sequence of messages, depending on whether multiplicity/order matters.
- Use explicit actions for send, receive, drop, duplicate, partition, heal, crash, and recover.
- Keep persistent and volatile node state separate for crash-recovery models.
- Start with type invariants before protocol invariants.
- Make constants explicit in `.cfg` files: nodes, values, terms, message bounds, timeout bounds.
- Avoid hiding real environment assumptions in `Next`; document them as failure model constraints.

TLC-friendly discipline:

- Keep state finite.
- Prefer small model values before integers when arithmetic is not central.
- Add one invariant at a time.
- Preserve counterexample traces while debugging.
