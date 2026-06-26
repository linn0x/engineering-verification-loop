#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required" >&2
  exit 127
fi

python3 - "$ROOT" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
skills_dir = root / "skills"
name_re = re.compile(r"^[a-z0-9-]+$")
errors = []

if not skills_dir.is_dir():
    errors.append("missing skills/ directory")
else:
    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("skills/ contains no skill directories")
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{skill_dir.relative_to(root)}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{skill_md.relative_to(root)}: missing YAML frontmatter")
            continue
        try:
            frontmatter = text.split("---\n", 2)[1]
        except IndexError:
            errors.append(f"{skill_md.relative_to(root)}: invalid YAML frontmatter fence")
            continue
        fields = {}
        for line in frontmatter.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
        name = fields.get("name", "")
        description = fields.get("description", "")
        if not name:
            errors.append(f"{skill_md.relative_to(root)}: missing name")
        elif not name_re.match(name) or name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"{skill_md.relative_to(root)}: invalid name {name!r}")
        if skill_dir.name != name:
            errors.append(f"{skill_md.relative_to(root)}: folder name {skill_dir.name!r} does not match name {name!r}")
        if not description:
            errors.append(f"{skill_md.relative_to(root)}: missing description")
        elif len(description) > 1024:
            errors.append(f"{skill_md.relative_to(root)}: description exceeds 1024 characters")

for json_file in sorted(root.rglob("*.json")):
    if ".git" in json_file.parts:
        continue
    try:
        json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{json_file.relative_to(root)}: invalid JSON: {exc}")

for script in sorted(root.rglob("*")):
    if not script.is_file() or ".git" in script.parts:
        continue
    if script.suffix in {".py", ".sh"}:
        first = script.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        if first and first[0].startswith("#!") and not (script.stat().st_mode & 0o111):
            errors.append(f"{script.relative_to(root)}: shebang script is not executable")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)

print("[validate] skill metadata and JSON files ok")
PY

while IFS= read -r -d '' file; do
  python3 -m py_compile "$file"
done < <(find skills scripts -type f -name '*.py' -print0)
echo "[validate] Python scripts compile"

while IFS= read -r -d '' file; do
  bash -n "$file"
done < <(find skills scripts -type f -name '*.sh' -print0)
echo "[validate] shell scripts parse"

echo "[validate] package validation passed"
