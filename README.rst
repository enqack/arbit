Arbit
=====

An Ethereum blockchain arbitrage price monitor. Watches token prices across
Uniswap V2, Kyber, and Bancor in real time and displays a live table of
prices, best buy/sell exchange, and spread percentage for each configured token.

**Alpha stage software**


Quickstart
----------

.. code:: sh

    git clone git@github.com:enqack/arbit.git
    cd arbit

Requirements
^^^^^^^^^^^^

Python 3.12 or newer.

Ubuntu prerequisites:

.. code:: sh

    sudo apt install python3.12-minimal python3.12-venv python3.12-dev python3-pip


Infura
^^^^^^

An Ethereum node provider such as `Infura <https://infura.io/>`_ is required
to connect to mainnet.


Environment setup
^^^^^^^^^^^^^^^^^

.. code:: sh

    python3.12 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    cp example.env .env

Edit ``.env`` as required:

.. code:: sh

    ARBIT_RPC_URL="https://mainnet.infura.io/v3/<INFURA_API_KEY>"
    ARBIT_ETH_WALLET_ADDRESS="0x0000"
    ARBIT_ETH_INPUT_AMOUNT="0.1"
    ARBIT_POLLING_INTERVAL="5"
    ARBIT_LOGLEVEL="INFO"
    ARBIT_LOGFILE="data/arbit.log"

``ARBIT_RPC_URL``
    URL of an Ethereum node provider (required).

``ARBIT_ETH_WALLET_ADDRESS``
    Wallet address whose ETH balance is shown in the header (required).

``ARBIT_ETH_INPUT_AMOUNT``
    Amount of ETH used as the notional input for price quotes. Default: ``1``.

``ARBIT_POLLING_INTERVAL``
    Seconds between price checks. Default: ``5``.

``ARBIT_LOGLEVEL``
    Log level for console and file output. Default: ``INFO``.

``ARBIT_LOGFILE``
    Path to the rotating log file. Default: ``data/arbit.log``.


Tokens
^^^^^^

Edit ``data/tokens.json`` to configure which tokens to monitor:

.. code:: json

    {
        "tokens": [
            {"symbol": "DAI", "address": "0x6b175474e89094c44da98b954eedeac495271d0f", "decimals": 18},
            {"symbol": "LINK", "address": "0x514910771af9ca656af840dff83e8264ecf986ca", "decimals": 18}
        ]
    }


Run it!
^^^^^^^

From the root of the repository:

.. code:: sh

    python -m arbit
