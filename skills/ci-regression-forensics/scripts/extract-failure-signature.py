#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path


TEST_PATTERNS = [
    re.compile(r"--- FAIL:\s+([A-Za-z0-9_./:-]+)"),
    re.compile(r"FAILED\s+([A-Za-z0-9_./:-]+)"),
    re.compile(r"FAIL:\s+([A-Za-z0-9_./:-]+)"),
    re.compile(r"it\(['\"](.+?)['\"]"),
]

FRAME_PATTERNS = [
    re.compile(r"([A-Za-z0-9_./-]+\.(?:go|py|ts|tsx|js|jsx|java|rs|cpp|cc|c|h)):(\d+)"),
    re.compile(r"at\s+.+\(([^()]+\.(?:ts|tsx|js|jsx)):(\d+):(\d+)\)"),
]

ERROR_PATTERNS = [
    re.compile(r"(AssertionError.*)"),
    re.compile(r"(panic:.*)"),
    re.compile(r"(Error:.*)"),
    re.compile(r"(expected .*)", re.I),
    re.compile(r"(cannot .*|failed .*)", re.I),
]

FRAME_EXCLUDES = (
    "/runtime/",
    "/site-packages/",
    "/dist-packages/",
    "node_modules/",
    "/pkg/mod/",
    "testing.tRunner",
)


def normalize_error(text):
    text = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", text)
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}[T ][0-9:.Z+-]+", "TIMESTAMP", text)
    text = re.sub(r"\b\d+\.\d+\b", "N", text)
    text = re.sub(r"\b\d+\b", "N", text)
    return " ".join(text.split())[:500]


def first_match(patterns, lines):
    for line in lines:
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                return match.groups()[0]
    return ""


def extract_frames(lines):
    frames = []
    for line in lines:
        for pattern in FRAME_PATTERNS:
            match = pattern.search(line)
            if match:
                groups = match.groups()
                frames.append(":".join(groups[:2]))
                break
    return frames


def choose_frame(frames, repo_root, prefer_user_frame):
    if not frames:
        return ""
    if not prefer_user_frame:
        return frames[0]
    root = str(Path(repo_root).resolve()) if repo_root else ""
    for frame in frames:
        if any(exclude in frame for exclude in FRAME_EXCLUDES):
            continue
        if root and str(Path(frame.split(":")[0])).startswith(root):
            return frame
        if not Path(frame.split(":")[0]).is_absolute():
            return frame
    return frames[0]


def main():
    parser = argparse.ArgumentParser(description="Extract stable CI failure signatures.")
    parser.add_argument("log")
    parser.add_argument("--repo-root")
    parser.add_argument("--prefer-user-frame", action="store_true")
    parser.add_argument("--job-name", default="")
    parser.add_argument("--command", default="")
    parser.add_argument("--category", default="")
    args = parser.parse_args()

    path = Path(args.log)
    lines = path.read_text(errors="replace").splitlines()
    test = first_match(TEST_PATTERNS, lines)
    top_frame = choose_frame(extract_frames(lines), args.repo_root, args.prefer_user_frame)

    error = ""
    for line in lines:
        for pattern in ERROR_PATTERNS:
            match = pattern.search(line)
            if match:
                error = normalize_error(match.group(1))
                break
        if error:
            break

    result = {
        "log": str(path),
        "category": args.category,
        "job_name": args.job_name,
        "command": args.command,
        "test": test,
        "top_frame": top_frame,
        "normalized_error": error,
        "confidence": "high",
        "issues": [],
    }
    if not any([test, top_frame, error]):
        result["confidence"] = "none"
        result["signature_hash"] = ""
        result["issues"] = ["no stable signature components found"]
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    raw = "|".join([args.category, args.job_name, args.command, test, top_frame, error])
    result["signature_hash"] = hashlib.sha256(raw.encode()).hexdigest()[:16]
    if not test or not top_frame or not error:
        result["confidence"] = "medium"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
