---- MODULE async_message_dedup ----
EXTENDS FiniteSets

CONSTANTS Messages

VARIABLES network, delivered

TypeOK ==
  /\ network \subseteq Messages
  /\ delivered \subseteq Messages

Init ==
  /\ network = Messages
  /\ delivered = {}

Deliver(m) ==
  /\ m \in network
  /\ delivered' = delivered \cup {m}
  /\ network' = network

Drop(m) ==
  /\ m \in network
  /\ network' = network \ {m}
  /\ delivered' = delivered

Duplicate(m) ==
  /\ m \in network
  /\ network' = network \cup {m}
  /\ delivered' = delivered

Next ==
  \E m \in Messages:
    Deliver(m) \/ Drop(m) \/ Duplicate(m)

NoUnknownDelivery ==
  delivered \subseteq Messages

Spec ==
  Init /\ [][Next]_<<network, delivered>>

====
