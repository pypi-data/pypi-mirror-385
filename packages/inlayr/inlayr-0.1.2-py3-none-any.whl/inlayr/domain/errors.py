"""
Error hierarchy used throughout the module.
"""

from __future__ import annotations

class QuoteError(Exception):
    """
    Raised when obtaining a quote fails.
    """

class TransactionError(Exception):
    """
    Raised when building a transaction fails.
    """

class SignatureError(Exception):
    """
    Raised when signing a transaction fails.
    """

class StatusError(Exception):
    """
    Raised when cannot retrieve a block confirmation.
    """

class BalanceError(Exception):
    """
    Raised when cannot retrieve a token balance.
    """
