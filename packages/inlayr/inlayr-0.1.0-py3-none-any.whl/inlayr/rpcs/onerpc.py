"""
Implementation of 1rpc connector.

Dependencies
------------
* `web3` (interaction with chains)
"""

from __future__ import annotations

from ..utils.constants import ConstDict

import requests, json
from web3 import Web3, HTTPProvider

class RPC:
    def __init__(self, chain_id: int | None, headers: dict = {}):
        self.name = "1rpc"

        self.chain_dict = {
            1: "eth",
            17000: "holesky",
            11155111: "sepolia",
            560048: "hoodi",
            56: "bnb",
            137: "matic",
            1101: "polygon/zkevm",
            43114: "avax/c",
            42161: "arb",
            1284: "glmr",
            592: "astr",
            10: "op",
            324: "zksync2-era",
            250: "ftm",
            42220: "celo",
            8217: "klay",
            9997: "alt-testnet",
            1313161554: "aurora",
            8453: "base",
            1666600000: "one",
            59144: "linea",
            42262: "oasis/emerald",
            23294: "oasis/sapphire",
            534352: "scroll",
            1398243: "ata/testnet",
            100: "gnosis",
            66: "oktc",
            5000: "mantle",
            25: "cro",
            204: "opbnb",
            169: "manta",
            1116: "core",
            40: "telos/evm",
            288: "boba/eth",
            34443: "mode",
            7332: "horizen-eon",
            999: "hyperliquid",
            130: "unichain",
        }

        self.rpc_url = f"https://1rpc.io/{self.chain_dict[chain_id]}"
        self.chain_id = chain_id

        self.client = Web3(HTTPProvider(self.rpc_url))
        self.headers = headers
