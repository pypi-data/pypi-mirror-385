"""
Environment Constants. (Depreciated in favor of manually specifying endpoints))
"""

from enum import Enum


class Chains(Enum):
    """Supported Chains Enum."""

    EVM = "EVM"
    SOLANA = "SOLANA"
    SUI = "SUI"


ENVS = {
    "PRODUCTION": {
        "base_url": "https://app.ithacaprotocol.io/api/v1",
        "ws_url": "wss://app.ithacaprotocol.io/wss",
        "rpc_url": "https://arbitrum.llamarpc.com",
        # "calc_server_url": "https://app.ithacaprotocol.io/api/calc",
        "calc_server_url": "https://app.ithacaprotocol.io/api/calc",
        "subgraph": "https://api.studio.thegraph.com/query/43740/ithaca-arbitrum/v1.1.0",  # type: ignore  # noqa: E501
    },
    "SOLANA_PRODUCTION": {
        "base_url": "https://solapp.ithacaprotocol.io/api/v1",
        "ws_url": "wss://solapp.ithacaprotocol.io/wss",
        "rpc_url": "https://rpc.ankr.com/solana",
        "calc_server_url": "https://app.canary.ithacanoemon.tech/api/calc",
        "subgraph": None,  # type: ignore  # noqa: E501
    },
    "CANARY": {
        "base_url": "https://app.canary.ithacanoemon.tech/api/v1",
        "ws_url": "wss://app.canary.ithacanoemon.tech/wss",
        "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
        "calc_server_url": "https://app.canary.ithacanoemon.tech/api/calc",
        "subgraph": "https://api.studio.thegraph.com/query/43740/ithaca-arb-sepolia-canary/v1.1.0",
    },
    "SOLANA_CANARY": {
        "base_url": "https://solana.canary.ithacanoemon.tech/api/v1",
        "ws_url": "wss://solana.canary.ithacanoemon.tech/wss",
        "rpc_url": "https://api.devnet.solana.com",
        "calc_server_url": "https://app.canary.ithacanoemon.tech/api/calc",
        "subgraph": None,
    },
    "UAT": {
        "base_url": "https://testnet.ithacaprotocol.io/api/v1",
        "ws_url": "wss://testnet.ithacaprotocol.io/wss",
        "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
        "subgraph": "https://api.studio.thegraph.com/query/43740/ithaca-subgraph/v1.1.2",  # type: ignore  # noqa: E501
    },
    "SEPOLIA": {
        "base_url": "https://sepolia.canary.ithacanoemon.tech/api/v1",
        "ws_url": "wss://sepolia.canary.ithacanoemon.tech/wss",
        "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
        "subgraph": "https://api.studio.thegraph.com/query/43740/ithaca-arb-sepolia/v0.0.1",  # type: ignore  # noqa: E501
    },
    "MUMBAI": {
        "base_url": "https://mumbai.canary.ithacanoemon.tech/api/v1",
        "ws_url": "wss://mumbai.canary.ithacanoemon.tech/wss",
        "rpc_url": "https://polygon-mumbai.blockpi.network/v1/rpc/public",
        "subgraph": "https://api.studio.thegraph.com/query/43740/ithaca-mumbai/v1.0.1",  # type: ignore  # noqa: E501
    },
    "LOCAL": {
        "base_url": "https://localhost:8078/api/v1",
        "ws_url": "wss://localhost:8079",
        "rpc_url": "http://localhost:8545",
        "subgraph": None,
    },
}
