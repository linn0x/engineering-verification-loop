#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/skills"
DEST="${CODEX_HOME:-$HOME/.codex}/skills"
DRY_RUN=0
CORE_ONLY=0

SKILLS=(
  engineering-verification-loop
  dafny-verification
  property-based-differential-testing
  algorithm-selection-benchmarking
  api-contract-compatibility
  ci-regression-forensics
  reproducible-experiment-analysis
  profiler-guided-optimization
  model-implementation-conformance
  tla-distributed-model-checking
)

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [options]

Options:
  --dest PATH     Install into PATH instead of ${CODEX_HOME:-$HOME/.codex}/skills
  --core-only     Install only engineering-verification-loop
  --dry-run       Print actions without writing files
  -h, --help      Show this help
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dest)
      if [ "$#" -lt 2 ]; then
        echo "ERROR: --dest requires a path" >&2
        exit 2
      fi
      DEST="$2"
      shift 2
      ;;
    --core-only)
      CORE_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$SOURCE" ]; then
  echo "ERROR: source skills directory not found: $SOURCE" >&2
  exit 1
fi

if [ "$CORE_ONLY" -eq 1 ]; then
  SKILLS=(engineering-verification-loop)
fi

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[dry-run] %q' "$1"
    shift
    for arg in "$@"; do
      printf ' %q' "$arg"
    done
    printf '\n'
  else
    "$@"
  fi
}

TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
BACKUP="$DEST/.backup-engineering-verification-loop-$TIMESTAMP"

echo "[install] source: $SOURCE"
echo "[install] destination: $DEST"

if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$DEST"
fi

for skill in "${SKILLS[@]}"; do
  src="$SOURCE/$skill"
  dst="$DEST/$skill"
  if [ ! -d "$src" ]; then
    echo "ERROR: packaged skill missing: $src" >&2
    exit 1
  fi
  if [ -e "$dst" ]; then
    echo "[install] backing up existing $skill"
    run mkdir -p "$BACKUP"
    run cp -Rp "$dst" "$BACKUP/$skill"
    run rm -rf "$dst"
  fi
  echo "[install] installing $skill"
  run cp -Rp "$src" "$dst"
done

echo "[install] installed ${#SKILLS[@]} skill(s)"
if [ -d "$BACKUP" ]; then
  echo "[install] backup: $BACKUP"
fi
echo "[install] validate with: $DEST/engineering-verification-loop/scripts/audit-evidence-bundle.py --help"
