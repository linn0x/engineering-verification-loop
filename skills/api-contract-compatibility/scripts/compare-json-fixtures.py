#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def type_name(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def compare(base, cand, path="$"):
    issues = []
    if type_name(base) != type_name(cand):
        return [f"{path}: type changed {type_name(base)} -> {type_name(cand)}"]
    if isinstance(base, dict):
        for key, base_value in base.items():
            child_path = f"{path}.{key}"
            if key not in cand:
                issues.append(f"{child_path}: removed field")
            else:
                issues.extend(compare(base_value, cand[key], child_path))
    elif isinstance(base, list) and base and cand:
        issues.extend(compare(base[0], cand[0], f"{path}[]"))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Compare baseline and candidate JSON fixture directories.")
    parser.add_argument("--baseline-dir", required=True)
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--glob", default="*.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    baseline_dir = Path(args.baseline_dir)
    candidate_dir = Path(args.candidate_dir)
    issues = []
    for base_file in sorted(baseline_dir.rglob(args.glob)):
        rel = base_file.relative_to(baseline_dir)
        cand_file = candidate_dir / rel
        if not cand_file.exists():
            issues.append(f"{rel}: removed fixture")
            continue
        try:
            issues.extend(f"{rel}: {issue}" for issue in compare(load_json(base_file), load_json(cand_file)))
        except Exception as exc:
            print(f"ERROR: failed to compare {rel}: {exc}", file=sys.stderr)
            return 2

    result = {"baseline_dir": str(baseline_dir), "candidate_dir": str(candidate_dir), "breaking_changes": issues}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif issues:
        for issue in issues:
            print(f"BREAKING: {issue}")
    else:
        print("[json-fixture-compat] no breaking changes detected by this checker")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
