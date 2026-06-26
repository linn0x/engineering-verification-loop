#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <file.tla|directory> [more files/directories]" >&2
}

if [ "$#" -eq 0 ]; then
  usage
  exit 2
fi

collect_specs() {
  local input
  for input in "$@"; do
    case "$input" in
      -*)
        echo "ERROR: refusing path that begins with '-': $input" >&2
        return 1
        ;;
    esac
    if [ -d "$input" ]; then
      find "$input" -type f -name '*.tla' -print
    elif [ -f "$input" ] && [[ "$input" == *.tla ]]; then
      printf '%s\n' "$input"
    elif [ -e "$input" ]; then
      echo "ERROR: unsupported input: $input" >&2
      echo "Pass .tla files or directories containing .tla files." >&2
      return 1
    else
      echo "ERROR: path does not exist: $input" >&2
      return 1
    fi
  done
}

if command -v tlc >/dev/null 2>&1; then
  TLC_MODE="command"
elif [ -n "${TLA2TOOLS_JAR:-}" ] && [ -f "$TLA2TOOLS_JAR" ]; then
  TLC_MODE="jar"
else
  echo "ERROR: TLA+ TLC is not available." >&2
  echo "Install a 'tlc' command or set TLA2TOOLS_JAR to a local tla2tools.jar." >&2
  exit 127
fi

TMP_SPECS="$(mktemp "${TMPDIR:-/tmp}/tla-specs.XXXXXX")"
trap 'rm -f "$TMP_SPECS"' EXIT

collect_specs "$@" > "$TMP_SPECS"
LC_ALL=C sort -u "$TMP_SPECS" -o "$TMP_SPECS"

if [ ! -s "$TMP_SPECS" ]; then
  echo "ERROR: no .tla files found." >&2
  exit 1
fi

LOGS=()

while IFS= read -r SPEC; do
  DIR="$(cd "$(dirname "$SPEC")" && pwd)"
  BASE="$(basename "$SPEC" .tla)"
  CFG="$DIR/$BASE.cfg"
  if [ ! -f "$CFG" ]; then
    echo "ERROR: missing matching config for $SPEC: $CFG" >&2
    exit 1
  fi

  OUT_DIR="${TLA_OUT_DIR:-$DIR/out}"
  mkdir -p "$OUT_DIR"
  LOG="$OUT_DIR/${BASE}-tlc.log"

  echo "[tla-check] spec: $SPEC"
  echo "[tla-check] config: $CFG"
  echo "[tla-check] log: $LOG"
  LOGS+=("$LOG")

  if [ "$TLC_MODE" = "jar" ]; then
    set +e
    java -cp "$TLA2TOOLS_JAR" tla2sany.SANY "$SPEC" > "$OUT_DIR/${BASE}-sany.log" 2>&1
    SANY_STATUS=$?
    set -e
    if [ "$SANY_STATUS" -ne 0 ]; then
      cat "$OUT_DIR/${BASE}-sany.log" >&2
      echo "ERROR: SANY parser failed for $SPEC" >&2
      exit "$SANY_STATUS"
    fi
    set +e
    (
      cd "$DIR"
      java -cp "$TLA2TOOLS_JAR" tlc2.TLC -config "$BASE" "$BASE"
    ) > "$LOG" 2>&1
    TLC_STATUS=$?
    set -e
  else
    set +e
    (
      cd "$DIR"
      tlc -config "$BASE" "$BASE"
    ) > "$LOG" 2>&1
    TLC_STATUS=$?
    set -e
  fi

  if [ "$TLC_STATUS" -ne 0 ]; then
    cat "$LOG" >&2
    echo "ERROR: TLC exited with status $TLC_STATUS for $SPEC" >&2
    exit "$TLC_STATUS"
  fi

  if grep -E 'Error:|Invariant .* is violated|Temporal properties were violated|Deadlock reached' "$LOG" >/dev/null 2>&1; then
    cat "$LOG" >&2
    echo "ERROR: TLC reported a model-checking failure for $SPEC" >&2
    exit 1
  fi

  if [ "${APALACHE:-0}" = "1" ]; then
    if command -v apalache-mc >/dev/null 2>&1; then
      apalache-mc check "$SPEC" > "$OUT_DIR/${BASE}-apalache.log" 2>&1
    else
      echo "ERROR: APALACHE=1 but apalache-mc is not installed." >&2
      exit 127
    fi
  fi
done < "$TMP_SPECS"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$SCRIPT_DIR/summarize-tlc.py" ] && [ "${#LOGS[@]}" -gt 0 ]; then
  "$SCRIPT_DIR/summarize-tlc.py" "${LOGS[@]}" || true
fi

echo "[tla-check] all checks passed"
