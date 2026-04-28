import asyncio
import json
import logging
from decimal import Decimal

from rich.console import Console
from rich.table import Table
from rich.text import Text
from web3 import Web3

from arbit.config import Config
from arbit.exchanges import (
    ExchangePriceResult,
    build_contracts,
    build_web3,
    get_bancor_price,
    get_kyber_price,
    get_uniswap_v2_price,
)


def compute_spread(
    results: list[ExchangePriceResult],
) -> tuple[str, str, Decimal] | None:
    valid = [r for r in results if r.error is None and r.token_out_amount > 0]
    if len(valid) < 2:
        return None
    best_buy = min(valid, key=lambda r: r.price_eth_per_token)
    best_sell = max(valid, key=lambda r: r.price_eth_per_token)
    spread = (
        (best_sell.price_eth_per_token - best_buy.price_eth_per_token)
        / best_buy.price_eth_per_token
        * Decimal(100)
    )
    return best_buy.exchange, best_sell.exchange, spread


def render_table(
    console: Console,
    tokens: list[dict],
    token_results: list[list[ExchangePriceResult]],
    block: int,
    gas_gwei: Decimal,
    balance_eth: Decimal,
) -> None:
    console.print(
        Text(
            f"Block {block}  |  Gas {gas_gwei:.2f} Gwei  |  Balance {balance_eth:.6f} ETH",
            style="bold cyan",
        )
    )

    table = Table(show_header=True, header_style="bold white")
    table.add_column("Token", style="bold")
    table.add_column("Uniswap V2", justify="right")
    table.add_column("Kyber", justify="right")
    table.add_column("Bancor", justify="right")
    table.add_column("Best Buy", justify="center")
    table.add_column("Best Sell", justify="center")
    table.add_column("Spread %", justify="right")

    exchange_order = ["Uniswap V2", "Kyber", "Bancor"]

    for token, results in zip(tokens, token_results):
        by_name = {r.exchange: r for r in results}

        def fmt_price(name: str) -> str:
            r = by_name.get(name)
            if r is None or r.error is not None or r.token_out_amount == 0:
                return "[dim]N/A[/dim]"
            return f"{r.price_eth_per_token:.6f}"

        spread_data = compute_spread(results)
        if spread_data is None:
            best_buy_str = "[dim]N/A[/dim]"
            best_sell_str = "[dim]N/A[/dim]"
            spread_str = "[dim]N/A[/dim]"
        else:
            best_buy, best_sell, spread = spread_data
            best_buy_str = f"[green]{best_buy}[/green]"
            best_sell_str = f"[green]{best_sell}[/green]"
            if spread > 0:
                spread_str = f"[green]{spread:.2f}%[/green]"
            else:
                spread_str = f"[dim]{spread:.2f}%[/dim]"

        table.add_row(
            token["symbol"],
            fmt_price("Uniswap V2"),
            fmt_price("Kyber"),
            fmt_price("Bancor"),
            best_buy_str,
            best_sell_str,
            spread_str,
        )

    console.print(table)
    console.print()


async def check_token(
    contracts: dict,
    token: dict,
    config: Config,
    logger: logging.Logger,
) -> list[ExchangePriceResult]:
    amount_in_wei = int(config.eth_input_amount * Decimal(10**18))
    results = await asyncio.gather(
        get_uniswap_v2_price(contracts, token["address"], token["decimals"], amount_in_wei, config.eth_input_amount),
        get_kyber_price(contracts, token["address"], token["decimals"], amount_in_wei, config.eth_input_amount),
        get_bancor_price(contracts, token["address"], token["decimals"], amount_in_wei, config.eth_input_amount),
    )
    for r in results:
        if r.error:
            logger.debug("%s error for %s: %s", r.exchange, token["symbol"], r.error)
    return list(results)


async def run_monitor(config: Config, logger: logging.Logger) -> None:
    w3 = await build_web3(config.rpc_url)
    contracts = await build_contracts(w3, config.abi_dir)
    tokens: list[dict] = json.loads(config.tokens_file.read_text())["tokens"]
    console = Console()

    logger.info(
        "Monitoring %d token(s) across Uniswap V2, Kyber, Bancor every %ds",
        len(tokens),
        config.polling_interval,
    )

    while True:
        try:
            block, gas_wei, balance_wei = await asyncio.gather(
                w3.eth.block_number,
                w3.eth.gas_price,
                w3.eth.get_balance(Web3.to_checksum_address(config.eth_wallet_address)),
            )
            token_results = await asyncio.gather(
                *[check_token(contracts, t, config, logger) for t in tokens]
            )
            render_table(
                console,
                tokens,
                list(token_results),
                block,
                Web3.from_wei(gas_wei, "gwei"),
                Web3.from_wei(balance_wei, "ether"),
            )
        except Exception as exc:
            logger.exception("Poll cycle failed: %s", exc)

        await asyncio.sleep(config.polling_interval)
