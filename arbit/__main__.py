import asyncio
import signal
import sys

from arbit.config import load_config
from arbit.log import setup_logger
from arbit.monitor import run_monitor

ARBIT_VERSION = "0.1.0"


def main() -> None:
    config = load_config()
    logger = setup_logger(config)
    logger.info("Starting Arbit %s", ARBIT_VERSION)
    try:
        asyncio.run(run_monitor(config, logger))
    except KeyboardInterrupt:
        logger.info("Stopping Arbit")
        sys.exit(128 + signal.SIGINT)


if __name__ == "__main__":
    main()
