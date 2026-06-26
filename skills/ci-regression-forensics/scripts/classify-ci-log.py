#!/usr/bin/env python3
import argparse
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate-ci-failure-footer.py")
spec = importlib.util.spec_from_file_location("ci_footer_validator", VALIDATOR_PATH)
ci_footer_validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_footer_validator)


CATEGORY_ANCHORS = {
    "dependency-resolution": [
        r"\bcould not resolve\b",
        r"\bfailed to resolve\b",
        r"\bNo matching distribution found\b",
        r"\bgo: .*: reading .*: 404\b",
    ],
    "lint-format": [r"\bgofmt\b", r"\bblack --check\b", r"\bruff\b", r"\bformat check\b"],
    "typecheck": [r"\btype error\b", r"\btsc\b", r"\bmypy\b", r"\bpyright\b", r"\bTypeScript error\b"],
    "build-compile": [r"\bcompilation failed\b", r"\bcompile error\b", r"\bcannot find symbol\b", r"\bBuild failed\b"],
    "unit-test": [r"^--- FAIL:", r"^FAILED\s+[^ ]+::", r"^FAIL:\s+\w+", r"\bAssertionError\b", r"\bthread '.*' panicked\b"],
    "integration-e2e": [r"\be2e\b", r"\bintegration test\b", r"\bplaywright\b", r"\bselenium\b", r"\bcypress\b"],
    "timeout": [r"\btimed out\b", r"\btimeout\b", r"\bdeadline exceeded\b", r"\bcontext deadline exceeded\b"],
    "oom-resource": [r"\bout of memory\b", r"\bOOM\b", r"\bexit code 137\b", r"\bno space left on device\b"],
    "network-external": [r"\bECONNRESET\b", r"\bENOTFOUND\b", r"\bTLS handshake\b", r"\b503 Service Unavailable\b"],
    "flaky-suspicion": [r"\bflaky\b", r"\brerun succeeded\b", r"\brace detected\b", r"\bdata race\b", r"\brandom seed\b"],
    "benchmark-performance": [r"\bperformance regression\b", r"\bbenchmark.*regress\b", r"\bp95\b", r"\blatency regression\b"],
    "api-schema-compatibility": [
        r"\bBREAKING:\b",
        r"\bbuf breaking\b",
        r"\bOpenAPI contract test failed\b",
        r"\bcontract test failed\b",
        r"\bJSON Schema\b",
    ],
    "formal-verification": [
        r"\bDafny program verifier\b",
        r"\bdafny audit\b",
        r"\bTLC\b",
        r"\bInvariant .* violated\b",
        r"\bmodel checking\b",
    ],
}

GENERIC_FAILURE_PATTERNS = [r"^FAILED$", r"\bfailed\b", r"\berror\b", r"\bFAIL\b"]


def classify_fallback(text):
    scores = Counter()
    evidence = {name: [] for name in CATEGORY_ANCHORS}
    generic_hits = []
    for line in text.splitlines():
        stripped = line.strip()
        for name, patterns in CATEGORY_ANCHORS.items():
            for pattern in patterns:
                if re.search(pattern, stripped, re.I):
                    scores[name] += 3
                    if len(evidence[name]) < 5:
                        evidence[name].append(stripped[:300])
                    break
        if any(re.search(pattern, stripped, re.I) for pattern in GENERIC_FAILURE_PATTERNS):
            if len(generic_hits) < 5:
                generic_hits.append(stripped[:300])

    if not scores:
        return {
            "primary": "unknown",
            "scores": {},
            "evidence": {"generic": generic_hits} if generic_hits else {},
            "confidence": "low",
            "ambiguous": False,
            "runner_up": None,
            "requires_human_review": bool(generic_hits),
        }

    ranked = scores.most_common()
    primary, top_score = ranked[0]
    runner_up = ranked[1][0] if len(ranked) > 1 else None
    runner_score = ranked[1][1] if len(ranked) > 1 else 0
    ambiguous = bool(runner_up and top_score - runner_score <= 1)
    confidence = "high" if top_score >= 3 and not ambiguous else "medium"
    if ambiguous:
        confidence = "low"
    return {
        "primary": primary,
        "scores": dict(scores),
        "evidence": {k: v for k, v in evidence.items() if v},
        "confidence": confidence,
        "ambiguous": ambiguous,
        "runner_up": runner_up,
        "requires_human_review": ambiguous or confidence == "low",
    }


def classify_log(path, *, allow_external_signature=False):
    text = path.read_text(errors="replace")
    footer_result = ci_footer_validator.validate_log(
        path,
        strict=False,
        allow_external_signature=allow_external_signature,
    )
    warnings = list(footer_result.get("warnings", []))
    for invalid in footer_result.get("invalid", []):
        for issue in invalid.get("issues", []):
            warnings.append(issue)

    selected = footer_result.get("selected")
    if selected is not None and footer_result.get("valid"):
        primary = str(selected["failure_type"])
        return {
            "log": str(path),
            "primary": primary,
            "scores": {primary: 100},
            "evidence": {
                "structured-footer": [
                    f"job={selected['job_name']} command={selected['command']} route={selected['specialist_route']}"
                ]
            },
            "confidence": "high",
            "ambiguous": False,
            "runner_up": None,
            "requires_human_review": False,
            "structured_footer": {"valid": True, "ci_failure": selected},
            "warnings": warnings,
        }

    fallback = classify_fallback(text)
    fallback.update(
        {
            "log": str(path),
            "structured_footer": {
                "valid": False,
                "valid_count": footer_result.get("valid_count", 0),
                "invalid_count": footer_result.get("invalid_count", 0),
            },
            "warnings": warnings,
        }
    )
    return fallback


def main():
    parser = argparse.ArgumentParser(description="Classify CI log failure types.")
    parser.add_argument("logs", nargs="+")
    parser.add_argument("--allow-external-signature", action="store_true", help="Accept external stable_signature provenance when source and reason are present.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = [classify_log(Path(log), allow_external_signature=args.allow_external_signature) for log in args.logs]
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['log']}: {result['primary']} confidence={result['confidence']}")
            for warning in result.get("warnings", []):
                print(f"  warning: {warning}")
            for name, score in sorted(result["scores"].items(), key=lambda item: (-item[1], item[0])):
                print(f"  {name}: {score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
