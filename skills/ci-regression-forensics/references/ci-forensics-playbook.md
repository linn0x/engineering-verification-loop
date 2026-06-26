# CI Forensics Playbook

1. Preserve raw logs and artifact links.
2. Identify exact job, command, commit SHA, runner OS, dependency cache state, and timeout/resource limits.
3. Validate any structured `ci_failure` footer. A valid footer must have known failure type, matching specialist route, non-zero exit code, stable hex signature, artifact path resolving to the classified log, and a signature matching `emit-ci-failure-footer.py`. Custom signatures must be emitted with external provenance, source, and reason metadata; they remain invalid unless the validator is run with `--allow-external-signature`.
4. Classify the failure before editing code. If the footer uses trusted external signature provenance, pass `--allow-external-signature` to the classifier; otherwise it is treated as invalid and regex fallback is used. If there is no valid footer, use fallback regex classification with confidence and ambiguity flags; low-confidence or ambiguous results require human review.
5. Extract a stable signature that can deduplicate repeated failures. Empty logs or logs with no test/frame/error components must not produce a hash.
6. Build the smallest local reproduction command.
7. Compare local and CI environments if reproduction differs.
8. Use bisect only after the failure command is stable enough.
9. Route to the specialist skill after classification.
10. Add a prevention check: regression test, contract check, benchmark threshold, formal verification, or CI environment pin.
