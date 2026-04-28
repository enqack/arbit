import json
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from web3 import AsyncWeb3, Web3
from web3.providers import AsyncHTTPProvider

WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
ETH_SENTINEL = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
KYBER_PROXY_ADDRESS = "0x818E6FECD516Ecc3849DAf6845e3EC868087B755"
BANCOR_REGISTRY_ADDRESS = "0x52Ae12ABe5D8BD778BD5397F99cA900624CfADD4"


@dataclass
class ExchangePriceResult:
    exchange: str
    token_out_amount: Decimal
    price_eth_per_token: Decimal
    error: str | None = None


def _load_abi(abi_dir: Path, filename: str) -> list:
    return json.loads((abi_dir / filename).read_text())


async def build_web3(rpc_url: str) -> AsyncWeb3:
    return AsyncWeb3(AsyncHTTPProvider(rpc_url))


async def build_contracts(w3: AsyncWeb3, abi_dir: Path) -> dict:
    uniswap_router = w3.eth.contract(
        address=Web3.to_checksum_address(UNISWAP_V2_ROUTER_ADDRESS),
        abi=_load_abi(abi_dir, "uniswap_v2_router.json"),
    )
    kyber = w3.eth.contract(
        address=Web3.to_checksum_address(KYBER_PROXY_ADDRESS),
        abi=_load_abi(abi_dir, "kyber_network_proxy.json"),
    )
    registry = w3.eth.contract(
        address=Web3.to_checksum_address(BANCOR_REGISTRY_ADDRESS),
        abi=_load_abi(abi_dir, "bancor_registry.json"),
    )
    bancor_address = await registry.functions.addressOf(
        Web3.to_hex(text="BancorNetwork")
    ).call()
    bancor = w3.eth.contract(
        address=bancor_address,
        abi=_load_abi(abi_dir, "bancor_network.json"),
    )
    return {
        "uniswap_router": uniswap_router,
        "kyber": kyber,
        "bancor": bancor,
    }


async def get_uniswap_v2_price(
    contracts: dict,
    token_address: str,
    token_decimals: int,
    amount_in_wei: int,
    eth_input_amount: Decimal,
) -> ExchangePriceResult:
    try:
        amounts = await contracts["uniswap_router"].functions.getAmountsOut(
            amount_in_wei,
            [
                Web3.to_checksum_address(WETH_ADDRESS),
                Web3.to_checksum_address(token_address),
            ],
        ).call()
        token_out = Decimal(amounts[-1]) / Decimal(10**token_decimals)
        price = eth_input_amount / token_out
        return ExchangePriceResult("Uniswap V2", token_out, price)
    except Exception as exc:
        return ExchangePriceResult("Uniswap V2", Decimal(0), Decimal(0), error=str(exc))


async def get_kyber_price(
    contracts: dict,
    token_address: str,
    token_decimals: int,
    amount_in_wei: int,
    eth_input_amount: Decimal,
) -> ExchangePriceResult:
    try:
        expected_rate, _ = await contracts["kyber"].functions.getExpectedRate(
            Web3.to_checksum_address(ETH_SENTINEL),
            Web3.to_checksum_address(token_address),
            amount_in_wei,
        ).call()
        token_out = (Decimal(expected_rate) / Decimal(10**18)) * eth_input_amount
        price = eth_input_amount / token_out
        return ExchangePriceResult("Kyber", token_out, price)
    except Exception as exc:
        return ExchangePriceResult("Kyber", Decimal(0), Decimal(0), error=str(exc))


async def get_bancor_price(
    contracts: dict,
    token_address: str,
    token_decimals: int,
    amount_in_wei: int,
    eth_input_amount: Decimal,
) -> ExchangePriceResult:
    try:
        path = await contracts["bancor"].functions.conversionPath(
            Web3.to_checksum_address(ETH_SENTINEL),
            Web3.to_checksum_address(token_address),
        ).call()
        out_wei = await contracts["bancor"].functions.rateByPath(
            path, amount_in_wei
        ).call()
        token_out = Decimal(out_wei) / Decimal(10**token_decimals)
        price = eth_input_amount / token_out
        return ExchangePriceResult("Bancor", token_out, price)
    except Exception as exc:
        return ExchangePriceResult("Bancor", Decimal(0), Decimal(0), error=str(exc))
