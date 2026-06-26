# Dafny Patterns

Load this file when a task needs concrete Dafny modeling patterns or proof repair examples.

The verified examples live in `references/examples/`. When changing these patterns, run:

```bash
.agents/skills/dafny-verification/scripts/verify-dafny.sh .agents/skills/dafny-verification/references/examples
```

## Authorization Model

Use explicit domain types and prove both allowed and denied cases. Prefer modeling tenant boundaries directly instead of hiding them in integer conventions.

See `references/examples/authorization.dfy` for:

- admin allowed;
- same-tenant public resource allowed;
- same-tenant owner allowed;
- private non-owner non-admin denied;
- cross-tenant non-admin denied.

## State Transition Model

Model legal transitions as predicates or functions with preconditions, then prove illegal transitions are impossible.

See `references/examples/state_machine.dfy` for order-shipping and refund properties.

## Loop Invariant Pattern

Choose a specification shape that matches the implementation. For left-to-right loops over sequences, a prefix specification often verifies with smaller invariants than a front-recursive whole-sequence function.

See `references/examples/sum_loop.dfy` for a prefix-sum invariant.

## Parser Or Validator Pattern

Model acceptance and rejection as separate properties. Do not only prove that valid inputs pass.

See `references/examples/parser_validator.dfy` for a simple token validator with valid-input and wrong-length rejection lemmas.

## Proof Repair Priorities

When verification fails:

1. Fix implementation if behavior is wrong.
2. Add the smallest loop invariant that states what the loop has preserved so far.
3. Add a narrow lemma instead of expanding a proof inline everywhere.
4. Add `assert` statements to expose the exact fact Dafny cannot derive, then remove or keep only useful explanatory assertions.
5. Strengthen a precondition only when callers can establish it and the user requirement allows it.
6. Do not add `assume`, `expect`, `{:axiom}`, `{:only}`, `{:verify false}`, or vacuous postconditions.
