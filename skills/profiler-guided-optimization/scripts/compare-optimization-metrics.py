#!/usr/bin/env python3
import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path


def load_records(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of records")
        return data
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def values(records, variant, metric):
    out = []
    for record in records:
        if record.get("variant") == variant and record.get("metric") == metric:
            out.append(float(record["value"]))
    return out


def summary(values_):
    if not values_:
        return {"n": 0}
    mean = statistics.fmean(values_)
    stdev = statistics.stdev(values_) if len(values_) > 1 else 0.0
    return {
        "n": len(values_),
        "mean": mean,
        "median": statistics.median(values_),
        "stdev": stdev,
        "cv": abs(stdev / mean) if mean else math.inf,
        "min": min(values_),
        "max": max(values_),
    }


def improvement_pct(before_mean, after_mean, direction):
    if before_mean == 0:
        raise ValueError("before mean is zero; percentage change is undefined")
    if direction == "lower-is-better":
        return ((before_mean - after_mean) / abs(before_mean)) * 100.0
    if direction == "higher-is-better":
        return ((after_mean - before_mean) / abs(before_mean)) * 100.0
    raise ValueError("invalid direction")


def main():
    parser = argparse.ArgumentParser(description="Compare before/after optimization metrics.")
    parser.add_argument("--input", required=True, help="CSV or JSON records with variant,metric,value")
    parser.add_argument("--before", default="before")
    parser.add_argument("--after", default="after")
    parser.add_argument("--metric", required=True)
    parser.add_argument("--direction", choices=["lower-is-better", "higher-is-better"], required=True)
    parser.add_argument("--min-samples", type=int, default=3)
    parser.add_argument("--min-improvement-pct", type=float, default=1.0)
    parser.add_argument("--max-cv", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        records = load_records(args.input)
        before_values = values(records, args.before, args.metric)
        after_values = values(records, args.after, args.metric)
        if len(before_values) < args.min_samples or len(after_values) < args.min_samples:
            raise RuntimeError(
                f"insufficient samples: {args.before}={len(before_values)}, {args.after}={len(after_values)}, required={args.min_samples}"
            )
        before = summary(before_values)
        after = summary(after_values)
        if before["cv"] > args.max_cv or after["cv"] > args.max_cv:
            raise RuntimeError(
                f"coefficient of variation too high: before={before['cv']:.4g}, after={after['cv']:.4g}, max={args.max_cv}"
            )
        improvement = improvement_pct(before["mean"], after["mean"], args.direction)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    ok = improvement >= args.min_improvement_pct
    result = {
        "input": args.input,
        "metric": args.metric,
        "direction": args.direction,
        "before": before,
        "after": after,
        "improvement_pct": improvement,
        "min_improvement_pct": args.min_improvement_pct,
        "optimization_supported": ok,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"[optimization-compare] metric={args.metric} direction={args.direction}")
        print(f"[optimization-compare] before n={before['n']} mean={before['mean']:.6g} cv={before['cv']:.4g}")
        print(f"[optimization-compare] after n={after['n']} mean={after['mean']:.6g} cv={after['cv']:.4g}")
        print(f"[optimization-compare] improvement={improvement:.4g}%")
        print(f"[optimization-compare] optimization_supported={str(ok).lower()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
