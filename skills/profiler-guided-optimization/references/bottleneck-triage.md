# Bottleneck Triage

- Rank by cumulative time for call chains and self time for leaf functions.
- Check whether the hotspot is on the representative workload path.
- Separate CPU, allocation, I/O wait, lock contention, and scheduler delay.
- Do not optimize a function merely because it appears in a profile; estimate impact from its share of total time.
- Re-profile after each change to confirm the hotspot moved or shrank.
