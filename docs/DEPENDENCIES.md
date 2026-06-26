# Dependency Reference

The skill pack itself is mostly shell, Python standard library, JSON, and Markdown. Specialist gates need additional tools only when those gates are active.

## Base Package

Required:

- Bash
- Python 3.10+
- Git

Recommended:

- PyYAML, for YAML OpenAPI files and Codex system skill validation

```bash
python3 -m pip install --user PyYAML
```

## Gate-Specific Tools

| Gate | Skill | Tools |
| --- | --- | --- |
| Evidence bundle audit | `engineering-verification-loop` | Python 3 |
| Dafny proof | `dafny-verification` | Dafny 4+ with `verify` and `audit` |
| TLA model checking | `tla-distributed-model-checking` | Java, TLC command or `TLA2TOOLS_JAR` |
| Optional symbolic TLA check | `tla-distributed-model-checking` | `apalache-mc` and `APALACHE=1` |
| Protobuf compatibility | `api-contract-compatibility` | `buf` |
| OpenAPI YAML compatibility | `api-contract-compatibility` | PyYAML |
| Go implementation evidence | multiple skills | Go toolchain |
| Python implementation evidence | multiple skills | `pytest`, optionally `hypothesis`, `pytest-benchmark` |
| Python profiling | `profiler-guided-optimization` | `cProfile` built in, optionally `py-spy`, `scalene` |
| CI forensics | `ci-regression-forensics` | Git, project-native CI/test commands |

## macOS One-Time Setup Example

```bash
brew install dafny buf
python3 -m pip install --user PyYAML pytest hypothesis pytest-benchmark py-spy scalene
```

TLC and Apalache are not required for non-distributed work. Install them only when using TLA checks.

## Verification Commands

Check key tools:

```bash
python3 --version
git --version
dafny --version
buf --version
tlc 2>&1 | head -n 1
apalache-mc version
pytest --version
py-spy --version
scalene --version
```

Tool availability does not imply a project gate has passed. Each gate must run the exact project command and preserve artifacts in the evidence bundle.
