"""
Implementation of raydium connector.

Dependencies
------------
* `requests` (HTTP calls to provider)
* `solana` (RPC client + transaction objects)
* `solders` (Public key management)
* `spl` (Associated token address)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

from spl.token.instructions import get_associated_token_address

import base58, base64

from solana.rpc.api import VersionedTransaction
from solders.pubkey import Pubkey

import requests, json

class Aggregator:
    def __init__(self, headers: dict = {}):
        self.name = "Raydium"

        self.quote_api = "https://transaction-v1.raydium.io/compute/swap-base-in"
        self.swap_api = "https://transaction-v1.raydium.io/transaction/swap-base-in"
        self.fee_api = "https://api-v3.raydium.io/main/auto-fee"

        self.session = requests.Session()
        self.headers = headers

    def get_quote(self, **kwargs):
        params = {
            "txVersion": "V0",
            "inputMint": kwargs.get("source_token"),
            "outputMint": kwargs.get("destination_token"),
            "amount": kwargs.get("source_amount"),
        }
        
        if ("slippage" in kwargs):
            params["slippageBps"] = kwargs.get("slippage")

        response = self.session.get(self.quote_api, params=params, headers=self.headers)
        
        return response.json()

    def get_swap(self, **kwargs):
        quote = kwargs.get("quote").quote
        wallet = kwargs.get("chain").wallet

        response = self.session.get(self.fee_api, headers=self.headers)
        fee_data = response.json()

        fees = fee_data["data"]["default"][kwargs.get("priority_fee")]

        receiver = Pubkey.from_string(kwargs.get("receiver")) if ("receiver" in kwargs) else wallet.pubkey()

        params = json.dumps({
            "txVersion": "V0",
            "wallet": str(wallet.pubkey()),
            "swapResponse": quote,     
            "inputAccount": str(get_associated_token_address(wallet.pubkey(), Pubkey.from_string(quote["data"]["inputMint"]))),
            "outputAccount": str(get_associated_token_address(receiver, Pubkey.from_string(quote["data"]["outputMint"]))),
            "computeUnitPriceMicroLamports": str(fees)
        })

        response = self.session.post(self.swap_api, data=params, headers={"Content-Type": "application/json", **self.headers})
        response_data = response.json()

        trx_list = []
        for record in response_data["data"]:
            trx_decoded = base64.b64decode(record['transaction'])
            trx_versioned = VersionedTransaction.from_bytes(trx_decoded)
            trx_signed = VersionedTransaction(trx_versioned.message, [wallet])

            trx_list.append(trx_signed)
            
        return trx_list
