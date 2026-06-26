# Distributed Failure Model Matrix

| Fault | Model shape | Common mistake |
|---|---|---|
| Reordering | Network as unordered set/bag or nondeterministic receive from sequence | Assuming FIFO without a production guarantee |
| Duplication | Receive is idempotent or network can retain equivalent messages | Forgetting idempotency |
| Loss | Drop action removes arbitrary deliverable message | Accidentally proving reliable-network behavior only |
| Partition | `CanDeliver(sender, receiver)` relation changes nondeterministically | Modeling only permanent partition or only healthy network |
| Heal | Partition relation can restore connectivity | Forgetting convergence after repair |
| Crash-stop | Crashed node stops local/send actions | Allowing crashed nodes to send |
| Crash-recovery | Persistent and volatile state are separate | Restoring volatile state magically |
| Clock skew | Clocks are nondeterministic within explicit bound | Treating wall-clock timeout as logical truth |
| Retry | Retry action resends or re-enqueues messages | Not modeling duplicate side effects |
| Byzantine | Arbitrary malicious behavior | Accidentally including Byzantine behavior without designing for it |
