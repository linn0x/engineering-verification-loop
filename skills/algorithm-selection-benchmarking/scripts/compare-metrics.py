#!/usr/bin/env python3
import argparse
import csv
import math
import sys
from collections import defaultdict


def parse_bool(value):
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def pct_change(baseline, candidate):
    if baseline == 0:
        if candidate == 0:
            return 0.0
        return math.inf if candidate > 0 else -math.inf
    return (candidate - baseline) / abs(baseline) * 100.0


def main():
    parser = argparse.ArgumentParser(description="Compare baseline and candidate benchmark metrics.")
    parser.add_argument("csv_file", help="CSV with name,variant,metric,value,unit,lower_is_better")
    parser.add_argument("--baseline", default="baseline")
    parser.add_argument("--candidate", default="candidate")
    parser.add_argument("--max-regression-percent", type=float, default=0.0)
    args = parser.parse_args()

    groups = defaultdict(dict)
    required = {"name", "variant", "metric", "value", "unit", "lower_is_better"}

    with open(args.csv_file, newline="") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            print(f"ERROR: missing required columns: {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
        for row_num, row in enumerate(reader, start=2):
            try:
                key = (row["name"].strip(), row["metric"].strip(), row["unit"].strip())
                variant = row["variant"].strip()
                value = float(row["value"])
                lower = parse_bool(row["lower_is_better"])
            except Exception as exc:
                print(f"ERROR: invalid row {row_num}: {exc}", file=sys.stderr)
                return 2
            groups[key][variant] = (value, lower)

    failures = []
    compared = 0
    print("| name | metric | unit | baseline | candidate | change_pct | regression_pct |")
    print("|---|---|---:|---:|---:|---:|---:|")

    for key in sorted(groups):
        variants = groups[key]
        if args.baseline not in variants or args.candidate not in variants:
            continue
        compared += 1
        base, lower = variants[args.baseline]
        cand, cand_lower = variants[args.candidate]
        if cand_lower != lower:
            print(f"ERROR: lower_is_better mismatch for {key}", file=sys.stderr)
            return 2
        change = pct_change(base, cand)
        if math.isinf(change):
            change_text = "inf" if change > 0 else "-inf"
        else:
            change_text = f"{change:.2f}"
        regression = change if lower else -change
        if regression < 0:
            regression = 0.0
        name, metric, unit = key
        print(f"| {name} | {metric} | {unit} | {base:g} | {cand:g} | {change_text} | {regression:.2f} |")
        if regression > args.max_regression_percent:
            failures.append((name, metric, regression))

    if compared == 0:
        print(
            f"ERROR: no comparable metrics found for variants {args.baseline!r} and {args.candidate!r}",
            file=sys.stderr,
        )
        return 2

    if failures:
        print("", file=sys.stderr)
        for name, metric, regression in failures:
            print(
                f"ERROR: {name}/{metric} regressed by {regression:.2f}% "
                f"(allowed {args.max_regression_percent:.2f}%)",
                file=sys.stderr,
            )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
