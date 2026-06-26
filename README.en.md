# Engineering Verification Loop

[中文](README.md) | English

Engineering Verification Loop is a Codex skill pack for evidence-driven Go and Python engineering work. It routes high-risk changes through specialist verification gates and produces an auditable evidence bundle before readiness, performance, compatibility, or conformance claims are accepted.

This repository packages the currently installed local skill pack into a GitHub-ready distribution.

## What This Skill Pack Is For

Use this pack when a change needs defensible evidence for one or more of these risks:

- correctness-critical logic, parsers, validators, authorization, or state transitions
- handwritten Go/Python implementation alignment with Dafny or TLA models
- algorithm or data-structure selection under measurable performance constraints
- benchmark, experiment, or product performance claims
- API, schema, SDK, event, OpenAPI, JSON Schema, GraphQL, or Protobuf compatibility
- CI failure classification, reproduction, and regression forensics
- profiler-guided CPU, memory, allocation, or I/O optimization
- distributed protocol behavior under retries, partitions, crashes, clocks, quorum, or async ordering

The pack is intentionally strict: unsupported claims are documented as limitations instead of being treated as passed gates.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `engineering-verification-loop` | Top-level orchestration, risk routing, evidence bundle audit |
| `dafny-verification` | Dafny 4+ proof workflow for local correctness properties |
| `property-based-differential-testing` | Property, differential, metamorphic, and generated-input testing |
| `algorithm-selection-benchmarking` | Algorithm/data-structure selection and benchmark evidence |
| `api-contract-compatibility` | OpenAPI, JSON fixture, Protobuf, and contract compatibility checks |
| `ci-regression-forensics` | CI failure classification, signature extraction, diagnostics, bisect support |
| `reproducible-experiment-analysis` | Experiment manifests, repeated metrics, uncertainty, reproducibility audit |
| `profiler-guided-optimization` | Profiling workflow and before/after optimization metrics |
| `model-implementation-conformance` | Map Dafny/TLA model properties to Go/Python implementation evidence |
| `tla-distributed-model-checking` | TLC and optional Apalache model checking for distributed protocols |

## Repository Layout

```text
.
├── skills/                    # Codex skill directories copied into CODEX_HOME/skills
├── scripts/
│   ├── install.sh             # Install or update skills locally
│   └── validate.sh            # Validate repository package structure and scripts
├── docs/
│   ├── INSTALL.md             # Detailed installation guide
│   ├── DEPENDENCIES.md        # Gate-specific tool dependencies
│   └── RELEASE_CHECKLIST.md   # Maintainer release checklist
├── .github/workflows/         # GitHub Actions validation workflow
├── VERSION
├── README.md                  # Default Chinese README
└── README.en.md               # English README
```

## Quick Install

From a clone of this repository:

```bash
./scripts/install.sh
```

By default, the installer copies every skill into:

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

Install into a custom Codex home:

```bash
./scripts/install.sh --dest "$HOME/.codex/skills"
```

Preview without writing:

```bash
./scripts/install.sh --dry-run
```

See [docs/INSTALL.md](docs/INSTALL.md) for full installation and dependency setup.

## Validate the Package

Run:

```bash
./scripts/validate.sh
```

Validation checks:

- every packaged skill has a valid `SKILL.md` frontmatter
- Python scripts compile
- shell scripts parse with `bash -n`
- JSON templates parse
- executable scripts have executable permissions

This does not prove every specialist gate can run on a target project. Gate-specific tools are listed in [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md).

## Basic Usage

After installation, ask Codex to use the top-level skill on a concrete engineering change:

```text
Use $engineering-verification-loop to verify this Go/Python change.
```

The orchestrator will:

1. classify active risks
2. route each risk to a specialist skill
3. require the relevant command evidence
4. assemble an evidence bundle
5. run `skills/engineering-verification-loop/scripts/audit-evidence-bundle.py`
6. report passed gates, failed gates, unsupported claims, and the next blocked gate

## Evidence Bundle

The core release artifact is the evidence bundle format under:

```text
skills/engineering-verification-loop/assets/templates/evidence-bundle.json
```

Use it to record:

- changed targets and implementation languages
- active risks
- formal coverage maps
- workloads and claim scopes
- artifacts with `sha256`, producer command, and exit code
- specialist evidence by risk
- structured unsupported claims

Audit it with:

```bash
skills/engineering-verification-loop/scripts/audit-evidence-bundle.py path/to/evidence-bundle.json --repo-root .
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
