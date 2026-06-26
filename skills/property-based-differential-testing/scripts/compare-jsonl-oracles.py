#!/usr/bin/env python3
import argparse
import json
import sys


def load_jsonl(path, key_field):
    records = {}
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if key_field not in record:
                raise ValueError(f"{path}:{line_no}: missing key field {key_field!r}")
            key = str(record[key_field])
            if key in records:
                raise ValueError(f"{path}:{line_no}: duplicate key {key!r}")
            records[key] = record
    return records


def project(record, ignored):
    return {k: v for k, v in record.items() if k not in ignored}


def main():
    parser = argparse.ArgumentParser(description="Compare expected and actual JSONL oracle records.")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--key", default="case_id")
    parser.add_argument("--ignore-field", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="Report all mismatches instead of stopping after the first.")
    args = parser.parse_args()

    ignored = set(args.ignore_field)
    try:
        expected = load_jsonl(args.expected, args.key)
        actual = load_jsonl(args.actual, args.key)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    failures = 0
    for key in sorted(set(expected) | set(actual)):
        if key not in expected:
            print(f"ERROR: unexpected actual record {key}", file=sys.stderr)
            failures += 1
        elif key not in actual:
            print(f"ERROR: missing actual record {key}", file=sys.stderr)
            failures += 1
        else:
            exp = project(expected[key], ignored)
            act = project(actual[key], ignored)
            if exp != act:
                print(f"ERROR: mismatch for {key}", file=sys.stderr)
                print("expected:", json.dumps(exp, sort_keys=True), file=sys.stderr)
                print("actual:  ", json.dumps(act, sort_keys=True), file=sys.stderr)
                failures += 1
        if failures and not args.all:
            return 1

    if failures:
        print(f"ERROR: {failures} mismatch(es)", file=sys.stderr)
        return 1

    print(f"[oracle-compare] matched {len(expected)} record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
