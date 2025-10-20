"""
Implementation of EVM provider.

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

class Chain:
    def __init__(self, wallet_pk: str):
        self.name = "EVM"

        self.wallet = Account.from_key(wallet_pk)

        self.ABI: list[dict] = [      
            {
                "constant": True,
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [{"name": "spender", "type": "address"}, {"name": "value", "type": "uint256"}],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]

    def get_balance(self, **kwargs):
        client = kwargs.get("rpc").client

        token_address = Web3.to_checksum_address(kwargs.get("source_token"))
        erc20 = client.eth.contract(address = token_address, abi = self.ABI)

        amount_func = erc20.functions.balanceOf(self.wallet.address)

        return amount_func.call()

    def get_approval(self, **kwargs):
        client = kwargs.get("rpc").client
        chain_id = kwargs.get("rpc").chain_id
        token = kwargs.get("source_token")
        spender = kwargs.get("aggregator").spender

        token_address = Web3.to_checksum_address(token)
        spender_address = Web3.to_checksum_address(spender)

        erc20 = client.eth.contract(address = token_address, abi = self.ABI)

        allowance = erc20.functions.allowance(self.wallet.address, spender_address)
        allowance_amount = allowance.call()

        transaction = None
        if (allowance_amount < kwargs.get("source_amount")):
            approval = erc20.functions.approve(spender_address, (1<<256)-1)

            gas = approval.estimate_gas({"from": self.wallet.address})
            gas_price = client.eth.gas_price
            max_priority_fee = client.eth.max_priority_fee

            params = {
                "chainId": chain_id,
                "from": self.wallet.address,
                "maxPriorityFeePerGas": int(1.0 * max_priority_fee),
                "maxFeePerGas": int(2.0 * gas_price),
                "gas": int(1.25 * gas),
                "nonce": client.eth.get_transaction_count(self.wallet.address),
            }

            transaction = approval.build_transaction(params)
        else:
            print ("Allowance is sufficient, no approval needed.")

        return transaction

    def execute_trx(self, **kwargs):
        transaction = kwargs.get("transaction").transaction
        client = kwargs.get("rpc").client

        trx_signed = self.wallet.sign_transaction(transaction)
        trx_hash = client.eth.send_raw_transaction(trx_signed.raw_transaction)
        trx_executed = client.to_hex(trx_hash)        

        return trx_executed

    def trx_status(self, **kwargs):
        signature = kwargs.get("signature").signature
        client = kwargs.get("rpc").client

        receipt = client.eth.get_transaction_receipt(signature)

        return receipt
