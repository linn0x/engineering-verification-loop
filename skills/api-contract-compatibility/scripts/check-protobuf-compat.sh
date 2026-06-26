#!/usr/bin/env bash
set -euo pipefail

if ! command -v buf >/dev/null 2>&1; then
  echo "ERROR: buf is required for protobuf compatibility checks." >&2
  echo "Install buf or use the project's official protobuf breaking-change command." >&2
  exit 127
fi

if [ ! -f buf.yaml ] && [ ! -f buf.work.yaml ]; then
  echo "ERROR: no buf.yaml or buf.work.yaml found in current directory." >&2
  exit 2
fi

if [ -z "${BUF_AGAINST:-}" ]; then
  echo "ERROR: BUF_AGAINST is required, for example BUF_AGAINST='.git#branch=main'." >&2
  exit 2
fi

echo "[protobuf-compat] running: buf breaking --against $BUF_AGAINST"
buf breaking --against "$BUF_AGAINST"
