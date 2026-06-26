# Compatibility Rules

Common backward-incompatible changes:

- removing a path, method, event type, RPC, or SDK symbol;
- removing a documented response status;
- removing a response field that consumers may read;
- changing a response field scalar type;
- adding a required request field;
- narrowing accepted request enum values;
- changing operation IDs used by generated SDKs;
- changing error envelope shape;
- reusing or removing protobuf field numbers incorrectly;
- changing message semantics while keeping the same schema.

If a breaking change is intentional, require a version bump, migration plan, deprecation window, or consumer coordination record.
