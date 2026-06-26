datatype OrderState = Created | Paid | Cancelled | Shipped | Refunded

predicate CanShip(s: OrderState) {
  s == Paid
}

predicate CanRefund(s: OrderState) {
  s == Paid || s == Shipped
}

function Ship(s: OrderState): OrderState
  requires CanShip(s)
{
  Shipped
}

function Refund(s: OrderState): OrderState
  requires CanRefund(s)
{
  Refunded
}

lemma CancelledCannotShip()
  ensures !CanShip(Cancelled)
{
}

lemma CreatedCannotShip()
  ensures !CanShip(Created)
{
}

lemma RefundedIsTerminal()
  ensures !CanShip(Refunded)
  ensures !CanRefund(Refunded)
{
}
