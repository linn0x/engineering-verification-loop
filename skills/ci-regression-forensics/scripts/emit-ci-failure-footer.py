#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys


FAILURE_TYPES = {
    "dependency-resolution",
    "lint-format",
    "typecheck",
    "build-compile",
    "unit-test",
    "integration-e2e",
    "timeout",
    "oom-resource",
    "network-external",
    "flaky-suspicion",
    "benchmark-performance",
    "api-schema-compatibility",
    "formal-verification",
    "unknown",
}

ROUTES = {
    "api-schema-compatibility": "api-contract-compatibility",
    "benchmark-performance": "profiler-guided-optimization",
    "formal-verification": "dafny-verification",
}

SIGNATURE_RE = re.compile(r"^[0-9a-f]{16,64}$")


def expected_route(failure_type):
    if failure_type in ROUTES:
        return ROUTES[failure_type]
    if failure_type in FAILURE_TYPES:
        return "ci-regression-forensics"
    return ""


def stable_signature(args):
    if args.stable_signature:
        return args.stable_signature
    material = "\n".join(
        [
            args.job_name,
            args.command,
            str(args.exit_code),
            args.failure_type,
            args.artifact_path,
            args.specialist_route,
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(description="Emit a machine-readable CI failure footer.")
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--exit-code", required=True, type=int)
    parser.add_argument("--failure-type", required=True)
    parser.add_argument("--artifact-path", required=True)
    parser.add_argument("--specialist-route", required=True)
    parser.add_argument("--stable-signature")
    parser.add_argument("--signature-provenance", choices=["external"])
    parser.add_argument("--signature-source")
    parser.add_argument("--signature-reason")
    args = parser.parse_args()

    if args.exit_code <= 0:
        print("ERROR: --exit-code must be non-zero for a failure footer", file=sys.stderr)
        return 2
    if args.failure_type not in FAILURE_TYPES:
        print(f"ERROR: unknown --failure-type {args.failure_type!r}", file=sys.stderr)
        return 2
    route = expected_route(args.failure_type)
    if route and args.specialist_route != route:
        print(f"ERROR: --specialist-route must be {route!r} for {args.failure_type}", file=sys.stderr)
        return 2
    if args.stable_signature and not SIGNATURE_RE.match(args.stable_signature):
        print("ERROR: --stable-signature must be 16-64 lowercase hex characters", file=sys.stderr)
        return 2
    if args.stable_signature and args.signature_provenance != "external":
        print("ERROR: --stable-signature requires --signature-provenance external", file=sys.stderr)
        return 2
    if args.signature_provenance == "external":
        if not args.stable_signature:
            print("ERROR: --signature-provenance external requires --stable-signature", file=sys.stderr)
            return 2
        for flag, value in (
            ("--signature-source", args.signature_source),
            ("--signature-reason", args.signature_reason),
        ):
            if not value:
                print(f"ERROR: {flag} is required for external signature provenance", file=sys.stderr)
                return 2

    failure = {
        "job_name": args.job_name,
        "command": args.command,
        "exit_code": args.exit_code,
        "failure_type": args.failure_type,
        "artifact_path": args.artifact_path,
        "stable_signature": stable_signature(args),
        "specialist_route": args.specialist_route,
    }
    if args.signature_provenance == "external":
        failure.update(
            {
                "signature_provenance": "external",
                "signature_source": args.signature_source,
                "signature_reason": args.signature_reason,
            }
        )

    footer = {"ci_failure": failure}
    print(json.dumps(footer, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
