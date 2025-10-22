"""
Implementation of 1inch connector.

Dependencies
------------
* `requests` (HTTP calls to provider)
* `web3` (interaction with chains)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

import requests, json
from web3 import Web3, HTTPProvider

class Aggregator:
    def __init__(self, headers: dict = {}):
        self.name = "1inch"

        self.quote_api = "https://api.1inch.dev/swap/v6.1/{chain}/swap"
        self.swap_api = None

        self.spender = "0x111111125421cA6dC452d289314280a0f8842a65"

        self.session = requests.Session()
        self.headers = headers

    def get_quote(self, **kwargs):
        wallet = kwargs.get("chain").wallet        
        chain_id = kwargs.get("rpc").chain_id

        receiver = kwargs.get("receiver") if ("receiver" in kwargs) else wallet.address

        params = {
            "disableEstimate": False,
            "src": kwargs.get("source_token"),
            "dst": kwargs.get("destination_token"),
            "amount": kwargs.get("source_amount"),
            "fromAddress": wallet.address,
            "receiver": receiver,
        }

        if ("slippage" in kwargs):
            params["slippage"] = kwargs.get("slippage") / 100

        url = self.quote_api.format(chain = chain_id)
        response = self.session.get(url, params = params, headers = self.headers)

        return response.json()

    def get_swap(self, **kwargs):
        quote = kwargs.get("quote").quote
        wallet = kwargs.get("chain").wallet
        client = kwargs.get("rpc").client
        chain_id = kwargs.get("rpc").chain_id

        params = {
            "chainId": chain_id,
            "to": Web3.to_checksum_address(quote["tx"]["to"]),
            "data": quote["tx"]["data"],
            "value": int(quote["tx"]["value"]),
            "gas": int(quote["tx"]["gas"]),
            "nonce": int(client.eth.get_transaction_count(wallet.address)),
        }

        if ("maxFeePerGas" in quote["tx"]) and ("maxPriorityFeePerGas" in quote["tx"]):
            params["type"] = 2
            params["maxFeePerGas"] = int(quote["tx"]["maxFeePerGas"])
            params["maxPriorityFeePerGas"] = int(quote["tx"]["maxPriorityFeePerGas"])
        else:
            params["gasPrice"] = int(quote["tx"]["gasPrice"])

        if ("accessList" in quote["tx"]):
            params["accessList"] = quote["tx"]["accessList"]
        
        return params
