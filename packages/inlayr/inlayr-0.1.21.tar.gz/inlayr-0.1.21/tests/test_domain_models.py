from decimal import Decimal
from frozendict import frozendict

from inlayr.domain.models import Quote, Transaction, Signature, Status, Balance

def test_quote_hashable_and_attrs():
    q1 = Quote(source="test", quote=frozendict({"path": ("A", "B")}))
    q2 = Quote(source="test", quote=frozendict({"path": ("A", "B")}))

    assert q1 == q2

def test_transaction_signature_status_balance():
    trx = Transaction(source="test", transaction=frozendict({"to": "0xabc"}))
    sig = Signature(source="test", signature=b"\x01\x02")
    stat = Status(source="test", status=frozendict({"confirmed": True}))
    bal = Balance(source="test", amount=Decimal("1.2345"))

    assert trx.source == "test" and "to" in trx.transaction
    assert sig.signature.startswith(b"\x01")
    assert stat.status["confirmed"] is True
    assert bal.amount == Decimal("1.2345")
