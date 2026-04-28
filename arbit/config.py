from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import os

from dotenv import load_dotenv


def _strtobool(value: str) -> bool:
    if value.lower() in ("1", "true", "yes", "on"):
        return True
    if value.lower() in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"Cannot parse boolean from: {value!r}")


@dataclass(frozen=True)
class Config:
    rpc_url: str
    eth_wallet_address: str
    eth_input_amount: Decimal
    polling_interval: int
    trading_enabled: bool
    log_level: str
    log_file: str
    tokens_file: Path
    abi_dir: Path


def load_config() -> Config:
    load_dotenv(verbose=True)

    rpc_url = os.environ.get("ARBIT_RPC_URL")
    if not rpc_url:
        raise RuntimeError("ARBIT_RPC_URL is required")

    wallet = os.environ.get("ARBIT_ETH_WALLET_ADDRESS")
    if not wallet:
        raise RuntimeError("ARBIT_ETH_WALLET_ADDRESS is required")

    base = Path(__file__).parent.parent

    return Config(
        rpc_url=rpc_url,
        eth_wallet_address=wallet,
        eth_input_amount=Decimal(os.environ.get("ARBIT_ETH_INPUT_AMOUNT", "1")),
        polling_interval=int(os.environ.get("ARBIT_POLLING_INTERVAL", "5")),
        trading_enabled=_strtobool(os.environ.get("ARBIT_TRADING_ENABLED", "0")),
        log_level=os.environ.get("ARBIT_LOGLEVEL", "INFO"),
        log_file=os.environ.get("ARBIT_LOGFILE", "data/arbit.log"),
        tokens_file=base / "data" / "tokens.json",
        abi_dir=base / "data" / "abi",
    )
