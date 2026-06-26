function SumPrefix(xs: seq<int>, n: nat): int
  requires n <= |xs|
  decreases n
{
  if n == 0 then 0 else SumPrefix(xs, n - 1) + xs[n - 1]
}

function SumSpec(xs: seq<int>): int {
  SumPrefix(xs, |xs|)
}

method Sum(xs: seq<int>) returns (s: int)
  ensures s == SumSpec(xs)
{
  s := 0;
  var i: nat := 0;
  while i < |xs|
    invariant i <= |xs|
    invariant s == SumPrefix(xs, i)
  {
    s := s + xs[i];
    i := i + 1;
  }
}
