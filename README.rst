Arbit
=====

An Ethereum blockchain arbitrage bot

**Alpha stage software**


Quickstart
----------

.. code:: sh

    git clone git@github.com:enqack/arbit.git
    cd arbit

Ubuntu prerequisites
^^^^^^^^^^^^^^^^^^^^

.. code:: sh

    sudo apt install python3.7-minimal python3.7-venv python3.7-dev python3-pip


Infura
^^^^^^

In order to interact with the Ethereum blockchain a node provider, like `Infura <https://infura.io/>`_, is required.


Environment setup
^^^^^^^^^^^^^^^^^

Configure a python virtual environment for the bot as follows.

.. code:: sh

    python3.7 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt

Set environment variables by first copying the example file.

.. code:: sh

    cp example.env .env

Then edit `.env` as required.

.. code:: sh

    ARBIT_RPC_URL="https://mainnet.infura.io/v3/<INFURA_API_KEY>"
    ARBIT_ETH_WALLET_ADDRESS="0x0000"
    ARBIT_ETH_INPUT_AMOUNT="0.1"
    ARBIT_POLLING_INTERVAL="5"
    ARBIT_LOGLEVEL="INFO"

`ARBIT_RPC_URL` is the URL of an Ethereum node.

`ARBIT_ETH_WALLET_ADDRESS` is the address of an Ethereum wallet to used for transactions.

`ARBIT_ETH_INPUT_AMOUNT` is the amount of Ether to use for token purchases.

`ARBIT_POLLING_INTERVAL` is the time, in seconds, between pricing and trade runs.

`ARBIT_LOGLEVEL` is the level of logging to use. Applies to both console and the log file.


Run it!
^^^^^^^

To run arbit as described below ensure you are in the root directory of the repository.

.. code:: sh

    python arbit/arbit.py
