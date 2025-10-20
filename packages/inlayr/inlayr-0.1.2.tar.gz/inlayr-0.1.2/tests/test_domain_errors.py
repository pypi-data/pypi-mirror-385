import pytest

from inlayr.domain import errors

def test_custom_errors_exist():
    for name in ("QuoteError","TransactionError","SignatureError","StatusError","BalanceError"):
        assert hasattr(errors, name)

def test_raise_and_catch():
    with pytest.raises(errors.QuoteError):
        raise errors.QuoteError("boom")
