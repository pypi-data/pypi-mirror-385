"""
Implementation of 0x connector.

Dependencies
------------
* `requests` (HTTP calls to provider)
* `web3` (interaction with chains)
* `eth_account` (managing private keys)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

import requests, json
from web3 import Web3, HTTPProvider

from eth_account import Account
from eth_keys import keys

class Aggregator:
    def __init__(self, headers: dict = {}):
        self.name = "0x"

        self.quote_api = "https://api.0x.org/swap/permit2/quote"
        self.swap_api = None

        self.spender = "0x000000000022D473030F116dDEE9F6B43aC78BA3"

        self.session = requests.Session()
        self.headers = headers

    def get_quote(self, **kwargs):
        wallet = kwargs.get("chain").wallet
        chain_id = kwargs.get("rpc").chain_id

        params = {
            "chainId": chain_id,
            "taker": wallet.address,
            "sellToken": kwargs.get("source_token"),
            "buyToken": kwargs.get("destination_token"),
            "sellAmount": kwargs.get("source_amount"),
        }

        if ("slippage" in kwargs):
            params["slippageBps"] = kwargs.get("slippage")

        response = self.session.get(self.quote_api, params = params, headers = self.headers)
        
        return response.json()

    def get_swap(self, **kwargs):
        quote = kwargs.get("quote").quote
        wallet = kwargs.get("chain").wallet
        client = kwargs.get("rpc").client
        chain_id = kwargs.get("rpc").chain_id

        digest = Web3.to_bytes(hexstr = quote["permit2"]["hash"])
        priv = keys.PrivateKey(wallet.key)
        sig = priv.sign_msg_hash(digest)

        r, s, v = sig.r, sig.s, sig.v
        if v in (0, 1):
            v += 27

        signature = r.to_bytes(32, "big") + s.to_bytes(32, "big") + v.to_bytes(1, "big")

        params = {
            "chainId": chain_id, 
            "to": Web3.to_checksum_address(quote["transaction"]["to"]),
            "data": quote["transaction"]["data"] + len(signature).to_bytes(32, "big").hex() + signature.hex(),
            "value": int(quote["transaction"]["value"]),
            "gas": int(quote["transaction"]["gas"]),
            "nonce": int(client.eth.get_transaction_count(wallet.address)),
        }

        if ("maxFeePerGas" in quote["transaction"]) and ("maxPriorityFeePerGas" in quote["transaction"]):
            params["type"] = 2
            params["maxFeePerGas"] = int(quote["transaction"]["maxFeePerGas"])
            params["maxPriorityFeePerGas"] = int(quote["transaction"]["maxPriorityFeePerGas"])
        else:
            params["gasPrice"] = int(quote["transaction"]["gasPrice"])

        if ("accessList" in quote["transaction"]):
            params["accessList"] = quote["transaction"]["accessList"]
        
        return params
