import types, sys
import importlib
import builtins

from inlayr.provider.registry import get_provider

class Chain: 
    name = "testchain"

    def get_balance(self, address, rpc): return 42
    def get_approval(self, **kwargs): return {"approval": True}
    def get_quote(self, **kwargs): return {"route": [1,2,3]}
    def get_swap(self, **kwargs): return {"tx": "0xdead"}
    def execute_trx(self, trx): return {"hash": "0x01"}
    def trx_status(self, txid): return {"confirmed": True}

class RPC:
    name = "testrpc"

class Aggregator:
    name = "testagg"

def test_registry_get_provider():
    chains_mod = sys.modules.setdefault(f"inlayr.chains", types.ModuleType(f"inlayr.chains"))
    testchain = types.ModuleType(f"inlayr.chains.testchain")
    testchain.Chain = Chain
    sys.modules[f"inlayr.chains.testchain"] = testchain

    rpcs_mod = sys.modules.setdefault(f"inlayr.rpcs", types.ModuleType(f"inlayr.rpcs"))
    testrpc = types.ModuleType(f"inlayr.rpcs.testrpc")
    testrpc.RPC = RPC
    sys.modules[f"inlayr.rpcs.testrpc"] = testrpc

    aggs_mod = sys.modules.setdefault(f"inlayr.aggregators", types.ModuleType(f"inlayr.aggregators"))
    testagg = types.ModuleType(f"inlayr.aggregators.testagg")
    testagg.Aggregator = Aggregator
    sys.modules[f"inlayr.aggregators.testagg"] = testagg
    
    provider = get_provider(chain="testchain", rpc="testrpc", aggregator="testagg")

    assert provider.chain.name == "testchain"
    assert provider.rpc.name == "testrpc"
    assert provider.aggregator.name == "testagg"
