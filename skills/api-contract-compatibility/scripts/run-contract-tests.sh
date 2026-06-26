#!/usr/bin/env bash
set -euo pipefail

if [ -z "${CONTRACT_TEST_CMD:-}" ]; then
  echo "ERROR: CONTRACT_TEST_CMD is required." >&2
  echo "Example: CONTRACT_TEST_CMD='npm run test:contracts' CONTRACT_TEST_LABEL='provider' $0" >&2
  exit 2
fi

LABEL="${CONTRACT_TEST_LABEL:-contract-test}"
case "$LABEL" in
  *[!A-Za-z0-9_.-]*|'')
    echo "ERROR: CONTRACT_TEST_LABEL must contain only letters, digits, dot, underscore, or hyphen." >&2
    exit 2
    ;;
esac

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$(pwd)"
fi

cd "$ROOT"
mkdir -p .contract-tests
TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
LOG=".contract-tests/${TIMESTAMP}-${LABEL}.log"
exec > >(tee "$LOG") 2>&1

echo "[contract-test] label: $LABEL"
echo "[contract-test] timestamp_utc: $TIMESTAMP"
echo "[contract-test] command: $CONTRACT_TEST_CMD"
echo "[contract-test] root: $ROOT"
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "[contract-test] git_sha: $(git rev-parse HEAD)"
  echo "[contract-test] git_status_short:"
  git status --short || true
fi

echo "[contract-test] begin"
set +e
bash -lc "$CONTRACT_TEST_CMD"
STATUS=$?
set -e
echo "[contract-test] exit_status: $STATUS"
echo "[contract-test] log: $ROOT/$LOG"
exit "$STATUS"
