datatype Token = Digit(n: nat) | Dash | Other

predicate IsDigit(t: Token) {
  t.Digit?
}

predicate IsSimpleId(ts: seq<Token>) {
  |ts| == 3 && IsDigit(ts[0]) && ts[1] == Dash && IsDigit(ts[2])
}

function AcceptsSimpleId(ts: seq<Token>): bool {
  IsSimpleId(ts)
}

lemma ValidSimpleIdAccepted(a: nat, b: nat)
  ensures AcceptsSimpleId([Digit(a), Dash, Digit(b)])
{
}

lemma WrongLengthRejected(ts: seq<Token>)
  requires |ts| != 3
  ensures !AcceptsSimpleId(ts)
{
}
