#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PROFILE_CMD:-}" ]; then
  echo "ERROR: PROFILE_CMD is required." >&2
  echo "Example: PROFILE_CMD='python -m cProfile -o .profiles/app.prof script.py' PROFILE_LABEL=baseline $0" >&2
  exit 2
fi

LABEL="${PROFILE_LABEL:-profile}"
case "$LABEL" in
  *[!A-Za-z0-9_.-]*|'')
    echo "ERROR: PROFILE_LABEL must contain only letters, digits, dot, underscore, or hyphen." >&2
    exit 2
    ;;
esac

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$(pwd)"
fi

cd "$ROOT"
mkdir -p .profiles
TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
LOG=".profiles/${TIMESTAMP}-${LABEL}.log"
exec > >(tee "$LOG") 2>&1

echo "[profile] label: $LABEL"
echo "[profile] timestamp_utc: $TIMESTAMP"
echo "[profile] root: $ROOT"
echo "[profile] command: $PROFILE_CMD"
echo "[profile] uname: $(uname -a)"
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "[profile] git_sha: $(git rev-parse HEAD)"
  echo "[profile] git_status_short:"
  git status --short || true
fi

echo "[profile] begin"
set +e
bash -lc "$PROFILE_CMD"
STATUS=$?
set -e
echo "[profile] exit_status: $STATUS"
echo "[profile] log: $ROOT/$LOG"
exit "$STATUS"
