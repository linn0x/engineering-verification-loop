#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


GO_HINTS = {"go.mod", "go.sum"}
PYTHON_HINTS = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "poetry.lock",
    "uv.lock",
    "setup.py",
    "setup.cfg",
}


def classify(path_text):
    path = Path(path_text)
    name = path.name
    suffix = path.suffix
    if suffix == ".go" or name in GO_HINTS:
        return "go"
    if suffix == ".py" or name in PYTHON_HINTS or name.startswith("requirements"):
        return "python"
    return ""


def target_kind(path_text):
    path = Path(path_text)
    parts = set(path.parts)
    name = path.name
    if name.endswith("_test.go") or name.startswith("test_") or "tests" in parts or "test" in parts:
        return "test"
    if name in GO_HINTS or name in PYTHON_HINTS or name.startswith("requirements"):
        return "dependency"
    return "source"


def infer(paths):
    grouped = {}
    for raw in paths:
        raw = raw.strip()
        if not raw:
            continue
        language = classify(raw)
        if not language:
            continue
        grouped.setdefault(language, {"language": language, "paths": [], "kinds": []})
        grouped[language]["paths"].append(raw)
        kind = target_kind(raw)
        if kind not in grouped[language]["kinds"]:
            grouped[language]["kinds"].append(kind)
    return [grouped[key] for key in sorted(grouped)]


def main():
    parser = argparse.ArgumentParser(description="Infer Go/Python implementation targets from changed file paths.")
    parser.add_argument("--changed-files", required=True, help="Text file with one changed path per line.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    paths = Path(args.changed_files).read_text(encoding="utf-8").splitlines()
    targets = infer(paths)
    if args.json:
        print(json.dumps({"targets": targets}, indent=2, sort_keys=True))
    else:
        for target in targets:
            print(f"{target['language']}: {', '.join(target['paths'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
