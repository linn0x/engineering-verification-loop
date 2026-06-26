#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  set -- formal
fi

if ! command -v dafny >/dev/null 2>&1; then
  echo "ERROR: dafny is not installed or not in PATH" >&2
  echo "Install Dafny, then rerun verification." >&2
  exit 127
fi

if ! dafny verify --help >/dev/null 2>&1 || ! dafny audit --help >/dev/null 2>&1; then
  echo "ERROR: this skill requires Dafny 4+ with 'verify' and 'audit' subcommands." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/scan-forbidden.sh" "$@"

collect_files() {
  local input
  for input in "$@"; do
    case "$input" in
      -*)
        echo "ERROR: refusing path that begins with '-': $input" >&2
        return 1
        ;;
    esac
    if [ -d "$input" ]; then
      find "$input" -type f -name '*.dfy' -print
    elif [ -f "$input" ] && [[ "$input" == *.dfy ]]; then
      printf '%s\n' "$input"
    elif [ -e "$input" ]; then
      echo "ERROR: unsupported Dafny verification input: $input" >&2
      echo "Pass .dfy files or directories containing .dfy files." >&2
      return 1
    else
      if [ "$input" = "formal" ]; then
        echo "ERROR: no path supplied and formal/ does not exist; create formal/ or pass .dfy files/directories." >&2
      else
        echo "ERROR: path does not exist: $input" >&2
      fi
      return 1
    fi
  done
}

TMP_FILES="$(mktemp "${TMPDIR:-/tmp}/dafny-verify-files.XXXXXX")"
AUDIT_OUTPUT="$(mktemp "${TMPDIR:-/tmp}/dafny-audit-output.XXXXXX")"
trap 'rm -f "$TMP_FILES" "$AUDIT_OUTPUT"' EXIT

collect_files "$@" > "$TMP_FILES"
LC_ALL=C sort -u "$TMP_FILES" -o "$TMP_FILES"

FILES=()
while IFS= read -r file; do
  FILES+=("$file")
done < "$TMP_FILES"

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "ERROR: no .dfy files found in: $*" >&2
  exit 1
fi

echo "[dafny-verify] Dafny version: $(dafny --version)"
echo "[dafny-verify] verifying ${#FILES[@]} Dafny file(s)"

dafny verify --verify-included-files --analyze-proofs "${FILES[@]}"

echo "[dafny-verify] auditing unproven assumptions"
if ! dafny audit "${FILES[@]}" > "$AUDIT_OUTPUT" 2>&1; then
  cat "$AUDIT_OUTPUT" >&2
  echo "ERROR: dafny audit failed." >&2
  exit 1
fi

if grep -q 'Dafny auditor completed with 0 findings' "$AUDIT_OUTPUT"; then
  :
else
  cat "$AUDIT_OUTPUT" >&2
  echo "ERROR: dafny audit reported unproven assumptions or soundness-limiting constructs." >&2
  exit 1
fi

echo "[dafny-verify] verification passed"
