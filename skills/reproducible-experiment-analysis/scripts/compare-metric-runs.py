#!/usr/bin/env python3
import argparse
import csv
import json
import math
import random
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
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numeric_values(records, variant, metric):
    values = []
    for record in records:
        if record.get("variant") != variant or record.get("metric") != metric:
            continue
        try:
            values.append(float(record["value"]))
        except Exception as exc:
            raise ValueError(f"non-numeric value for {variant}/{metric}: {record}") from exc
    return values


def summarize(values):
    if not values:
        return {"n": 0}
    mean = statistics.fmean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    cv = abs(stdev / mean) if mean else math.inf
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "stdev": stdev,
        "cv": cv,
        "min": min(values),
        "max": max(values),
    }


def effect_pct(base_mean, cand_mean, direction):
    if base_mean == 0:
        raise ValueError("baseline mean is zero; percentage effect is undefined")
    if direction == "lower-is-better":
        return ((base_mean - cand_mean) / abs(base_mean)) * 100.0
    if direction == "higher-is-better":
        return ((cand_mean - base_mean) / abs(base_mean)) * 100.0
    raise ValueError("direction must be lower-is-better or higher-is-better")


def percentile(values, pct):
    if not values:
        return math.nan
    ordered = sorted(values)
    pos = (len(ordered) - 1) * pct
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def bootstrap_ci(base_values, cand_values, direction, iterations, seed):
    rng = random.Random(seed)
    effects = []
    for _ in range(iterations):
        base_sample = [rng.choice(base_values) for _ in base_values]
        cand_sample = [rng.choice(cand_values) for _ in cand_values]
        effects.append(effect_pct(statistics.fmean(base_sample), statistics.fmean(cand_sample), direction))
    return percentile(effects, 0.025), percentile(effects, 0.975)


def classify(effect, ci_low, ci_high, claim, min_effect_pct, regression_threshold_pct):
    likely_regression = ci_high < -regression_threshold_pct
    improvement_supported = ci_low >= min_effect_pct
    difference_supported = ci_low > 0 or ci_high < 0
    if claim == "improvement":
        ok = improvement_supported
    elif claim == "no-regression":
        ok = not likely_regression
    else:
        ok = difference_supported
    return {
        "effect_pct": effect,
        "ci95_effect_pct": [ci_low, ci_high],
        "likely_regression": likely_regression,
        "improvement_supported": improvement_supported,
        "difference_supported": difference_supported,
        "claim_supported": ok,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare repeated baseline/candidate metric samples.")
    parser.add_argument("--input", required=True, help="CSV or JSON records with variant,metric,value")
    parser.add_argument("--baseline", default="baseline")
    parser.add_argument("--candidate", default="candidate")
    parser.add_argument("--metric", required=True)
    parser.add_argument("--direction", choices=["lower-is-better", "higher-is-better"], required=True)
    parser.add_argument("--claim", choices=["no-regression", "improvement", "difference"], default="no-regression")
    parser.add_argument("--min-samples", type=int, default=5)
    parser.add_argument("--min-effect-pct", type=float, default=1.0)
    parser.add_argument("--regression-threshold-pct", type=float, default=1.0)
    parser.add_argument("--max-cv", type=float, default=1.0)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        records = load_records(args.input)
        base_values = numeric_values(records, args.baseline, args.metric)
        cand_values = numeric_values(records, args.candidate, args.metric)
        if len(base_values) < args.min_samples or len(cand_values) < args.min_samples:
            raise RuntimeError(
                f"insufficient samples: {args.baseline}={len(base_values)}, {args.candidate}={len(cand_values)}, required={args.min_samples}"
            )
        base_summary = summarize(base_values)
        cand_summary = summarize(cand_values)
        noisy = base_summary["cv"] > args.max_cv or cand_summary["cv"] > args.max_cv
        if noisy:
            raise RuntimeError(
                f"coefficient of variation too high: baseline={base_summary['cv']:.4g}, candidate={cand_summary['cv']:.4g}, max={args.max_cv}"
            )
        effect = effect_pct(base_summary["mean"], cand_summary["mean"], args.direction)
        ci_low, ci_high = bootstrap_ci(base_values, cand_values, args.direction, args.bootstrap, args.seed)
        verdict = classify(effect, ci_low, ci_high, args.claim, args.min_effect_pct, args.regression_threshold_pct)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {
        "input": args.input,
        "metric": args.metric,
        "direction": args.direction,
        "claim": args.claim,
        "baseline": base_summary,
        "candidate": cand_summary,
        "verdict": verdict,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"[metric-compare] metric={args.metric} direction={args.direction} claim={args.claim}")
        print(f"[metric-compare] baseline n={base_summary['n']} mean={base_summary['mean']:.6g} cv={base_summary['cv']:.4g}")
        print(f"[metric-compare] candidate n={cand_summary['n']} mean={cand_summary['mean']:.6g} cv={cand_summary['cv']:.4g}")
        print(
            f"[metric-compare] effect={verdict['effect_pct']:.4g}% ci95=[{ci_low:.4g}%, {ci_high:.4g}%]"
        )
        print(f"[metric-compare] claim_supported={str(verdict['claim_supported']).lower()}")
    return 0 if verdict["claim_supported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
