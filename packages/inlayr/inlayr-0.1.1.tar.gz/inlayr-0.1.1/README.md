# inlayr

_A modular, chain‑agnostic SDK for building and integrating crypto quoting and trading flows on DEXs._

> **Status:** Experimental (v0.1.1). APIs may change before 1.0.

[![PyPI](https://img.shields.io/pypi/v/inlayr.svg)](https://pypi.org/project/inlayr/)
[![Python](https://img.shields.io/pypi/pyversions/inlayr.svg)](https://pypi.org/project/inlayr/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![Typing](https://img.shields.io/badge/typing-PEP%20661%20%7C%20py.typed-success)](#type-hints)

---

inlayr aims to provide a clean, typed interface for **quoting, routing and submitting swaps** across multiple chains.

- ✅ **Pluggable backends** — add providers without touching the core
- ✅ **No commission** — avoid wallet-level commissions
- ✅ **Integration** — build your own DEX trading bots

If you just want the docs: jump to **[Quickstart](#quickstart)** or **[Installation](#installation)**.

---

## Installation

The base install:

```bash
pip install inlayr
```

Supported Python: **3.9+**

## Quickstart

> The exact API surface may evolve before 1.0. The snippets below show the intended usage patterns while staying dependency‑light.

### Verify install

```python
import inlayr
print (inlayr.__version__)
```

### High‑level sketch (pseudocode)

```python
# Illustrative only. Actual class and method names may differ in your version.

# 1) Import provider interface
from inlayr.provider import get_provider

# 2) Fetch your private key
solana_pk = open(r"solana_pk").read()

# 3) Configure Chain, RPC, and Aggregator
provider = get_provider(
	chain = "solana",
	chain_params = {"wallet_pk": solana_pk},
	rpc = "solana",
	rpc_params = {"chain_id": None},
	aggregator = "jupiter",
	aggregator_params = {}
)

# 4) Perform operations (e.g. request a quote)
quote = provider.get_quote(
	source_token = "4eDf52YYzL6i6gbZ6FXqrLUPXbtP61f1gPSFM66M4XHe",
	source_amount = 1_000_000_000,
	destination_token = "So11111111111111111111111111111111111111112",
	slippage = 1000
)
```

Please refer to [examples](https://github.com/OlegMitsik/inlayr/tree/main/examples) for more functional use cases.

## Configuration

Common runtime knobs (RPC endpoints, routing preferences, etc) are typically supplied by you at construction time.

Currently supported configurations:
- **RPCs** — ankr, 1rpc, solana
- **Chains** — evm, solana
- **Aggregators** — 0x, 1inch, jupiter, raydium

## Type hints

- The package includes `py.typed` so type checkers (mypy, pyright) understand the public API.
- We aim to keep public call signatures stable across minor versions; experimental pieces will be marked in docstrings where applicable.

## Contributing

PRs and issues are welcome! A few guidelines:
- Discuss larger changes in an issue first.
- Ensure `python -m build && twine check dist/*` succeeds.
- Add or update tests (`pytest`).

To run tests:

```bash
pip install -e '.[test]'
pytest -q
```

## Versioning

We use **Semantic Versioning**. Until `1.0.0`, minor bumps may include small breaking changes as we refine the API.

## License

Licensed under the **Apache 2.0** license. See [LICENSE](https://github.com/OlegMitsik/inlayr/blob/main/LICENSE) for details.

## Links

- PyPI: <https://pypi.org/project/inlayr/>
- Issues: <https://github.com/OlegMitsik/inlayr/issues>
- Repo: <https://github.com/OlegMitsik/inlayr>
