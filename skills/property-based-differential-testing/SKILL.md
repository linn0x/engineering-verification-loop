---
name: property-based-differential-testing
description: Property-based, differential, metamorphic, and stateful testing specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to compare optimized Go/Python code against a simple oracle, old implementation, Dafny-modeled behavior, protocol trace, parser/validator spec, or API fixture across generated inputs. Not for formal proof, benchmark claims, mutation-score gates, API schema compatibility, or CI log triage.
---

# Property-Based Differential Testing

## Operating Contract

Use this skill to falsify incorrect target-language implementations with generated inputs and trusted oracles. Differential/property tests do not prove full correctness; they provide implementation-alignment evidence and durable counterexamples.

Do not claim correctness only because randomized tests passed. For correctness-critical logic, compose with `dafny-verification` for formal contracts and use this skill to test that the production implementation follows the model.

## Workflow

1. Read the requirement, existing tests, implementation, and any Dafny/TLA model.
2. Identify the behavior contract and choose the oracle:
   - simple but slow implementation;
   - old implementation;
   - reference library;
   - Dafny-modeled behavior exported as fixtures;
   - TLA counterexample trace or transition obligation;
   - hand-written expected fixture.
3. Define generated input domains:
   - valid inputs;
   - invalid/malformed inputs;
   - boundary sizes;
   - adversarial/skewed cases;
   - duplicates, empty cases, extreme numeric values, ordering variants.
4. Choose test style:
   - property-based tests for broad input spaces;
   - differential tests against oracle outputs;
   - metamorphic tests when exact expected outputs are expensive;
   - stateful/model-based tests for sequences of operations.
5. Add deterministic seed replay and counterexample capture.
6. Run the tests through `scripts/run-property-tests.sh` using the project-native command.
7. If a generated test fails, preserve the seed, minimal shrunk input, framework output, and a fixed regression test.
8. If comparing oracle output streams, use `scripts/compare-jsonl-oracles.py`.
9. Report:
   - oracle used;
   - generated domains;
   - framework/command;
   - seed/replay instructions;
   - counterexamples found or none found;
   - fixed regression tests;
   - assumptions not covered.

## Boundaries

This skill owns generated behavioral testing and counterexample management. It does not own Dafny proof repair, TLA model checking, API schema compatibility, mutation-score gates, benchmark interpretation, or CI failure forensics except when handed a specific failing generated-test seed.

Use this skill after:

- `algorithm-selection-benchmarking` proposes or implements a faster algorithm;
- `dafny-verification` defines a local functional contract needing target-language alignment tests;
- `tla-distributed-model-checking` produces counterexample traces or local handler obligations.

## Resources

- `scripts/run-property-tests.sh`: record and run a project-native property/differential test command under `.property-tests/`.
- `scripts/extract-counterexamples.py`: extract framework hints, seeds, shrunk examples, and failing lines from logs into JSONL.
- `scripts/compare-jsonl-oracles.py`: compare expected vs actual JSONL oracle records.
- `references/property-patterns.md`: property, differential, metamorphic, and stateful testing patterns.
- `references/framework-selection.md`: framework selection by language/ecosystem.
- `references/oracle-design.md`: guidance for choosing trustworthy oracles.
- `references/dafny-tla-composition.md`: composition with formal models and protocol traces.
- `assets/templates/`: test plan, counterexample report, and oracle fixture template.
