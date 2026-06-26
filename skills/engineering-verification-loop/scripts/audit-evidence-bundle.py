#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


RISK_REQUIREMENTS = {
    "correctness": {"dafny-verification", "property-based-differential-testing"},
    "conformance": {"model-implementation-conformance"},
    "algorithm": {"algorithm-selection-benchmarking"},
    "performance": {"algorithm-selection-benchmarking"},
    "profile": {"profiler-guided-optimization"},
    "api": {"api-contract-compatibility"},
    "ci": {"ci-regression-forensics"},
    "experiment": {"reproducible-experiment-analysis"},
    "distributed": {"tla-distributed-model-checking"},
}

CLAIM_REQUIREMENTS = {
    "performance": {"algorithm-selection-benchmarking"},
    "optimization": {"profiler-guided-optimization"},
    "profile": {"profiler-guided-optimization"},
    "experiment": {"reproducible-experiment-analysis"},
    "implementation_conformance": {"model-implementation-conformance"},
    "api_compatibility": {"api-contract-compatibility"},
}

FORMAL_SKILLS = {"dafny-verification", "tla-distributed-model-checking"}
REQUIRED_EVIDENCE_FIELDS = {"skill", "command", "status", "summary"}
IMPLEMENTATION_LANGUAGES = {"go", "python"}
FORMAL_PROPERTY_FIELDS = {"id", "formal_artifact", "formal_symbol", "kind", "implementation_obligations"}
FORMAL_EVIDENCE_FIELDS = {
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
LANGUAGE_CHECK_FIELDS = {"kind", "command", "status", "summary", "artifact_refs"}
ARTIFACT_FIELDS = {"id", "path", "kind", "sha256", "producer_command", "exit_code"}
ARTIFACT_KINDS = {
    "test-log",
    "audit-result",
    "metrics",
    "profile",
    "ci-log",
    "schema-report",
    "source",
    "fixture",
    "coverage-report",
}
RESULT_ARTIFACT_KINDS = ARTIFACT_KINDS - {"source"}
WORKLOAD_LEVELS = {"synthetic_only", "replay", "shadow", "canary", "production"}
PRODUCTION_WORKLOAD_LEVELS = {"replay", "shadow", "canary", "production"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonempty(value):
    return value not in (None, "", [], {})


def find_repo_root(start):
    start = Path(start)
    cwd = start if start.is_dir() else start.parent
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=True,
        )
        return Path(result.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def resolve_path(raw_path, base_dir, repo_root=None):
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    candidates = [base_dir / path]
    if repo_root is not None:
        candidates.append(repo_root / path)
    candidates.append(Path.cwd() / path)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def is_relative_to(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def limitation_matches(item, *, scope=None, disposition=None, related_field=None):
    if not isinstance(item, dict):
        return False
    if scope is not None and item.get("scope") != scope:
        return False
    if disposition is not None:
        dispositions = {disposition} if isinstance(disposition, str) else set(disposition)
        if item.get("disposition") not in dispositions:
            return False
    if related_field is not None:
        related = item.get("related_fields", [])
        if related_field not in related:
            return False
    return True


def has_limitation(unsupported_claims, *, scope=None, disposition=None, related_field=None):
    return any(
        limitation_matches(item, scope=scope, disposition=disposition, related_field=related_field)
        for item in unsupported_claims
    )


def audit_unsupported_claims(bundle, issues):
    unsupported = bundle.get("unsupported_claims", [])
    if unsupported in (None, ""):
        return []
    if not isinstance(unsupported, list):
        issues.append("unsupported_claims must be a list when present")
        return []
    for index, item in enumerate(unsupported):
        if not isinstance(item, dict):
            issues.append(f"unsupported_claims[{index}] must be a structured object, not free text")
            continue
        for field in ("id", "claim", "reason", "scope", "disposition", "related_fields"):
            if not nonempty(item.get(field)):
                issues.append(f"unsupported_claims[{index}] missing {field}")
        if item.get("related_fields") is not None and not isinstance(item.get("related_fields"), list):
            issues.append(f"unsupported_claims[{index}].related_fields must be a list")
    return unsupported


def infer_target_languages(bundle):
    targets = bundle.get("targets", [])
    languages = set()
    if not isinstance(targets, list):
        return languages
    for target in targets:
        if isinstance(target, dict) and target.get("language") in IMPLEMENTATION_LANGUAGES:
            languages.add(target["language"])
    return languages


def audit_targets_and_languages(bundle, issues, warnings):
    targets = bundle.get("targets", [])
    if targets is not None and targets != [] and not isinstance(targets, list):
        issues.append("targets must be a list when present")
        targets = []
    for index, target in enumerate(targets if isinstance(targets, list) else []):
        if not isinstance(target, dict):
            issues.append(f"targets[{index}] must be an object")
            continue
        if target.get("language") not in IMPLEMENTATION_LANGUAGES:
            warnings.append(f"targets[{index}] unsupported language {target.get('language')!r}")
        if not isinstance(target.get("paths", []), list) or not target.get("paths"):
            issues.append(f"targets[{index}] missing non-empty paths")

    implementation_languages = bundle.get("implementation_languages", [])
    if not isinstance(implementation_languages, list):
        issues.append("implementation_languages must be a list")
        implementation_languages = []
    declared = {language for language in implementation_languages if language in IMPLEMENTATION_LANGUAGES}
    for language in implementation_languages:
        if language not in IMPLEMENTATION_LANGUAGES:
            warnings.append(f"unsupported implementation language: {language}")

    target_languages = infer_target_languages(bundle)
    if target_languages and declared != target_languages:
        issues.append(
            f"implementation_languages {sorted(declared)} does not match targets {sorted(target_languages)}"
        )
    if target_languages and not implementation_languages:
        issues.append("implementation_languages is required when Go/Python targets are declared")
    return declared or target_languages


def audit_artifacts(bundle, base_dir, repo_root, issues):
    raw_artifacts = bundle.get("artifacts")
    evidence = bundle.get("evidence", {})
    has_passed_evidence = any(
        isinstance(entries, list)
        and any(isinstance(entry, dict) and entry.get("status") == "passed" for entry in entries)
        for entries in evidence.values()
    )
    if has_passed_evidence and not isinstance(raw_artifacts, list):
        issues.append("artifacts manifest is required for passed evidence")
        return {}
    if raw_artifacts is None:
        return {}
    if not isinstance(raw_artifacts, list):
        issues.append("artifacts must be a list")
        return {}

    artifacts = {}
    for index, artifact in enumerate(raw_artifacts):
        if not isinstance(artifact, dict):
            issues.append(f"artifacts[{index}] must be an object")
            continue
        missing = sorted(field for field in ARTIFACT_FIELDS if not nonempty(artifact.get(field)))
        for field in missing:
            issues.append(f"artifacts[{index}] missing {field}")
        artifact_id = artifact.get("id")
        if artifact_id in artifacts:
            issues.append(f"artifacts[{index}] duplicate id {artifact_id!r}")
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(f"artifacts[{index}] unknown kind {artifact.get('kind')!r}")
        path = resolve_path(artifact.get("path", ""), base_dir, repo_root)
        allowed_root = repo_root
        if ".." in Path(str(artifact.get("path", ""))).parts:
            issues.append(f"artifacts[{index}] path must not escape with '..': {artifact.get('path')}")
        if path.is_absolute() and not is_relative_to(path, allowed_root):
            issues.append(f"artifacts[{index}] path is outside allowed root {allowed_root}: {artifact.get('path')}")
        if not path.is_absolute() and path.exists() and not is_relative_to(path, allowed_root):
            issues.append(f"artifacts[{index}] resolved path is outside allowed root {allowed_root}: {artifact.get('path')}")
        if not path.exists():
            issues.append(f"artifacts[{index}] path does not exist: {artifact.get('path')}")
        elif artifact.get("sha256") and sha256_file(path) != artifact.get("sha256"):
            issues.append(f"artifacts[{index}] sha256 mismatch for {artifact.get('path')}")
        if artifact.get("exit_code") is not None and not isinstance(artifact.get("exit_code"), int):
            issues.append(f"artifacts[{index}].exit_code must be an integer")
        artifacts[artifact_id] = artifact
    return artifacts


def validate_artifact_refs(refs, artifacts, issues, prefix, *, passed=False):
    if not isinstance(refs, list) or not refs:
        issues.append(f"{prefix}: artifact_refs must be a non-empty list")
        return
    kinds = []
    for ref in refs:
        artifact = artifacts.get(ref)
        if artifact is None:
            issues.append(f"{prefix}: artifact_refs references unknown artifact id {ref!r}")
            continue
        kinds.append(artifact.get("kind"))
        if passed and artifact.get("exit_code") != 0:
            issues.append(f"{prefix}: passed evidence references artifact {ref!r} with exit_code={artifact.get('exit_code')}")
    if passed and not any(kind in RESULT_ARTIFACT_KINDS for kind in kinds):
        issues.append(f"{prefix}: passed gate must reference at least one result artifact, not only source artifacts")


def has_passed_skill(evidence, skill):
    for entries in evidence.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("skill") == skill and entry.get("status") == "passed":
                return True
    return False


def has_formal_model_evidence(bundle):
    evidence = bundle.get("evidence", {})
    for entries in evidence.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("skill") in FORMAL_SKILLS and entry.get("status") == "passed":
                return True
    coverage = bundle.get("formal_coverage_map")
    if isinstance(coverage, dict):
        model = coverage.get("model", {})
        return isinstance(model, dict) and model.get("kind") in {"dafny", "tla"} and model.get("status") == "passed"
    return False


def load_formal_coverage_map(bundle, base_dir, repo_root, issues):
    coverage = bundle.get("formal_coverage_map")
    if isinstance(coverage, str):
        if ".." in Path(coverage).parts:
            issues.append(f"formal_coverage_map path must not escape with '..': {coverage}")
            return None
        path = resolve_path(coverage, base_dir, repo_root)
        if not is_relative_to(path, repo_root):
            issues.append(f"formal_coverage_map path is outside allowed root {repo_root}: {coverage}")
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"formal_coverage_map: failed to load {coverage}: {exc}")
            return None
    return coverage


def audit_formal_coverage_map(coverage, languages, issues, warnings):
    if not isinstance(coverage, dict):
        issues.append("formal_coverage_map must be an object or JSON file path")
        return
    model = coverage.get("model")
    if not isinstance(model, dict):
        issues.append("formal_coverage_map.model must be an object")
    elif model.get("kind") not in {"dafny", "tla"}:
        issues.append("formal_coverage_map.model.kind must be dafny or tla")

    properties = coverage.get("properties")
    evidence = coverage.get("evidence")
    if not isinstance(properties, list) or not properties:
        issues.append("formal_coverage_map.properties must be a non-empty list")
        properties = []
    if not isinstance(evidence, list) or not evidence:
        issues.append("formal_coverage_map.evidence must be a non-empty list")
        evidence = []

    property_ids = set()
    for index, prop in enumerate(properties):
        if not isinstance(prop, dict):
            issues.append(f"formal_coverage_map.properties[{index}]: entry must be an object")
            continue
        missing = sorted(field for field in FORMAL_PROPERTY_FIELDS if not nonempty(prop.get(field)))
        for field in missing:
            issues.append(f"formal_coverage_map.properties[{index}]: missing {field}")
        prop_id = str(prop.get("id", ""))
        if prop_id in property_ids:
            issues.append(f"formal_coverage_map.properties[{index}]: duplicate property id {prop_id!r}")
        elif prop_id:
            property_ids.add(prop_id)
        semantics = prop.get("model_semantics", {})
        if "go" in languages and isinstance(semantics, dict) and semantics.get("integer_domain") == "unbounded_math_int":
            target_semantics = prop.get("target_semantics", {})
            if not isinstance(target_semantics, dict) or not nonempty(target_semantics.get("integer_width")):
                issues.append(
                    f"formal_coverage_map.properties[{index}]: Go target needs integer_width target_semantics for unbounded_math_int model"
                )

    covered = set()
    covered_by_language = {}
    evidence_languages = set()
    evidence_ids = set()
    for index, entry in enumerate(evidence):
        prefix = f"formal_coverage_map.evidence[{index}]"
        if not isinstance(entry, dict):
            issues.append(f"{prefix}: entry must be an object")
            continue
        missing = sorted(field for field in FORMAL_EVIDENCE_FIELDS if not nonempty(entry.get(field)))
        for field in missing:
            issues.append(f"{prefix}: missing {field}")
        entry_id = entry.get("id")
        if entry_id in evidence_ids:
            issues.append(f"{prefix}: duplicate evidence id {entry_id!r}")
        elif entry_id:
            evidence_ids.add(entry_id)
        language = entry.get("language")
        if language not in IMPLEMENTATION_LANGUAGES:
            warnings.append(f"{prefix}: unsupported language {language!r}")
        else:
            evidence_languages.add(language)
        if entry.get("status") != "passed":
            issues.append(f"{prefix}: status is {entry.get('status')!r}, expected 'passed'")
            continue
        covers = entry.get("covers")
        if not isinstance(covers, list) or not covers:
            issues.append(f"{prefix}: covers must be a non-empty list")
            continue
        for prop_id in covers:
            if prop_id not in property_ids:
                issues.append(f"{prefix}: covers unknown property {prop_id!r}")
            else:
                covered.add(prop_id)
                if language in IMPLEMENTATION_LANGUAGES:
                    covered_by_language.setdefault(language, set()).add(prop_id)

    for language in sorted(languages):
        if language not in evidence_languages:
            issues.append(f"formal_coverage_map: missing {language} conformance evidence")
        for prop_id in sorted(property_ids - covered_by_language.get(language, set())):
            issues.append(f"formal_coverage_map: {language} evidence missing property {prop_id!r}")
    for prop_id in sorted(property_ids - covered):
        issues.append(f"formal_coverage_map: property {prop_id} has no passed implementation evidence")


def required_language_kinds(language, risks, traits):
    required = {"unit"}
    traits = set(traits)
    risks = set(risks)
    if language == "go":
        if traits & {"concurrency", "race"}:
            required.add("race")
        if traits & {"parser", "validator", "stateful", "algorithmic"}:
            required.add("fuzz_or_differential")
    if language == "python" and "correctness" in risks:
        required.add("property_or_differential")
    if risks & {"performance", "algorithm", "experiment"}:
        required.add("benchmark")
    if "profile" in risks:
        required.add("profile")
    return required


def satisfies_kind(required, kinds):
    if required == "fuzz_or_differential":
        return bool(kinds & {"fuzz", "differential", "property", "fixture", "corpus"})
    if required == "property_or_differential":
        return bool(kinds & {"property", "hypothesis", "differential", "fixture"})
    return required in kinds


def audit_language_checks(bundle, languages, risks, artifacts, issues):
    checks = bundle.get("language_checks")
    if not isinstance(checks, dict):
        if languages:
            issues.append("language_checks must be an object keyed by language")
        return
    traits = bundle.get("risk_traits", [])
    if traits and not isinstance(traits, list):
        issues.append("risk_traits must be a list")
        traits = []
    for language in sorted(languages):
        entries = checks.get(language, [])
        if not isinstance(entries, list) or not entries:
            issues.append(f"language_checks.{language} must be a non-empty list")
            continue
        kinds = set()
        for index, entry in enumerate(entries):
            prefix = f"language_checks.{language}[{index}]"
            if not isinstance(entry, dict):
                issues.append(f"{prefix}: entry must be an object")
                continue
            missing = sorted(field for field in LANGUAGE_CHECK_FIELDS if not nonempty(entry.get(field)))
            for field in missing:
                issues.append(f"{prefix}: missing {field}")
            kind = entry.get("kind")
            if nonempty(kind):
                kinds.add(kind)
            if entry.get("status") != "passed":
                issues.append(f"{prefix}: status is {entry.get('status')!r}, expected 'passed'")
            validate_artifact_refs(entry.get("artifact_refs"), artifacts, issues, prefix, passed=entry.get("status") == "passed")
        for required in sorted(required_language_kinds(language, risks, traits)):
            if not satisfies_kind(required, kinds):
                issues.append(f"language_checks.{language}: missing required {required} check")


def audit_workloads_and_claims(bundle, risks, unsupported_claims, issues):
    risk_set = set(risks)
    needs_workload = bool({"performance", "algorithm", "experiment", "profile"} & risk_set)
    workloads = bundle.get("workloads")
    if workloads is None and "workload_validity" in bundle:
        issues.append("workload_validity is deprecated; use structured workloads[]")
    if needs_workload and not isinstance(workloads, list):
        issues.append("workloads must be a non-empty list for performance, algorithm, profile, or experiment risks")
        workloads = []
    if workloads is None:
        workloads = []
    if not isinstance(workloads, list):
        issues.append("workloads must be a list")
        workloads = []

    workload_by_id = {}
    for index, workload in enumerate(workloads):
        prefix = f"workloads[{index}]"
        if not isinstance(workload, dict):
            issues.append(f"{prefix} must be an object")
            continue
        for field in ("id", "level", "source"):
            if not nonempty(workload.get(field)):
                issues.append(f"{prefix} missing {field}")
        workload_id = workload.get("id")
        if workload_id in workload_by_id:
            issues.append(f"{prefix} duplicate id {workload_id!r}")
        elif workload_id:
            workload_by_id[workload_id] = workload
        level = workload.get("level")
        if level not in WORKLOAD_LEVELS:
            issues.append(f"{prefix}.level must be one of {sorted(WORKLOAD_LEVELS)}")
        if workload.get("production_claim") is True and level == "synthetic_only":
            issues.append(f"{prefix}: synthetic_only cannot support a production impact claim")
        if level == "synthetic_only" and not has_limitation(
            unsupported_claims,
            scope="production",
            disposition={"blocking_for_production", "accepted_local_only"},
            related_field="workloads",
        ):
            issues.append(f"{prefix}: synthetic_only workload requires structured production limitation in unsupported_claims")
        if level in {"replay", "shadow", "canary", "production"}:
            for field in ("collection_window", "sample_count", "runtime_environment", "metric_definition"):
                if not nonempty(workload.get(field)):
                    issues.append(f"{prefix}: {level} workload missing {field}")
        if level in {"canary", "production"} and not nonempty(workload.get("traffic_slice")):
            issues.append(f"{prefix}: {level} workload missing traffic_slice")

    claims = bundle.get("claims", [])
    if needs_workload and not isinstance(claims, list):
        issues.append("claims must be a list")
        claims = []
    if needs_workload and not claims:
        issues.append("claims must be a non-empty structured list for workload-backed risks")
    for index, claim in enumerate(claims if isinstance(claims, list) else []):
        prefix = f"claims[{index}]"
        if not isinstance(claim, dict):
            issues.append(f"{prefix} must be an object")
            continue
        for field in ("id", "kind", "scope", "evidence_refs"):
            if field == "evidence_refs" and claim.get("kind") in CLAIM_REQUIREMENTS:
                if not isinstance(claim.get(field), list) or not claim.get(field):
                    issues.append(f"{prefix} missing non-empty {field}")
            elif field != "evidence_refs" and not nonempty(claim.get(field)):
                issues.append(f"{prefix} missing {field}")
        workload_id = claim.get("workload_id")
        if workload_id:
            workload = workload_by_id.get(workload_id)
            if workload is None:
                issues.append(f"{prefix}: references unknown workload_id {workload_id!r}")
            elif claim.get("scope") == "production" and workload.get("level") not in PRODUCTION_WORKLOAD_LEVELS:
                issues.append(f"{prefix}: production claim requires replay, shadow, canary, or production workload")
        elif claim.get("kind") in {"performance", "optimization", "profile", "experiment"}:
            issues.append(f"{prefix}: workload_id is required for workload-backed claim")
        if claim.get("scope") == "production" and not workload_id:
            issues.append(f"{prefix}: production claim requires workload_id")

    evidence_text = json.dumps(bundle.get("evidence", {})).lower()
    if "production" in evidence_text and not any(isinstance(claim, dict) and claim.get("scope") == "production" for claim in claims):
        issues.append("evidence summaries mention production but no structured production-scoped claim exists")


def audit_claim_requirements(bundle, evidence, issues):
    claims = bundle.get("claims", [])
    if not isinstance(claims, list):
        return
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        required = CLAIM_REQUIREMENTS.get(claim.get("kind"))
        if not required:
            continue
        for skill in sorted(required):
            if not has_passed_skill(evidence, skill):
                issues.append(f"claims[{index}]: missing passed evidence from {skill}")


def collect_passed_artifact_refs(evidence):
    all_refs = set()
    refs_by_skill = {}
    if not isinstance(evidence, dict):
        return all_refs, refs_by_skill
    for entries in evidence.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("status") != "passed":
                continue
            refs = entry.get("artifact_refs", [])
            if not isinstance(refs, list):
                continue
            skill = entry.get("skill")
            for ref in refs:
                all_refs.add(ref)
                refs_by_skill.setdefault(skill, set()).add(ref)
    return all_refs, refs_by_skill


def audit_claim_links(bundle, evidence, artifacts, issues):
    claims = bundle.get("claims", [])
    if not isinstance(claims, list):
        return
    passed_refs, refs_by_skill = collect_passed_artifact_refs(evidence)
    artifact_ids = set(artifacts)
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        refs = claim.get("evidence_refs")
        if refs is None:
            continue
        prefix = f"claims[{index}]"
        if not isinstance(refs, list) or not refs:
            issues.append(f"{prefix}.evidence_refs must be a non-empty list")
            continue
        ref_set = set(refs)
        for ref in sorted(ref_set - artifact_ids):
            issues.append(f"{prefix}.evidence_refs references unknown artifact id {ref!r}")
        for ref in sorted(ref_set - passed_refs):
            issues.append(f"{prefix}.evidence_refs references artifact {ref!r} that is not linked from passed evidence")
        for skill in sorted(CLAIM_REQUIREMENTS.get(claim.get("kind"), set())):
            if not (ref_set & refs_by_skill.get(skill, set())):
                issues.append(f"{prefix}.evidence_refs are not linked to passed evidence from {skill}")


def formal_property_ids(coverage):
    if not isinstance(coverage, dict):
        return set()
    properties = coverage.get("properties", [])
    if not isinstance(properties, list):
        return set()
    return {prop.get("id") for prop in properties if isinstance(prop, dict) and nonempty(prop.get("id"))}


def formal_evidence_languages(coverage):
    if not isinstance(coverage, dict):
        return set()
    evidence = coverage.get("evidence", [])
    if not isinstance(evidence, list):
        return set()
    return {
        entry.get("language")
        for entry in evidence
        if isinstance(entry, dict) and entry.get("language") in IMPLEMENTATION_LANGUAGES
    }


def audit_claim_property_ids(bundle, coverage, issues):
    claims = bundle.get("claims", [])
    if not isinstance(claims, list):
        return
    known_properties = formal_property_ids(coverage)
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict) or claim.get("kind") != "implementation_conformance":
            continue
        prefix = f"claims[{index}].property_ids"
        property_ids = claim.get("property_ids")
        if not isinstance(property_ids, list) or not property_ids:
            issues.append(f"{prefix} must be a non-empty list for implementation_conformance claims")
            continue
        seen = set()
        for property_id in property_ids:
            if not nonempty(property_id):
                issues.append(f"{prefix} contains an empty property id")
                continue
            if property_id in seen:
                issues.append(f"{prefix} contains duplicate property id {property_id!r}")
            seen.add(property_id)
            if property_id not in known_properties:
                issues.append(f"{prefix} references unknown formal property {property_id!r}")


def audit_ci_footer(bundle, risks, unsupported_claims, issues):
    if "ci" not in risks:
        return
    footer = bundle.get("ci_structured_footer")
    footer_present = isinstance(footer, dict) and footer.get("present") is True
    if not footer_present and not has_limitation(
        unsupported_claims,
        scope="ci-observability",
        disposition={"blocking_for_ci_readiness", "accepted_legacy_ci"},
        related_field="ci_structured_footer",
    ):
        issues.append("ci_structured_footer.present=true is required for CI risk unless structured unsupported_claims documents missing footer")
    if footer_present:
        for field in ("artifact", "failure_type", "specialist_route"):
            if not nonempty(footer.get(field)):
                issues.append(f"ci_structured_footer missing {field}")


def audit(bundle, base_dir=Path("."), repo_root=None):
    issues = []
    warnings = []
    repo_root = Path(repo_root).resolve() if repo_root is not None else find_repo_root(base_dir)
    if not isinstance(bundle, dict):
        return ["bundle root must be an object"], warnings

    if bundle.get("schema_version") != "1.0":
        issues.append("schema_version must be '1.0'")
    if not nonempty(bundle.get("change_summary")):
        issues.append("missing change_summary")

    risks = bundle.get("risks")
    if not isinstance(risks, list) or not risks:
        issues.append("risks must be a non-empty list")
        risks = []
    if len(risks) != len(set(risks)):
        issues.append("risks contains duplicate labels")
    for risk in risks:
        if risk not in RISK_REQUIREMENTS:
            issues.append(f"unknown risk label: {risk}")

    evidence = bundle.get("evidence")
    if not isinstance(evidence, dict):
        issues.append("evidence must be an object keyed by risk")
        evidence = {}

    unsupported_claims = audit_unsupported_claims(bundle, issues)
    languages = audit_targets_and_languages(bundle, issues, warnings)
    target_languages = infer_target_languages(bundle)
    artifacts = audit_artifacts(bundle, base_dir, repo_root, issues)
    claims = bundle.get("claims", [])
    claim_entries = claims if isinstance(claims, list) else []
    has_conformance_claim = any(
        isinstance(claim, dict) and claim.get("kind") == "implementation_conformance"
        for claim in claim_entries
    )
    coverage = None
    gate_languages = set(languages)
    if has_conformance_claim:
        implementation_languages = bundle.get("implementation_languages")
        if not isinstance(implementation_languages, list) or not implementation_languages:
            issues.append("implementation_languages is required for implementation_conformance claims")
        if not target_languages:
            issues.append("targets must declare Go/Python target entries for implementation_conformance claims")

    for risk in risks:
        if risk not in RISK_REQUIREMENTS:
            continue
        entries = evidence.get(risk)
        if not isinstance(entries, list) or not entries:
            issues.append(f"{risk}: missing evidence entries")
            continue
        passed_skills = set()
        for index, entry in enumerate(entries):
            prefix = f"{risk}[{index}]"
            if not isinstance(entry, dict):
                issues.append(f"{prefix}: evidence entry must be an object")
                continue
            missing = sorted(field for field in REQUIRED_EVIDENCE_FIELDS if not nonempty(entry.get(field)))
            for field in missing:
                issues.append(f"{prefix}: missing {field}")
            if entry.get("status") != "passed":
                issues.append(f"{prefix}: status is {entry.get('status')!r}, expected 'passed'")
            validate_artifact_refs(entry.get("artifact_refs"), artifacts, issues, prefix, passed=entry.get("status") == "passed")
            skill = entry.get("skill")
            if skill in RISK_REQUIREMENTS[risk] and entry.get("status") == "passed":
                passed_skills.add(skill)
        missing_skills = sorted(RISK_REQUIREMENTS[risk] - passed_skills)
        for skill in missing_skills:
            issues.append(f"{risk}: missing passed evidence from {skill}")

    if languages and has_formal_model_evidence(bundle):
        if "conformance" not in risks:
            issues.append("conformance risk is required for Go/Python implementation with Dafny/TLA evidence")
        if not has_passed_skill({"conformance": evidence.get("conformance", [])}, "model-implementation-conformance"):
            issues.append("conformance: Go/Python implementation with Dafny/TLA evidence requires passed model-implementation-conformance gate")

    if ("correctness" in risks and languages) or has_conformance_claim:
        coverage = load_formal_coverage_map(bundle, base_dir, repo_root, issues)
        if coverage is None:
            if "correctness" in risks and languages:
                issues.append("formal_coverage_map is required for Go/Python correctness evidence")
            if has_conformance_claim:
                issues.append("formal_coverage_map is required for implementation_conformance claims")
        else:
            if has_conformance_claim and not gate_languages:
                gate_languages = formal_evidence_languages(coverage)
            audit_formal_coverage_map(coverage, gate_languages, issues, warnings)

    audit_language_checks(bundle, gate_languages, risks, artifacts, issues)
    audit_workloads_and_claims(bundle, risks, unsupported_claims, issues)
    audit_claim_requirements(bundle, evidence, issues)
    audit_claim_links(bundle, evidence, artifacts, issues)
    audit_claim_property_ids(bundle, coverage, issues)
    audit_ci_footer(bundle, risks, unsupported_claims, issues)

    return issues, warnings


def main():
    parser = argparse.ArgumentParser(description="Audit an engineering verification evidence bundle.")
    parser.add_argument("bundle")
    parser.add_argument("--repo-root", help="Repository root used for artifact path containment and repo-relative paths.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        bundle_path = Path(args.bundle)
        bundle = load(bundle_path)
        issues, warnings = audit(bundle, bundle_path.parent, args.repo_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {"bundle": args.bundle, "issues": issues, "warnings": warnings}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"ISSUE: {issue}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if not issues:
            print("[engineering-verification-loop] evidence bundle passed")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
