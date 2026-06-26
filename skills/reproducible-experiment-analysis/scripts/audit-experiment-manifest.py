#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


REQUIRED = [
    "claim",
    "hypothesis",
    "baseline",
    "candidate",
    "dataset",
    "command",
    "metrics",
    "seeds",
    "repetitions",
    "environment",
]

RECOMMENDED = [
    "git_revision",
    "dependency_snapshot",
    "hardware",
    "warmup_policy",
    "exclusion_policy",
    "confirmation_run",
]


def load_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"{path}: YAML requires PyYAML or use JSON. Original error: {exc}") from exc
    return yaml.safe_load(text)


def is_blank(value):
    return value is None or value == "" or value == [] or value == {}


def audit(doc):
    issues = []
    warnings = []
    if not isinstance(doc, dict):
        return ["manifest root must be an object"], []
    for key in REQUIRED:
        if key not in doc or is_blank(doc.get(key)):
            issues.append(f"missing required field: {key}")
    for key in RECOMMENDED:
        if key not in doc or is_blank(doc.get(key)):
            warnings.append(f"missing recommended field: {key}")
    repetitions = doc.get("repetitions")
    if isinstance(repetitions, int) and repetitions < 3:
        issues.append("repetitions must be at least 3 unless the metric is deterministic by construction")
    metrics = doc.get("metrics")
    if isinstance(metrics, list):
        for idx, metric in enumerate(metrics):
            if not isinstance(metric, dict):
                issues.append(f"metrics[{idx}] must be an object")
                continue
            for field in ("name", "direction", "unit"):
                if is_blank(metric.get(field)):
                    issues.append(f"metrics[{idx}] missing {field}")
            if metric.get("direction") not in ("higher-is-better", "lower-is-better", "target"):
                issues.append(f"metrics[{idx}] direction must be higher-is-better, lower-is-better, or target")
    elif metrics is not None:
        issues.append("metrics must be a list")
    claim = doc.get("claim")
    if isinstance(claim, str) and "improvement" in claim.lower() and is_blank(doc.get("minimum_effect")):
        warnings.append("improvement claim should define minimum_effect")
    return issues, warnings


def main():
    parser = argparse.ArgumentParser(description="Audit experiment manifest reproducibility fields.")
    parser.add_argument("manifest")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        doc = load_doc(Path(args.manifest))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    issues, warnings = audit(doc)
    result = {"manifest": args.manifest, "issues": issues, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"ISSUE: {issue}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if not issues:
            print("[experiment-manifest] required fields present")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
