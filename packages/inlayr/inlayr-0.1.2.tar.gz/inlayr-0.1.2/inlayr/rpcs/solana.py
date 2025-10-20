"""
Implementation of solana chain connector.

Dependencies
------------
* `solana` (RPC client + transaction objects)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

from solana.rpc.api import Client

class RPC:
    def __init__(self, chain_id: int | None, headers: dict = {}):
        self.name = "Solana"

        self.rpc_url = "https://api.mainnet-beta.solana.com"
        self.chain_id = chain_id

        self.client = Client(self.rpc_url)
        self.headers = headers
