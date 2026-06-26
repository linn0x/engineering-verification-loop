#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-}"
if [ -z "$OUT" ]; then
  mkdir -p .experiments
  OUT=".experiments/context-$(date -u '+%Y%m%dT%H%M%SZ').json"
fi

mkdir -p "$(dirname "$OUT")"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().rstrip("\n")))'
}

command_json() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    local path version
    path="$(command -v "$cmd")"
    version="$("$cmd" --version 2>&1 | head -n 1 || true)"
    printf '{"path":%s,"version":%s}' "$(printf '%s' "$path" | json_escape)" "$(printf '%s' "$version" | json_escape)"
  else
    printf 'null'
  fi
}

file_sha256() {
  local file="$1"
  if [ -f "$file" ]; then
    shasum -a 256 "$file" | awk '{print $1}'
  fi
}

lockfiles_json() {
  local first=1
  printf '['
  for file in package-lock.json pnpm-lock.yaml yarn.lock poetry.lock requirements.txt Pipfile.lock go.sum Cargo.lock pom.xml build.gradle gradle.lockfile; do
    if [ -f "$file" ]; then
      if [ "$first" -eq 0 ]; then printf ','; fi
      first=0
      printf '{"path":%s,"sha256":%s}' "$(printf '%s' "$file" | json_escape)" "$(file_sha256 "$file" | json_escape)"
    fi
  done
  printf ']'
}

git_json() {
  if git rev-parse --show-toplevel >/dev/null 2>&1; then
    local root sha branch status diff_hash
    root="$(git rev-parse --show-toplevel)"
    sha="$(git rev-parse HEAD 2>/dev/null || true)"
    branch="$(git branch --show-current 2>/dev/null || true)"
    status="$(git status --short 2>/dev/null || true)"
    diff_hash="$(git diff --binary | shasum -a 256 | awk '{print $1}')"
    printf '{"root":%s,"sha":%s,"branch":%s,"status_short":%s,"diff_sha256":%s}' \
      "$(printf '%s' "$root" | json_escape)" \
      "$(printf '%s' "$sha" | json_escape)" \
      "$(printf '%s' "$branch" | json_escape)" \
      "$(printf '%s' "$status" | json_escape)" \
      "$(printf '%s' "$diff_hash" | json_escape)"
  else
    printf 'null'
  fi
}

{
  printf '{\n'
  printf '  "timestamp_utc": %s,\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ' | json_escape)"
  printf '  "cwd": %s,\n' "$(pwd | json_escape)"
  printf '  "system": {\n'
  printf '    "uname": %s,\n' "$(uname -a | json_escape)"
  printf '    "hostname": %s\n' "$(hostname | json_escape)"
  printf '  },\n'
  printf '  "git": %s,\n' "$(git_json)"
  printf '  "tools": {\n'
  printf '    "python3": %s,\n' "$(command_json python3)"
  printf '    "node": %s,\n' "$(command_json node)"
  printf '    "npm": %s,\n' "$(command_json npm)"
  printf '    "go": %s,\n' "$(command_json go)"
  printf '    "rustc": %s,\n' "$(command_json rustc)"
  printf '    "java": %s\n' "$(command_json java)"
  printf '  },\n'
  printf '  "lockfiles": %s\n' "$(lockfiles_json)"
  printf '}\n'
} > "$OUT"

python3 -m json.tool "$OUT" >/dev/null
echo "$OUT"
