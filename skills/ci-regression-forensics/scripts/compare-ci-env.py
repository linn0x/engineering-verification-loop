#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def flatten(value, prefix=""):
    if isinstance(value, dict):
        items = {}
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            items.update(flatten(child, child_prefix))
        return items
    return {prefix: value}


def main():
    parser = argparse.ArgumentParser(description="Compare two CI/local diagnostics JSON files.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    baseline = flatten(json.loads(Path(args.baseline).read_text()))
    candidate = flatten(json.loads(Path(args.candidate).read_text()))

    print("| key | baseline | candidate |")
    print("|---|---|---|")
    changes = 0
    for key in sorted(set(baseline) | set(candidate)):
        left = baseline.get(key, "")
        right = candidate.get(key, "")
        if left != right:
            changes += 1
            print(f"| {key} | `{str(left)[:120]}` | `{str(right)[:120]}` |")
    if changes == 0:
        print("| no differences |  |  |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
