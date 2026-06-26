#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path


MISSING = object()


def get_path(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return MISSING
        cur = cur[part]
    return cur


def has_path(obj, dotted):
    return get_path(obj, dotted) is not MISSING


def canonicalize(value, unordered_fields=(), prefix=""):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else key
            result[key] = canonicalize(child, unordered_fields, child_path)
        return result
    if isinstance(value, list):
        items = [canonicalize(item, unordered_fields, prefix) for item in value]
        if prefix in unordered_fields:
            return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
        return items
    return value


def load_jsonl(path, required_fields):
    records = {}
    seen_any = False
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            seen_any = True
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
            for field in required_fields:
                if field not in obj:
                    raise RuntimeError(f"{path}:{line_no}: missing required field {field}")
            case_id = obj.get("id")
            if not case_id:
                raise RuntimeError(f"{path}:{line_no}: missing id")
            if case_id in records:
                raise RuntimeError(f"{path}:{line_no}: duplicate id {case_id}")
            status = obj.get("status")
            if status == "ok" and "output" not in obj:
                raise RuntimeError(f"{path}:{line_no}: status ok requires output")
            if status == "error" and "error" not in obj:
                raise RuntimeError(f"{path}:{line_no}: status error requires error")
            records[case_id] = obj
    if not seen_any:
        raise RuntimeError(f"{path}: no records")
    return records


def values_equal(expected, actual, abs_tol, rel_tol):
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return math.isclose(float(expected), float(actual), abs_tol=abs_tol, rel_tol=rel_tol)
    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected) != set(actual):
            return False
        return all(values_equal(expected[key], actual[key], abs_tol, rel_tol) for key in expected)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(expected) == len(actual) and all(
            values_equal(left, right, abs_tol, rel_tol) for left, right in zip(expected, actual)
        )
    return expected == actual


def compare(expected, actual, *, value_field, allow_extra_actual, abs_tol, rel_tol, unordered_fields, canonicalize_json):
    issues = []
    expected_ids = set(expected)
    actual_ids = set(actual)
    for case_id in sorted(expected_ids - actual_ids):
        issues.append(f"{case_id}: missing actual record")
    if not allow_extra_actual:
        for case_id in sorted(actual_ids - expected_ids):
            issues.append(f"{case_id}: unexpected actual record")
    for case_id in sorted(expected_ids & actual_ids):
        exp_record = expected[case_id]
        act_record = actual[case_id]
        if exp_record.get("status") != act_record.get("status"):
            issues.append(f"{case_id}: status mismatch expected={exp_record.get('status')} actual={act_record.get('status')}")
            continue
        field = "error" if exp_record.get("status") == "error" else value_field
        if not has_path(exp_record, field):
            issues.append(f"{case_id}: expected record missing {field}")
            continue
        if not has_path(act_record, field):
            issues.append(f"{case_id}: actual record missing {field}")
            continue
        exp_value = get_path(exp_record, field)
        act_value = get_path(act_record, field)
        if canonicalize_json:
            exp_value = canonicalize(exp_value, unordered_fields, field)
            act_value = canonicalize(act_value, unordered_fields, field)
        if not values_equal(exp_value, act_value, abs_tol, rel_tol):
            issues.append(
                f"{case_id}: {field} mismatch expected={json.dumps(exp_value, sort_keys=True)} actual={json.dumps(act_value, sort_keys=True)}"
            )
    return issues


def main():
    parser = argparse.ArgumentParser(description="Compare model expected JSONL fixtures with implementation actual JSONL.")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--field", default="output")
    parser.add_argument("--required-field", action="append", default=["id", "input", "status"])
    parser.add_argument("--allow-extra-actual", action="store_true")
    parser.add_argument("--float-abs-tol", type=float, default=0.0)
    parser.add_argument("--float-rel-tol", type=float, default=0.0)
    parser.add_argument("--unordered-field", action="append", default=[])
    parser.add_argument("--canonicalize-json", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        required_fields = list(dict.fromkeys(args.required_field))
        expected = load_jsonl(args.expected, required_fields)
        actual = load_jsonl(args.actual, required_fields)
        issues = compare(
            expected,
            actual,
            value_field=args.field,
            allow_extra_actual=args.allow_extra_actual,
            abs_tol=args.float_abs_tol,
            rel_tol=args.float_rel_tol,
            unordered_fields=set(args.unordered_field),
            canonicalize_json=args.canonicalize_json,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {
        "expected": args.expected,
        "actual": args.actual,
        "field": args.field,
        "issues": issues,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"MISMATCH: {issue}")
        if not issues:
            print("[model-implementation-conformance] fixtures matched")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
