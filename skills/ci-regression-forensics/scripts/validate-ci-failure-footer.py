#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


FOOTER_REQUIRED_FIELDS = {
    "job_name",
    "command",
    "exit_code",
    "failure_type",
    "artifact_path",
    "stable_signature",
    "specialist_route",
}

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
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text):
    return ANSI_RE.sub("", text)


def extract_json_objects(text):
    decoder = json.JSONDecoder()
    cleaned = strip_ansi(text)
    objects = []
    malformed = []
    for index, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError as exc:
            snippet = cleaned[index : index + 80].replace("\n", "\\n")
            if "ci_failure" in snippet:
                malformed.append(f"offset {index}: malformed ci_failure JSON: {exc.msg}")
            continue
        if isinstance(obj, dict) and "ci_failure" in obj:
            objects.append((index, obj))
    return objects, malformed


def expected_route(failure_type):
    if failure_type in ROUTES:
        return ROUTES[failure_type]
    if failure_type in {"dependency-resolution", "lint-format", "typecheck", "build-compile", "unit-test", "integration-e2e", "timeout", "oom-resource", "network-external", "flaky-suspicion", "unknown"}:
        return "ci-regression-forensics"
    return ""


def expected_signature(failure):
    material = "\n".join(
        [
            str(failure.get("job_name")),
            str(failure.get("command")),
            str(failure.get("exit_code")),
            str(failure.get("failure_type")),
            str(failure.get("artifact_path")),
            str(failure.get("specialist_route")),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def artifact_path_matches_log(artifact_path, log_path):
    raw_path = Path(str(artifact_path))
    log_resolved = log_path.resolve()
    candidates = [raw_path] if raw_path.is_absolute() else [log_path.parent / raw_path, Path.cwd() / raw_path]
    return any(candidate.resolve() == log_resolved for candidate in candidates)


def validate_failure(failure, log_path, *, allow_external_signature=False):
    issues = []
    warnings = []
    if not isinstance(failure, dict):
        return ["ci_failure must be an object"], warnings
    missing = sorted(field for field in FOOTER_REQUIRED_FIELDS if failure.get(field) in (None, "", [], {}))
    for field in missing:
        issues.append(f"ci_failure missing {field}")
    if missing:
        return issues, warnings

    if not isinstance(failure.get("exit_code"), int) or failure.get("exit_code") <= 0:
        issues.append("ci_failure.exit_code must be a non-zero positive integer")
    failure_type = failure.get("failure_type")
    if failure_type not in FAILURE_TYPES:
        issues.append(f"ci_failure.failure_type unknown: {failure_type!r}")
    route = expected_route(failure_type)
    if route and failure.get("specialist_route") != route:
        issues.append(
            f"ci_failure.specialist_route {failure.get('specialist_route')!r} does not match expected route {route!r}"
        )
    signature = failure.get("stable_signature")
    if not isinstance(signature, str) or not SIGNATURE_RE.match(signature):
        issues.append("ci_failure.stable_signature must be 16-64 lowercase hex characters")
    elif failure.get("signature_provenance") == "external":
        if not allow_external_signature:
            issues.append("ci_failure.signature_provenance=external requires --allow-external-signature")
        for field in ("signature_source", "signature_reason"):
            if failure.get(field) in (None, "", [], {}):
                issues.append(f"ci_failure.{field} is required for external signature provenance")
        warnings.append("ci_failure uses external stable_signature provenance")
    else:
        expected = expected_signature(failure)
        if signature != expected:
            issues.append(
                f"ci_failure.stable_signature {signature!r} does not match expected emitter signature {expected!r}"
            )

    if not artifact_path_matches_log(failure.get("artifact_path"), log_path):
        issues.append(
            f"ci_failure.artifact_path {failure.get('artifact_path')!r} does not reference classified log {log_path}"
        )
    return issues, warnings


def validate_log(path, *, strict=False, allow_external_signature=False):
    text = Path(path).read_text(errors="replace")
    log_path = Path(path)
    objects, malformed = extract_json_objects(text)
    warnings = list(malformed)
    valid = []
    invalid = []
    for offset, obj in objects:
        failure = obj.get("ci_failure")
        issues, item_warnings = validate_failure(failure, log_path, allow_external_signature=allow_external_signature)
        warnings.extend(item_warnings)
        record = {"offset": offset, "footer": failure, "issues": issues}
        if issues:
            invalid.append(record)
        else:
            valid.append(record)

    errors = []
    if strict and malformed:
        errors.extend(malformed)
    if strict and invalid:
        for record in invalid:
            errors.extend(record["issues"])
    if valid:
        signatures = {record["footer"]["stable_signature"] for record in valid}
        if len(signatures) > 1:
            errors.append("multiple valid ci_failure footers have conflicting stable_signature values")
    return {
        "log": str(path),
        "valid": not errors and bool(valid),
        "selected": valid[-1]["footer"] if valid else None,
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "invalid": invalid,
        "warnings": warnings,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate structured ci_failure JSON footers in CI logs.")
    parser.add_argument("log")
    parser.add_argument("--strict", action="store_true", help="Treat malformed ci_failure-like JSON as an error.")
    parser.add_argument("--allow-external-signature", action="store_true", help="Accept external stable_signature provenance when source and reason are present.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = validate_log(args.log, strict=args.strict, allow_external_signature=args.allow_external_signature)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if result["selected"]:
            print(f"{args.log}: valid ci_failure footer")
        for issue in result["errors"]:
            print(f"ERROR: {issue}")
        for record in result["invalid"]:
            for issue in record["issues"]:
                print(f"ISSUE: {issue}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
