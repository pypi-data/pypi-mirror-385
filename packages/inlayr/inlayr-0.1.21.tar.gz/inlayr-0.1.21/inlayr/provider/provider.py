"""
Provider class implementation that wires Chain + RPC + Aggregator.

* `get_balance` – fetches total token balance on the wallet for a given address.
* `get_approval` – sets max allowance amount for trading specified token through permit2.
* `get_quote` – asks aggregator for the best swap route from *source_token* to *destination_token*.
* `get_swap` – creates a swap transaction on the wallet.
* `execute_trx` – broadcasts transaction via RPC endpoint.
* `trx_status` – checks status of a given transaction.
"""

from __future__ import annotations

from ..domain.models import Balance, Quote, Transaction, Signature, Status
from ..domain.errors import BalanceError, QuoteError, TransactionError, SignatureError, StatusError

class Provider:
    def __init__(self, *, chain, rpc, aggregator) -> None:
        self.chain = chain
        self.rpc = rpc
        self.aggregator = aggregator

    # Chain methods
    def get_balance(self, source_token: str, **kwargs) -> Balance:
        """
        Retrieve current holdings of the token.
        """
        try:
            return Balance(
                source = self.chain.name,     
                amount = self.chain.get_balance(
                    source_token = source_token,
                    aggregator = self.aggregator,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise BalanceError(f"Could not retrieve token balance: {e}") from e        

    def get_approval(self, source_token: str, source_amount: int, **kwargs) -> Transaction:
        """
        Approve allowance for trading specified token.
        """
        try:
            return Transaction(
                source = self.chain.name,
                transaction = self.chain.get_approval(
                    source_token = source_token, 
                    source_amount = source_amount,
                    aggregator = self.aggregator,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise TransactionError(f"Failed to approve allowance: {e}") from e 

    def execute_trx(self, transaction: Transaction , **kwargs) -> Signature:
        """
        Send transaction to the chain.
        """
        try:
            return Signature(
                source = self.chain.name,
                signature = self.chain.execute_trx(
                    transaction = transaction,
                    aggregator = self.aggregator,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise SignatureError(f"Failed to sign transaction: {e}") from e 

    def trx_status(self, signature: Signature, **kwargs) -> Status:
        """
        Check status of a transaction.
        """
        try:
            return Status(
                source = self.chain.name,
                status = self.chain.trx_status(
                    signature = signature,
                    aggregator = self.aggregator,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise StatusError(f"Could not retrieve transaction status: {e}") from e 

    # Aggregator methods
    def get_quote(self, source_token: str, source_amount: int, destination_token: str, **kwargs) -> Quote:
        """
        Fetch the best quote from aggregator to swap tokens.
        """
        try:
            return Quote(
                source = self.aggregator.name,       
                quote = self.aggregator.get_quote(
                    source_token = source_token,
                    source_amount = source_amount,
                    destination_token = destination_token,
                    chain = self.chain,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise QuoteError(f"Could not retrieve token balance: {e}") from e        

    def get_swap(self, quote: Quote, **kwargs) -> Transaction:
        """
        Build and sign a swap transaction based on the selected quote.
        """
        try:
            return Transaction(
                source = self.aggregator.name,
                transaction = self.aggregator.get_swap(
                    quote = quote,
                    chain = self.chain,
                    rpc = self.rpc,
                    **kwargs
                )
            )
        except Exception as e:
            raise TransactionError(f"Unable to build transaction: {e}") from e 
