# Versioning Policy

When a breaking change is required, document:

- affected consumers;
- old behavior and new behavior;
- migration path;
- deprecation window;
- version bump or endpoint/schema namespace change;
- rollout/rollback plan;
- telemetry or contract-test signal used to know consumers have moved.

Do not hide breaking changes behind "internal API" unless the artifact is truly not consumed across a boundary.
