---- MODULE quorum_register ----
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes, QuorumSize

VARIABLES votes, committed

TypeOK ==
  /\ votes \subseteq Nodes
  /\ committed \in BOOLEAN

Init ==
  /\ votes = {}
  /\ committed = FALSE

Vote(n) ==
  /\ n \in Nodes
  /\ votes' = votes \cup {n}
  /\ committed' = committed

Commit ==
  /\ Cardinality(votes) >= QuorumSize
  /\ committed' = TRUE
  /\ votes' = votes

Next ==
  Commit \/ \E n \in Nodes: Vote(n)

CommittedHasQuorum ==
  committed => Cardinality(votes) >= QuorumSize

Spec ==
  Init /\ [][Next]_<<votes, committed>>

====
