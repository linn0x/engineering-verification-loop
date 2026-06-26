#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


MISSING = object()


def project_state(state, projection, label):
    issues = []
    if not projection:
        return state, issues
    if not isinstance(state, dict):
        return state, [f"{label} must be an object when observable_projection is used"]
    projected = {}
    for key in projection:
        if key not in state:
            issues.append(f"{label} missing projection key {key}")
            continue
        projected[key] = state[key]
    return projected, issues


def load_jsonl(path):
    records = {}
    seen_any = False
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            seen_any = True
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
            case_id = obj.get("id")
            if not case_id:
                raise RuntimeError(f"{path}:{line_no}: missing id")
            if case_id in records:
                raise RuntimeError(f"{path}:{line_no}: duplicate id {case_id}")
            if not isinstance(obj.get("steps"), list) or not obj.get("steps"):
                raise RuntimeError(f"{path}:{line_no}: steps must be a non-empty list")
            records[case_id] = obj
    if not seen_any:
        raise RuntimeError(f"{path}: no records")
    return records


def observed_state(step):
    for key in ("observed_state", "actual_state"):
        if key in step:
            return step[key]
    return MISSING


def same_step_signature(expected_step, actual_step):
    return expected_step.get("action") == actual_step.get("action") and expected_step.get("input", {}) == actual_step.get("input", {})


def compare_expected_step(case_id, expected_step, actual_step, label, projection):
    issues = []
    if expected_step.get("action") != actual_step.get("action"):
        issues.append(f"{case_id}: {label} action mismatch expected={expected_step.get('action')} actual={actual_step.get('action')}")
    if expected_step.get("input", {}) != actual_step.get("input", {}):
        issues.append(f"{case_id}: {label} input mismatch")
    if observed_state(actual_step) is MISSING:
        issues.append(f"{case_id}: {label} missing observed_state or actual_state")
        return issues, None
    observed = observed_state(actual_step)
    expected_state, expected_projection_issues = project_state(
        expected_step.get("expected_state"),
        projection,
        f"{case_id}: {label} expected_state",
    )
    issues.extend(expected_projection_issues)
    actual_state, actual_projection_issues = project_state(
        observed,
        projection,
        f"{case_id}: {label} actual_state",
    )
    issues.extend(actual_projection_issues)
    if expected_projection_issues or actual_projection_issues:
        return issues, None
    if expected_state != actual_state:
        issues.append(
            f"{case_id}: {label} state mismatch expected={json.dumps(expected_state, sort_keys=True)} actual={json.dumps(actual_state, sort_keys=True)}"
        )
    return issues, actual_state


def projected_actual_state(case_id, actual_step, actual_index, projection):
    if observed_state(actual_step) is MISSING:
        return [f"{case_id}: actual step {actual_index} missing observed_state or actual_state"], None
    actual_state, projection_issues = project_state(
        observed_state(actual_step),
        projection,
        f"{case_id}: actual step {actual_index} actual_state",
    )
    return projection_issues, None if projection_issues else actual_state


def compare_trace_with_stuttering(case_id, expected, actual, projection):
    issues = []
    current_state, initial_projection_issues = project_state(
        expected.get("initial_state"),
        projection,
        f"{case_id}: initial_state",
    )
    if initial_projection_issues:
        return initial_projection_issues

    expected_steps = expected.get("steps", [])
    actual_steps = actual.get("steps", [])
    actual_index = 0
    for expected_index, expected_step in enumerate(expected_steps):
        matched = False
        while actual_index < len(actual_steps):
            actual_step = actual_steps[actual_index]
            if same_step_signature(expected_step, actual_step):
                step_issues, current_state = compare_expected_step(
                    case_id,
                    expected_step,
                    actual_step,
                    f"expected step {expected_index} actual step {actual_index}",
                    projection,
                )
                issues.extend(step_issues)
                actual_index += 1
                matched = True
                break

            stutter_issues, actual_state = projected_actual_state(case_id, actual_step, actual_index, projection)
            if stutter_issues:
                issues.extend(stutter_issues)
                return issues
            if actual_state != current_state:
                issues.append(
                    f"{case_id}: actual step {actual_index} is not a valid stutter before expected step {expected_index}"
                )
                return issues
            actual_index += 1

        if issues:
            return issues
        if not matched:
            issues.append(f"{case_id}: missing actual step for expected step {expected_index}")
            return issues

    while actual_index < len(actual_steps):
        stutter_issues, actual_state = projected_actual_state(case_id, actual_steps[actual_index], actual_index, projection)
        if stutter_issues:
            issues.extend(stutter_issues)
            return issues
        if actual_state != current_state:
            issues.append(f"{case_id}: trailing actual step {actual_index} is not a valid stutter")
            return issues
        actual_index += 1
    return issues


def compare_trace(case_id, expected, actual):
    issues = []
    projection = expected.get("observable_projection", [])
    if expected.get("initial_state") != actual.get("initial_state"):
        issues.append(f"{case_id}: initial_state mismatch")
    exp_steps = expected.get("steps", [])
    act_steps = actual.get("steps", [])
    if expected.get("allowed_stuttering") is True:
        return issues + compare_trace_with_stuttering(case_id, expected, actual, projection)
    if len(exp_steps) != len(act_steps):
        issues.append(f"{case_id}: step count mismatch expected={len(exp_steps)} actual={len(act_steps)}")
        return issues
    for index, (exp_step, act_step) in enumerate(zip(exp_steps, act_steps)):
        step_issues, _ = compare_expected_step(case_id, exp_step, act_step, f"step {index}", projection)
        issues.extend(step_issues)
    return issues


def compare(expected, actual, allow_extra_actual=False):
    issues = []
    expected_ids = set(expected)
    actual_ids = set(actual)
    for case_id in sorted(expected_ids - actual_ids):
        issues.append(f"{case_id}: missing actual trace")
    if not allow_extra_actual:
        for case_id in sorted(actual_ids - expected_ids):
            issues.append(f"{case_id}: unexpected actual trace")
    for case_id in sorted(expected_ids & actual_ids):
        issues.extend(compare_trace(case_id, expected[case_id], actual[case_id]))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Compare model expected traces with implementation observed traces.")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--allow-extra-actual", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        expected = load_jsonl(args.expected)
        actual = load_jsonl(args.actual)
        issues = compare(expected, actual, allow_extra_actual=args.allow_extra_actual)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {"expected": args.expected, "actual": args.actual, "issues": issues}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for issue in issues:
            print(f"MISMATCH: {issue}")
        if not issues:
            print("[model-implementation-conformance] traces matched")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
