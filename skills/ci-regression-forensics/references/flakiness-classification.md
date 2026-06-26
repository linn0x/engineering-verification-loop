# Flakiness Classification

Treat a failure as flaky suspicion, not proven flakiness, when:

- rerun succeeds without code changes;
- failure involves timeout, ordering, clock, random seed, race detector, external service, or resource pressure;
- logs differ materially across identical commits;
- the same test fails with different assertions;
- failure appears only on one runner class.

Do not dismiss failures as flaky without preserving the signature and environment. A flaky test often indicates a real race, missing isolation, hidden time dependency, or external service assumption.
