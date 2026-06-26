# Framework Selection

Prefer project-native property testing tools:

| Ecosystem | Common choices |
|---|---|
| Python | Hypothesis |
| Rust | proptest, quickcheck |
| TypeScript/JavaScript | fast-check |
| Go | testing/quick, rapid, gopter, project-native fuzz tests |
| JVM | jqwik, QuickTheories, ScalaCheck |
| .NET | FsCheck |

Selection rules:

- Use the framework already present in the repository when available.
- Prefer frameworks with shrinking and seed replay.
- If no framework exists, start with differential fixtures and table-driven generated cases before adding dependencies.
- Avoid introducing a new dependency in mature production code without checking project conventions.
- Use target-language fuzzing when the failure class is parser/decoder/security-input oriented.
