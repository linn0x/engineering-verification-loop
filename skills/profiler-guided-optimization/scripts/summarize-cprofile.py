#!/usr/bin/env python3
import argparse
import json
import pstats
import sys
from pathlib import Path


def summarize(path, sort, limit):
    stats = pstats.Stats(str(path))
    stats.sort_stats(sort)
    rows = []
    for func in stats.fcn_list[:limit]:
        cc, nc, tt, ct, callers = stats.stats[func]
        filename, line, name = func
        rows.append(
            {
                "function": f"{filename}:{line}:{name}",
                "primitive_calls": cc,
                "total_calls": nc,
                "total_time_sec": tt,
                "cumulative_time_sec": ct,
                "caller_count": len(callers),
            }
        )
    return {
        "profile": str(path),
        "sort": sort,
        "total_calls": stats.total_calls,
        "primitive_calls": stats.prim_calls,
        "total_time_sec": stats.total_tt,
        "hotspots": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize a Python cProfile .prof file.")
    parser.add_argument("profile")
    parser.add_argument("--sort", choices=["cumulative", "time", "calls"], default="cumulative")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = summarize(Path(args.profile), args.sort, args.limit)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"[cprofile] total_time={result['total_time_sec']:.6g}s total_calls={result['total_calls']} sort={args.sort}"
        )
        for idx, row in enumerate(result["hotspots"], start=1):
            print(
                f"{idx:>2}. cum={row['cumulative_time_sec']:.6g}s self={row['total_time_sec']:.6g}s "
                f"calls={row['total_calls']} {row['function']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
