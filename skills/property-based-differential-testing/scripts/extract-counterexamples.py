#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


PATTERNS = [
    ("hypothesis_falsifying", re.compile(r"Falsifying example:\s*(.*)", re.I)),
    ("hypothesis_seed", re.compile(r"(?:Hypothesis|reproduce_failure).*seed[=:]\s*([0-9A-Za-z_-]+)", re.I)),
    ("proptest_seed", re.compile(r"proptest.*(?:seed|rng seed)[=:]\s*([0-9A-Za-z_-]+)", re.I)),
    ("quickcheck_failure", re.compile(r"(?:Arguments|Test failed|Falsifiable).*?:\s*(.*)", re.I)),
    ("fast_check_seed", re.compile(r"(?:seed|Seed):\s*(-?\d+).*?(?:path|Path):\s*([0-9:]+)", re.I)),
    ("generic_seed", re.compile(r"\b(?:seed|SEED)[=:]\s*([0-9A-Za-z_-]+)\b")),
    ("shrunk", re.compile(r"\b(?:shrunk|minimal|smallest|counterexample)\b.*", re.I)),
    ("failure", re.compile(r"\b(?:FAIL|FAILED|AssertionError|panic:|thread '.*' panicked|counterexample)\b.*", re.I)),
]


def stable_id(path, line_no, text):
    raw = f"{path}:{line_no}:{text}".encode("utf-8", "replace")
    return hashlib.sha256(raw).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(description="Extract property-test counterexample hints from logs.")
    parser.add_argument("logs", nargs="+")
    parser.add_argument("--framework", default="unknown")
    args = parser.parse_args()

    found = 0
    for log in args.logs:
      path = Path(log)
      if not path.exists():
          print(f"ERROR: log not found: {path}", file=sys.stderr)
          return 2
      for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
          for kind, pattern in PATTERNS:
              match = pattern.search(line)
              if not match:
                  continue
              record = {
                  "case_id": stable_id(path, line_no, line),
                  "framework": args.framework,
                  "kind": kind,
                  "log": str(path),
                  "line": line_no,
                  "raw": line.strip(),
              }
              if match.groups():
                  record["captures"] = [g for g in match.groups() if g is not None]
              print(json.dumps(record, sort_keys=True))
              found += 1
              break

    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
