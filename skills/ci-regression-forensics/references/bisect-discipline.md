# Bisect Discipline

Use bisect only when:

- the worktree is clean or changes are intentionally allowed;
- the test command is deterministic enough to classify commits;
- good and bad revisions are known;
- build/setup time is acceptable.

Avoid bisect when:

- dependencies are floating;
- the failure is strongly environment-dependent;
- the command has high flaky probability;
- old commits cannot build with current external services.

Record inconclusive outcomes rather than forcing a first-bad commit.
