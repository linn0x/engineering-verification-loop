#!/usr/bin/env bash
set -euo pipefail

OUTPUT="${1:-}"
if [ -z "$OUTPUT" ]; then
  OUTPUT=".ci-forensics/local-diagnostics-$(date -u '+%Y%m%dT%H%M%SZ').json"
fi

mkdir -p "$(dirname "$OUTPUT")"

python3 - "$OUTPUT" <<'PY'
import json
import os
import platform
import shutil
import subprocess
import sys

output = sys.argv[1]
tools = [
    "git",
    "go",
    "python",
    "python3",
    "pytest",
    "ruff",
    "mypy",
    "pyright",
    "uv",
    "poetry",
    "pip",
    "pipx",
    "rustc",
    "cargo",
    "node",
    "npm",
    "java",
    "javac",
    "mvn",
    "gradle",
    "dafny",
    "tlc",
]


def run(cmd):
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10).stdout.strip().splitlines()[:5]
    except Exception as exc:
        return [f"ERROR: {exc}"]


def run_optional(cmd):
    if not shutil.which(cmd[0]):
        return []
    return run(cmd)


data = {
    "platform": {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    },
    "cwd": os.getcwd(),
    "env": {
        key: os.environ.get(key, "")
        for key in ["CI", "GITHUB_ACTIONS", "RUNNER_OS", "SHELL", "TLA2TOOLS_JAR"]
    },
    "tools": {},
    "git": {},
    "go": {},
    "python_packages": {},
}

for tool in tools:
    path = shutil.which(tool)
    if not path:
        continue
    if tool == "go":
        version_cmd = [tool, "version"]
    elif tool == "pytest":
        version_cmd = [tool, "--version"]
    else:
        version_cmd = [tool, "--version"]
    data["tools"][tool] = {"path": path, "version": run(version_cmd)}

if shutil.which("git"):
    data["git"]["root"] = run(["git", "rev-parse", "--show-toplevel"])
    data["git"]["sha"] = run(["git", "rev-parse", "HEAD"])
    data["git"]["status_short"] = run(["git", "status", "--short"])

if shutil.which("go"):
    data["go"]["env"] = run(["go", "env", "-json"])[:80]
    data["go"]["modules"] = run(["go", "list", "-m", "all"])[:80]

if shutil.which("python3"):
    data["python_packages"]["pip_freeze"] = run(["python3", "-m", "pip", "freeze"])[:80]
if shutil.which("uv"):
    data["python_packages"]["uv_pip_freeze"] = run(["uv", "pip", "freeze"])[:80]
if shutil.which("poetry"):
    data["python_packages"]["poetry_show_tree"] = run(["poetry", "show", "--tree"])[:80]

with open(output, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, sort_keys=True)
print(output)
PY
