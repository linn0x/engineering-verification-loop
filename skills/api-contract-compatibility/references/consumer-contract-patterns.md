# Consumer Contract Patterns

- Consumer-driven contract: consumer records expected request/response or message interaction; provider verifies it.
- Provider compatibility check: provider compares candidate schema against published baseline.
- Golden fixture compatibility: baseline and candidate payload fixtures are compared for removed fields and type changes.
- Negative compatibility case: invalid or deprecated inputs should fail in the same documented way until a migration window closes.

Contract tests complement implementation tests. A handler can be functionally correct and still break consumers by changing the public shape.
