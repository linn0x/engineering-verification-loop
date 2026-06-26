#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


PATTERNS = {
    "generated_states": re.compile(r"generated\s+([0-9,]+)\s+states", re.I),
    "distinct_states": re.compile(r"([0-9,]+)\s+distinct\s+states", re.I),
    "depth": re.compile(r"depth\s+of\s+the\s+complete\s+state\s+graph\s+search\s+is\s+([0-9,]+)", re.I),
    "no_error": re.compile(r"No error has been found", re.I),
    "deadlock": re.compile(r"Deadlock reached", re.I),
    "error": re.compile(r"(^|\s)Error:", re.I),
}


def first(pattern, text):
    match = pattern.search(text)
    if not match:
        return ""
    if match.groups():
        return match.group(match.lastindex or 1)
    return "yes"


def main():
    parser = argparse.ArgumentParser(description="Summarize TLC log files.")
    parser.add_argument("logs", nargs="+")
    args = parser.parse_args()

    print("| log | generated_states | distinct_states | depth | no_error | deadlock | error |")
    print("|---|---:|---:|---:|---|---|---|")
    for log in args.logs:
        path = Path(log)
        text = path.read_text(errors="replace") if path.exists() else ""
        generated = first(PATTERNS["generated_states"], text)
        distinct = first(PATTERNS["distinct_states"], text)
        depth = first(PATTERNS["depth"], text)
        no_error = "yes" if PATTERNS["no_error"].search(text) else "no"
        deadlock = "yes" if PATTERNS["deadlock"].search(text) else "no"
        error = "yes" if PATTERNS["error"].search(text) else "no"
        print(f"| {path} | {generated} | {distinct} | {depth} | {no_error} | {deadlock} | {error} |")


if __name__ == "__main__":
    main()
