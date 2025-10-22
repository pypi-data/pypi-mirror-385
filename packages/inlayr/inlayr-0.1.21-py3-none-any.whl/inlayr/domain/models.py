"""
Dataclass models shared across providers.
Models are *frozen* so they are hashable and safe to cache.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from typing import Any, Mapping

@dataclass(slots=True, frozen=True)
class Quote:
    """
    Wrapper around a chain‑specific quote.
    """    
    source: str
    quote: Any

@dataclass(slots=True, frozen=True)
class Transaction:
    """
    Wrapper around a chain‑specific transaction.
    """
    source: str    
    transaction: Any

@dataclass(slots=True, frozen=True)
class Signature:
    """
    Wrapper around a chain‑specific block signature.
    """
    source: str    
    signature: Any

@dataclass(slots=True, frozen=True)
class Status:
    """
    Wrapper around a chain‑specific block status.
    """    
    source: str    
    status: Any

@dataclass(slots=True, frozen=True)
class Balance:
    """
    Wrapper around a chain‑specific token balance.
    """    
    source: str    
    amount: Decimal
