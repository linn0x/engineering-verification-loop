#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: BENCH_CMD='<benchmark command>' $0 <label>" >&2
  echo "Example: BENCH_CMD='go test ./... -run ^$ -bench=. -benchmem' $0 baseline" >&2
}

if [ "$#" -ne 1 ]; then
  usage
  exit 2
fi

LABEL="$1"
case "$LABEL" in
  *[!A-Za-z0-9_.-]*|'')
    echo "ERROR: label must contain only letters, digits, dot, underscore, or hyphen." >&2
    exit 2
    ;;
esac

if [ -z "${BENCH_CMD:-}" ]; then
  echo "ERROR: BENCH_CMD is required." >&2
  usage
  exit 2
fi

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$(pwd)"
fi

cd "$ROOT"
mkdir -p .benchmarks

TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
LOG=".benchmarks/${TIMESTAMP}-${LABEL}.log"

exec > >(tee "$LOG") 2>&1

echo "[benchmark] label: $LABEL"
echo "[benchmark] timestamp_utc: $TIMESTAMP"
echo "[benchmark] root: $ROOT"
echo "[benchmark] command: $BENCH_CMD"
echo "[benchmark] uname: $(uname -a)"
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "[benchmark] git_sha: $(git rev-parse HEAD)"
  echo "[benchmark] git_status_short:"
  git status --short || true
fi

for tool in go rustc cargo node npm python3 java javac dafny; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "[benchmark] ${tool}_version:"
    if [ "$tool" = "go" ]; then
      go version 2>&1 | head -n 3 || true
    else
      "$tool" --version 2>&1 | head -n 3 || true
    fi
  fi
done

echo "[benchmark] begin"
set +e
bash -lc "$BENCH_CMD"
STATUS=$?
set -e
echo "[benchmark] exit_status: $STATUS"
echo "[benchmark] log: $ROOT/$LOG"
exit "$STATUS"
