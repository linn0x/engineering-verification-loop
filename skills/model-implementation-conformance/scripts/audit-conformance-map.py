#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


SUPPORTED_LANGUAGES = {"go", "python"}
MODEL_KINDS = {"dafny", "tla"}
REQUIRED_MODEL_FIELDS = {"kind", "artifact", "status"}
REQUIRED_PROPERTY_FIELDS = {"id", "formal_artifact", "formal_symbol", "kind", "implementation_obligations"}
REQUIRED_TARGET_FIELDS = {"language", "artifact", "entrypoints"}
REQUIRED_EVIDENCE_FIELDS = {
    "id",
    "language",
    "implementation_artifact",
    "entrypoint",
    "evidence_type",
    "test_command",
    "result_artifact",
    "status",
    "covers",
}
GENERATED_FIELDS = {"generator", "source_model_sha256", "generated_artifact_sha256"}
TRACE_PROPERTY_KINDS = {"state_machine", "temporal", "trace"}


def nonempty(value):
    return value not in (None, "", [], {})


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def has_structured_boundary(unsupported_claims):
    if not isinstance(unsupported_claims, list):
        return False
    return any(
        isinstance(item, dict)
        and item.get("scope") == "implementation-conformance"
        and item.get("disposition") in {"not_machine_checked", "tested_conformance_only"}
        for item in unsupported_claims
    )


def audit(doc):
    issues = []
    warnings = []
    if not isinstance(doc, dict):
        return ["conformance map root must be an object"], warnings

    if doc.get("schema_version") != "1.0":
        issues.append("schema_version must be '1.0'")

    model = doc.get("model")
    model_kind = None
    if not isinstance(model, dict):
        issues.append("model must be an object")
    else:
        for field in REQUIRED_MODEL_FIELDS:
            if not nonempty(model.get(field)):
                issues.append(f"model missing {field}")
        model_kind = model.get("kind")
        if model_kind not in MODEL_KINDS:
            issues.append(f"model.kind must be one of {sorted(MODEL_KINDS)}")
        if model.get("status") != "passed":
            issues.append(f"model status is {model.get('status')!r}, expected 'passed'")

    properties = doc.get("properties")
    if not isinstance(properties, list) or not properties:
        issues.append("properties must be a non-empty list")
        properties = []
    property_ids = set()
    trace_property_ids = set()
    for index, prop in enumerate(properties):
        prefix = f"properties[{index}]"
        if not isinstance(prop, dict):
            issues.append(f"{prefix} must be an object")
            continue
        missing = sorted(field for field in REQUIRED_PROPERTY_FIELDS if not nonempty(prop.get(field)))
        for field in missing:
            issues.append(f"{prefix} missing {field}")
        prop_id = prop.get("id")
        if prop_id in property_ids:
            issues.append(f"{prefix} duplicate property id {prop_id!r}")
        elif prop_id:
            property_ids.add(str(prop_id))
        if prop.get("kind") in TRACE_PROPERTY_KINDS:
            trace_property_ids.add(str(prop_id))

    targets = doc.get("implementation_targets")
    if not isinstance(targets, list) or not targets:
        issues.append("implementation_targets must be a non-empty list")
        targets = []
    target_pairs = set()
    target_languages = set()
    for index, target in enumerate(targets):
        prefix = f"implementation_targets[{index}]"
        if not isinstance(target, dict):
            issues.append(f"{prefix} must be an object")
            continue
        missing = sorted(field for field in REQUIRED_TARGET_FIELDS if not nonempty(target.get(field)))
        for field in missing:
            issues.append(f"{prefix} missing {field}")
        language = target.get("language")
        if language not in SUPPORTED_LANGUAGES:
            warnings.append(f"{prefix} unsupported language {language!r}")
            continue
        target_languages.add(language)
        entrypoints = target.get("entrypoints", [])
        if not isinstance(entrypoints, list) or not entrypoints:
            issues.append(f"{prefix}.entrypoints must be a non-empty list")
            continue
        for entrypoint in entrypoints:
            target_pairs.add((language, target.get("artifact"), entrypoint))

    evidence = doc.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        issues.append("evidence must be a non-empty list")
        evidence = []

    covered = set()
    covered_by_pair = {}
    passed_pairs = set()
    passed_languages = set()
    evidence_ids = set()
    handwritten_present = False
    trace_evidence_properties = set()
    for index, entry in enumerate(evidence):
        prefix = f"evidence[{index}]"
        if not isinstance(entry, dict):
            issues.append(f"{prefix} must be an object")
            continue
        missing = sorted(field for field in REQUIRED_EVIDENCE_FIELDS if not nonempty(entry.get(field)))
        for field in missing:
            issues.append(f"{prefix} missing {field}")
        entry_id = entry.get("id")
        if entry_id in evidence_ids:
            issues.append(f"{prefix} duplicate evidence id {entry_id!r}")
        elif entry_id:
            evidence_ids.add(entry_id)

        language = entry.get("language")
        if language not in SUPPORTED_LANGUAGES:
            warnings.append(f"{prefix} unsupported language {language!r}")
        evidence_type = entry.get("evidence_type")
        if evidence_type == "generated_code":
            for field in GENERATED_FIELDS:
                if not nonempty(entry.get(field)):
                    issues.append(f"{prefix} generated_code evidence missing {field}")
        else:
            handwritten_present = True
        if entry.get("status") != "passed":
            issues.append(f"{prefix} status is {entry.get('status')!r}, expected 'passed'")
            continue

        passed_languages.add(language)
        pair = (language, entry.get("implementation_artifact"), entry.get("entrypoint"))
        passed_pairs.add(pair)
        covers = entry.get("covers")
        if not isinstance(covers, list) or not covers:
            issues.append(f"{prefix} covers must be a non-empty list")
            continue
        for prop_id in covers:
            if prop_id not in property_ids:
                issues.append(f"{prefix} covers unknown property {prop_id!r}")
            else:
                covered.add(prop_id)
                covered_by_pair.setdefault(pair, set()).add(prop_id)
                if evidence_type in {"trace", "trace_replay", "state_machine_trace"}:
                    trace_evidence_properties.add(prop_id)

    for prop_id in sorted(property_ids - covered):
        issues.append(f"property {prop_id} has no passed implementation evidence")
    for language in sorted(target_languages):
        if language not in passed_languages:
            issues.append(f"implementation_targets: missing passed evidence for {language}")
    for language, artifact, entrypoint in sorted(target_pairs):
        if (language, artifact, entrypoint) not in passed_pairs:
            issues.append(f"implementation_targets: missing passed evidence for {language} {artifact}:{entrypoint}")
            continue
        missing_for_pair = property_ids - covered_by_pair.get((language, artifact, entrypoint), set())
        for prop_id in sorted(missing_for_pair):
            issues.append(
                f"implementation_targets: {language} {artifact}:{entrypoint} missing property {prop_id} evidence"
            )

    if model_kind == "tla":
        trace_property_ids.update(property_ids)
    for prop_id in sorted(trace_property_ids - trace_evidence_properties):
        issues.append(f"property {prop_id} requires trace evidence")

    unsupported = doc.get("unsupported_claims", [])
    if unsupported and not isinstance(unsupported, list):
        issues.append("unsupported_claims must be a list when present")
        unsupported = []
    if handwritten_present and not has_structured_boundary(unsupported):
        issues.append("handwritten Go/Python evidence requires structured unsupported_claims boundary for non-machine-checked refinement")

    return issues, warnings


def main():
    parser = argparse.ArgumentParser(description="Audit model-to-implementation conformance evidence.")
    parser.add_argument("conformance_map")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        doc = load(args.conformance_map)
        issues, warnings = audit(doc)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {"conformance_map": args.conformance_map, "issues": issues, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"ISSUE: {issue}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if not issues:
            print("[model-implementation-conformance] conformance map passed")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
