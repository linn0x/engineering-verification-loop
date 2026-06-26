# Installation Guide

This guide installs the Engineering Verification Loop skill pack into a local Codex environment.

## Prerequisites

Minimum tools:

- macOS, Linux, or another Unix-like shell environment
- Bash
- Python 3.10 or newer
- Git
- Codex configured to load skills from `${CODEX_HOME:-$HOME/.codex}/skills`

Recommended tools depend on which verification gates you plan to use. See [DEPENDENCIES.md](DEPENDENCIES.md).

## Install the Skills

Clone the repository:

```bash
git clone https://github.com/<owner>/engineering-verification-loop.git
cd engineering-verification-loop
```

Install all skills:

```bash
./scripts/install.sh
```

Install into a specific destination:

```bash
./scripts/install.sh --dest "$HOME/.codex/skills"
```

Preview the install without modifying files:

```bash
./scripts/install.sh --dry-run
```

Install only the top-level orchestrator:

```bash
./scripts/install.sh --core-only
```

Core-only installation is useful only when the specialist skills are already installed separately. For a complete release install, use the default all-skill installation.

## What the Installer Does

The installer:

1. resolves the repository root
2. creates the destination skill directory if needed
3. backs up any existing skill directory it will replace
4. copies packaged skills from `skills/` to the Codex skills directory
5. preserves executable permissions on bundled scripts
6. prints the installed skill names

Backups are created under:

```text
<dest>/.backup-engineering-verification-loop-<timestamp>
```

## Validate After Install

Validate the repository package:

```bash
./scripts/validate.sh
```

Validate a specific installed skill with the Codex system validator if available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/engineering-verification-loop
```

Run the evidence bundle auditor help:

```bash
~/.codex/skills/engineering-verification-loop/scripts/audit-evidence-bundle.py --help
```

Run the target inference helper help:

```bash
~/.codex/skills/engineering-verification-loop/scripts/infer-go-python-targets.py --help
```

## Optional Dependency Setup on macOS

Install common gate tools:

```bash
brew install dafny buf
python3 -m pip install --user PyYAML pytest hypothesis pytest-benchmark py-spy scalene
```

Install TLC using `tla2tools.jar`:

```bash
mkdir -p /opt/homebrew/share/tla2tools
curl -L -o /opt/homebrew/share/tla2tools/tla2tools.jar \
  https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar
cat >/opt/homebrew/bin/tlc <<'EOF'
#!/usr/bin/env bash
exec java -cp /opt/homebrew/share/tla2tools/tla2tools.jar tlc2.TLC "$@"
EOF
chmod +x /opt/homebrew/bin/tlc
```

Install Apalache when you want `APALACHE=1` checks:

```bash
curl -L -o /tmp/apalache.tgz \
  https://github.com/apalache-mc/apalache/releases/latest/download/apalache.tgz
mkdir -p /opt/homebrew/share/apalache
tar -xzf /tmp/apalache.tgz -C /opt/homebrew/share/apalache
ln -sf /opt/homebrew/share/apalache/apalache-*/bin/apalache-mc /opt/homebrew/bin/apalache-mc
```

Adjust `/opt/homebrew` to `/usr/local` or another prefix if needed.

## Updating

From a new checkout or pulled update:

```bash
git pull
./scripts/validate.sh
./scripts/install.sh
```

Existing installed skill directories are backed up before replacement.

## Uninstall

Remove installed skill directories:

```bash
rm -rf \
  ~/.codex/skills/engineering-verification-loop \
  ~/.codex/skills/dafny-verification \
  ~/.codex/skills/property-based-differential-testing \
  ~/.codex/skills/algorithm-selection-benchmarking \
  ~/.codex/skills/api-contract-compatibility \
  ~/.codex/skills/ci-regression-forensics \
  ~/.codex/skills/reproducible-experiment-analysis \
  ~/.codex/skills/profiler-guided-optimization \
  ~/.codex/skills/model-implementation-conformance \
  ~/.codex/skills/tla-distributed-model-checking
```

If `CODEX_HOME` is set, replace `~/.codex` with `$CODEX_HOME`.
