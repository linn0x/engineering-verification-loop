#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PROP_TEST_CMD:-}" ]; then
  echo "ERROR: PROP_TEST_CMD is required." >&2
  echo "Example: PROP_TEST_CMD='cargo test proptest' PROP_TEST_LABEL='dedupe' $0" >&2
  exit 2
fi

LABEL="${PROP_TEST_LABEL:-property-test}"
case "$LABEL" in
  *[!A-Za-z0-9_.-]*|'')
    echo "ERROR: PROP_TEST_LABEL must contain only letters, digits, dot, underscore, or hyphen." >&2
    exit 2
    ;;
esac

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$(pwd)"
fi

cd "$ROOT"
mkdir -p .property-tests

TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
LOG=".property-tests/${TIMESTAMP}-${LABEL}.log"

exec > >(tee "$LOG") 2>&1

echo "[property-test] label: $LABEL"
echo "[property-test] timestamp_utc: $TIMESTAMP"
echo "[property-test] root: $ROOT"
echo "[property-test] command: $PROP_TEST_CMD"
echo "[property-test] uname: $(uname -a)"
if git rev-parse HEAD >/dev/null 2>&1; then
  echo "[property-test] git_sha: $(git rev-parse HEAD)"
  echo "[property-test] git_status_short:"
  git status --short || true
fi

for name in HYPOTHESIS_SEED PROPTEST_SEED QUICKCHECK_TESTS QUICKCHECK_SEED FAST_CHECK_SEED; do
  if [ -n "${!name:-}" ]; then
    echo "[property-test] env_${name}: ${!name}"
  fi
done

for tool in go rustc cargo node npm pnpm yarn python3 java javac dafny tlc; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "[property-test] ${tool}_version:"
    if [ "$tool" = "go" ]; then
      go version 2>&1 | head -n 3 || true
    elif [ "$tool" = "tlc" ]; then
      tlc 2>&1 | head -n 1 || true
    else
      "$tool" --version 2>&1 | head -n 3 || true
    fi
  fi
done

echo "[property-test] begin"
set +e
bash -lc "$PROP_TEST_CMD"
STATUS=$?
set -e
echo "[property-test] exit_status: $STATUS"
echo "[property-test] log: $ROOT/$LOG"
exit "$STATUS"
