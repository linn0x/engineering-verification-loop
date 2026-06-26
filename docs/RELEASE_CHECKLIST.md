# Release Checklist

Use this checklist before publishing a GitHub release.

## Package Checks

1. Update `VERSION`.
2. Run package validation:

   ```bash
   ./scripts/validate.sh
   ```

3. Confirm all intended skills are included under `skills/`.
4. Confirm no generated outputs are present:

   ```bash
   find skills -type d \( -name __pycache__ -o -name out \) -print
   ```

5. Confirm executable scripts are executable:

   ```bash
   find skills scripts -type f \( -name '*.sh' -o -name '*.py' \) ! -perm -111 -print
   ```

## Git Checks

```bash
git status --short
git diff --check
```

## Tagging

```bash
git tag "v$(cat VERSION)"
git push origin main
git push origin "v$(cat VERSION)"
```

## GitHub Release Notes

Include:

- version
- included skills
- installation command
- validation command
- required and optional dependency changes
- known limitations
