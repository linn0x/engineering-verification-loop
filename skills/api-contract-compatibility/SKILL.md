---
name: api-contract-compatibility
description: API and schema compatibility specialist for engineering-verification-loop. Use directly or when routed by engineering-verification-loop to check OpenAPI, JSON Schema, Protobuf/gRPC, GraphQL schemas, HTTP endpoints, event payloads, SDK interfaces, or serialized wire formats for breaking changes against a baseline; not for endpoint implementation correctness, auth proof, distributed protocol semantics, performance, or general API documentation.
---

# API Contract Compatibility

## Operating Contract

Use this skill when a change can affect API consumers, SDK users, event subscribers, or other services. Contract compatibility is baseline-based: compare the candidate contract against a known baseline before claiming the change is safe.

Do not claim compatibility when the relevant checker did not run. Fail closed for unsupported schema formats or missing tooling.

## Workflow

1. Identify the contract surface:
   - OpenAPI/Swagger;
   - JSON Schema;
   - Protobuf/gRPC;
   - GraphQL schema;
   - HTTP request/response fixtures;
   - event/message payloads;
   - SDK public interface.
2. Identify the compatibility mode:
   - backward: new provider remains usable by old consumers;
   - forward: old provider remains usable by new consumers;
   - bidirectional when both matter.
3. Locate the baseline and candidate artifacts. If no baseline exists, create a baseline snapshot before editing.
4. Run the relevant checker:
   - OpenAPI: `scripts/check-openapi-compat.py`;
   - Protobuf: `scripts/check-protobuf-compat.sh`;
   - JSON fixtures: `scripts/compare-json-fixtures.py`;
   - project contract tests: `scripts/run-contract-tests.sh`.
5. Classify breaking changes:
   - removed path/method/status;
   - operation ID change when SDK generation depends on it;
   - newly required request field;
   - request enum narrowing;
   - removed response field;
   - changed response scalar type;
   - removed protobuf field number or incompatible field type;
   - changed event envelope or error shape.
6. If a breaking change is intended, require an explicit versioning/migration story.
7. Compose with other skills when needed:
   - `dafny-verification` for critical validators/auth/state transitions;
   - `property-based-differential-testing` for old/new handler behavior;
   - `ci-regression-forensics` when contract checks fail in CI.
8. Report baseline, candidate, mode, check commands, breaking changes, migration requirements, and unchecked surfaces.

## Boundaries

This skill owns contract surface compatibility and breaking-change detection. It does not own endpoint implementation correctness, authorization proof, distributed protocol semantics, performance, or documentation polish.

## Resources

- `scripts/check-openapi-compat.py`: baseline/candidate OpenAPI compatibility checker for common breaking changes.
- `scripts/check-protobuf-compat.sh`: strict wrapper for `buf breaking`; no fake protobuf checker.
- `scripts/compare-json-fixtures.py`: compare baseline/candidate JSON fixture directories for removed fields and type changes.
- `scripts/run-contract-tests.sh`: record and run project-native contract test commands.
- `references/compatibility-rules.md`: compatibility rules by artifact type.
- `references/schema-tooling.md`: tooling selection and failure policy.
- `references/consumer-contract-patterns.md`: consumer/provider contract testing patterns.
- `references/versioning-policy.md`: migration and versioning guidance.
- `assets/templates/`: compatibility report, change matrix, and fixture layout.
