#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  set -- formal
fi

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
      :
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

TMP_FILES="$(mktemp "${TMPDIR:-/tmp}/dafny-scan-files.XXXXXX")"
trap 'rm -f "$TMP_FILES"' EXIT

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

echo "[dafny-scan] scanning ${#FILES[@]} Dafny file(s)"

if LC_ALL=C grep -n -- $'\xC2\xA0' "${FILES[@]}"; then
  echo
  echo "ERROR: non-breaking spaces found in Dafny source; replace them with ASCII spaces." >&2
  exit 1
fi

FORBIDDEN_PATTERN='(^|[^[:alnum:]_])(assume|expect)([^[:alnum:]_]|$)|\{:[[:space:]]*verify[[:space:]]+false[[:space:]]*\}|\{:[[:space:]]*(axiom|extern|only)([^[:alnum:]_]|[[:space:]]|\})|decreases[[:space:]]+\*|ensures[[:space:]]+true([^[:alnum:]_]|$)|--no-verify|--allow-axioms|/allowAxioms|-allowAxioms|allowAxioms|allow-axioms|/dafnyVerify:0|-dafnyVerify:0|dafnyVerify[[:space:]]*=[[:space:]]*false'

set +e
grep -nE -- "$FORBIDDEN_PATTERN" "${FILES[@]}"
GREP_STATUS=$?
set -e

if [ "$GREP_STATUS" -eq 0 ]; then
  echo
  echo "ERROR: forbidden Dafny proof bypass or vacuous specification found." >&2
  echo "Forbidden: assume, expect, {:verify false}, {:axiom}, {:extern}, {:only}, decreases *, ensures true, no-verify, allow-axioms" >&2
  exit 1
elif [ "$GREP_STATUS" -ne 1 ]; then
  echo "ERROR: grep failed while scanning Dafny files." >&2
  exit "$GREP_STATUS"
fi

echo "[dafny-scan] ok"
