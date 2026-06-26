#!/usr/bin/env bash
set -euo pipefail

if [ -z "${GOOD_REV:-}" ] || [ -z "${BAD_REV:-}" ] || [ -z "${BISECT_TEST_CMD:-}" ]; then
  echo "ERROR: GOOD_REV, BAD_REV, and BISECT_TEST_CMD are required." >&2
  echo "Example: GOOD_REV=main~20 BAD_REV=HEAD BISECT_TEST_CMD='go test ./pkg -run TestX' $0" >&2
  exit 2
fi

if [ "${ALLOW_DIRTY:-0}" != "1" ] && [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: worktree is dirty; commit/stash changes or set ALLOW_DIRTY=1." >&2
  exit 2
fi

LOG_DIR=".ci-forensics/bisect-$(date -u '+%Y%m%dT%H%M%SZ')"
mkdir -p "$LOG_DIR"

cleanup() {
  git bisect reset >/dev/null 2>&1 || true
}
trap cleanup EXIT

cat > "$LOG_DIR/test.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
bash -lc '$BISECT_TEST_CMD'
EOF
chmod +x "$LOG_DIR/test.sh"

echo "[bisect] good: $GOOD_REV"
echo "[bisect] bad: $BAD_REV"
echo "[bisect] command: $BISECT_TEST_CMD"
echo "[bisect] log_dir: $LOG_DIR"

git bisect start "$BAD_REV" "$GOOD_REV"
set +e
git bisect run "$LOG_DIR/test.sh" 2>&1 | tee "$LOG_DIR/bisect.log"
STATUS=${PIPESTATUS[0]}
set -e

git bisect log > "$LOG_DIR/bisect-steps.log" || true
exit "$STATUS"
