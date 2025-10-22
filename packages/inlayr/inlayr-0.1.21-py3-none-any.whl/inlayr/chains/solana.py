"""
Implementation of Solana provider.

Dependencies
------------
* `solana` (RPC client + transaction objects)
* `solders` (faster message parsing)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

import base58, base64

from solana.rpc.api import types

from solders.pubkey import Pubkey
from solders.keypair import Keypair

class Chain:
    def __init__(self, wallet_pk: str):
        self.name = "Solana"

        pk64 = base58.b58decode(wallet_pk)
        self.wallet = Keypair.from_bytes(pk64)

    def get_balance(self, **kwargs):
        client = kwargs.get("rpc").client

        accounts = client.get_token_accounts_by_owner(
            self.wallet.pubkey(),
            types.TokenAccountOpts(mint = Pubkey.from_string(kwargs.get("source_token")))
        )

        token_Qts = []
        for account in accounts.value:
            account_balance = client.get_token_account_balance(account.pubkey)
            amount = account_balance.value.ui_amount * (10 ** account_balance.value.decimals)

            token_Qts.append(amount)
        
        return sum(token_Qts)

    def get_approval(self, **kwargs):
        print ("No approval needed on Solana.")

        return None

    def execute_trx(self, **kwargs):
        transaction = kwargs.get("transaction").transaction
        client = kwargs.get("rpc").client

        signatures = []
        for trx in transaction:
            trx_executed = client.send_transaction(trx, opts = types.TxOpts(skip_preflight = False, preflight_commitment = "finalized"))
            
            signatures.append(trx_executed.value)
        
        return signatures

    def trx_status(self, **kwargs):
        signature = kwargs.get("signature").signature
        client = kwargs.get("rpc").client

        receipt = client.get_signature_statuses(signature)

        return receipt
