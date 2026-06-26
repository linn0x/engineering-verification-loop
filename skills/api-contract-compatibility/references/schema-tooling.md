# Schema Tooling

Preferred tools:

- OpenAPI: project-native diff/check tooling when present; otherwise use `scripts/check-openapi-compat.py` for common breaks.
- Protobuf/gRPC: `buf breaking`; do not use weak ad hoc field-number checks.
- JSON fixtures/events: `scripts/compare-json-fixtures.py` for removed fields and type changes.
- Consumer/provider contracts: project-native Pact or equivalent command through `scripts/run-contract-tests.sh`.

Fail closed when parser support or required tools are missing. Report unverified surfaces explicitly.
