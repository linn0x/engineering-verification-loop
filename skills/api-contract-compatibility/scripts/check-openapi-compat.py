#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def load_doc(path):
    text = Path(path).read_text(encoding="utf-8")
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            f"{path}: YAML parsing requires PyYAML; install it or provide JSON. Original error: {exc}"
        ) from exc
    return yaml.safe_load(text)


def resolve_ref(doc, schema):
    if not isinstance(schema, dict) or "$ref" not in schema:
        return schema
    ref = schema["$ref"]
    if not ref.startswith("#/"):
        return schema
    cur = doc
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        cur = cur[part]
    return cur


def content_schema(doc, obj):
    if not isinstance(obj, dict):
        return {}
    content = obj.get("content") or {}
    if not isinstance(content, dict):
        return {}
    preferred = ["application/json", "application/*+json", "*/*"]
    for media in preferred:
        if media in content and isinstance(content[media], dict):
            return resolve_ref(doc, content[media].get("schema") or {})
    for media_obj in content.values():
        if isinstance(media_obj, dict) and "schema" in media_obj:
            return resolve_ref(doc, media_obj.get("schema") or {})
    return {}


def object_props(doc, schema):
    schema = resolve_ref(doc, schema)
    if not isinstance(schema, dict):
        return {}, set()
    if "allOf" in schema and isinstance(schema["allOf"], list):
        props = {}
        required = set()
        for child in schema["allOf"]:
            child_props, child_required = object_props(doc, child)
            props.update(child_props)
            required.update(child_required)
        return props, required
    props = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    required = set(schema.get("required") or [])
    return props, required


def schema_type(doc, schema):
    schema = resolve_ref(doc, schema)
    if not isinstance(schema, dict):
        return ""
    typ = schema.get("type")
    if isinstance(typ, list):
        return "|".join(sorted(map(str, typ)))
    return str(typ or "")


def schema_enum(schema):
    if not isinstance(schema, dict) or "enum" not in schema:
        return None
    return set(map(json.dumps, schema.get("enum") or []))


def compare_response_schema(issues, path, method, status, base_doc, cand_doc, base_schema, cand_schema, prefix=""):
    base_props, _ = object_props(base_doc, base_schema)
    cand_props, _ = object_props(cand_doc, cand_schema)
    for name, base_child in base_props.items():
        loc = f"{prefix}.{name}" if prefix else name
        if name not in cand_props:
            issues.append(f"{path} {method.upper()} response {status}: removed response field {loc}")
            continue
        cand_child = cand_props[name]
        base_type = schema_type(base_doc, base_child)
        cand_type = schema_type(cand_doc, cand_child)
        if base_type and cand_type and base_type != cand_type:
            issues.append(
                f"{path} {method.upper()} response {status}: changed field {loc} type {base_type} -> {cand_type}"
            )
        base_enum = schema_enum(resolve_ref(base_doc, base_child))
        cand_enum = schema_enum(resolve_ref(cand_doc, cand_child))
        if base_enum is not None and cand_enum is not None and not base_enum.issubset(cand_enum):
            issues.append(f"{path} {method.upper()} response {status}: narrowed enum for field {loc}")
        if schema_type(base_doc, base_child) == "object" and schema_type(cand_doc, cand_child) == "object":
            compare_response_schema(issues, path, method, status, base_doc, cand_doc, base_child, cand_child, loc)


def compare_request_schema(issues, path, method, base_doc, cand_doc, base_schema, cand_schema):
    base_props, base_required = object_props(base_doc, base_schema)
    cand_props, cand_required = object_props(cand_doc, cand_schema)
    for field in sorted(cand_required - base_required):
        issues.append(f"{path} {method.upper()}: newly required request field {field}")
    for name, base_child in base_props.items():
        if name not in cand_props:
            continue
        base_enum = schema_enum(resolve_ref(base_doc, base_child))
        cand_enum = schema_enum(resolve_ref(cand_doc, cand_props[name]))
        if base_enum is not None and cand_enum is not None and not base_enum.issubset(cand_enum):
            issues.append(f"{path} {method.upper()}: narrowed request enum for field {name}")


def check_backward(base, cand):
    issues = []
    base_paths = base.get("paths") or {}
    cand_paths = cand.get("paths") or {}
    for path, base_path_item in base_paths.items():
        if path not in cand_paths:
            issues.append(f"removed path {path}")
            continue
        cand_path_item = cand_paths[path] or {}
        for method, base_op in (base_path_item or {}).items():
            if method.lower() not in HTTP_METHODS:
                continue
            if method not in cand_path_item:
                issues.append(f"{path}: removed method {method.upper()}")
                continue
            cand_op = cand_path_item[method] or {}
            base_operation_id = base_op.get("operationId")
            cand_operation_id = cand_op.get("operationId")
            if base_operation_id and cand_operation_id and base_operation_id != cand_operation_id:
                issues.append(
                    f"{path} {method.upper()}: changed operationId {base_operation_id} -> {cand_operation_id}"
                )
            base_request_schema = content_schema(base, (base_op.get("requestBody") or {}))
            cand_request_schema = content_schema(cand, (cand_op.get("requestBody") or {}))
            if base_request_schema and cand_request_schema:
                compare_request_schema(issues, path, method, base, cand, base_request_schema, cand_request_schema)
            base_responses = base_op.get("responses") or {}
            cand_responses = cand_op.get("responses") or {}
            for status, base_response in base_responses.items():
                if status not in cand_responses:
                    issues.append(f"{path} {method.upper()}: removed response status {status}")
                    continue
                base_schema = content_schema(base, base_response)
                cand_schema = content_schema(cand, cand_responses[status])
                if base_schema and cand_schema:
                    compare_response_schema(issues, path, method, status, base, cand, base_schema, cand_schema)
    return issues


def main():
    parser = argparse.ArgumentParser(description="Check common OpenAPI backward compatibility breaks.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--mode", choices=["backward"], default="backward")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        baseline = load_doc(args.baseline)
        candidate = load_doc(args.candidate)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    issues = check_backward(baseline, candidate)
    result = {
        "baseline": args.baseline,
        "candidate": args.candidate,
        "mode": args.mode,
        "breaking_changes": issues,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif issues:
        for issue in issues:
            print(f"BREAKING: {issue}")
    else:
        print("[openapi-compat] no breaking changes detected by this checker")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
